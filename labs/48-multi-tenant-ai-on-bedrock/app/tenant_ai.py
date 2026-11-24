"""Multi-tenant AI building blocks for a pooled SaaS on Amazon Bedrock.

Every AI request is bound to a TenantContext derived from the *verified* JWT, never from the prompt:

* model access goes through the tenant's **application inference profile** → per-tenant cost & quotas
* retrieval uses a **metadata filter** tenantId == ctx.tenant_id → no cross-tenant RAG leakage
* memory uses **namespaces** /tenant/{tenantId}/... → no cross-tenant recall
* a **token budget** (DynamoDB atomic counter with a conditional update) hard-caps spend per tenant/month
* the model is chosen by **tier** (cheaper models for basic, stronger for enterprise)

AWS clients are injected so the logic is unit-testable without AWS.
"""
from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from typing import Any

TIER_DEFAULTS = {
    "basic": {"monthly_tokens": 2_000_000, "max_output_tokens": 800},
    "premium": {"monthly_tokens": 20_000_000, "max_output_tokens": 2_000},
    "enterprise": {"monthly_tokens": 200_000_000, "max_output_tokens": 4_000},
}


class TenantError(PermissionError):
    pass


class BudgetExceeded(RuntimeError):
    pass


@dataclass(frozen=True)
class TenantContext:
    tenant_id: str
    tier: str
    user_id: str

    @classmethod
    def from_claims(cls, claims: dict[str, Any]) -> "TenantContext":
        """Claims must come from a token your authorizer already verified (Cognito / AgentCore Identity)."""
        tenant = claims.get("custom:tenantId")
        tier = claims.get("custom:tier", "basic")
        if not tenant or not str(tenant).startswith("t-"):
            raise TenantError("token has no valid custom:tenantId claim")
        if tier not in TIER_DEFAULTS:
            raise TenantError(f"unknown tier {tier!r}")
        return cls(tenant_id=tenant, tier=tier, user_id=claims.get("sub", "unknown"))


class InferenceProfileResolver:
    """Maps tenant → application inference profile ARN (created by tenantctl.sh / create_tenant_profiles.py)."""

    def __init__(self, bedrock_client, cache_ttl_s: int = 300):
        self._bedrock, self._ttl, self._cache = bedrock_client, cache_ttl_s, {}

    def arn_for(self, ctx: TenantContext) -> str:
        hit = self._cache.get(ctx.tenant_id)
        now = dt.datetime.now().timestamp()
        if hit and hit[1] > now:
            return hit[0]
        name = f"{ctx.tenant_id}-default"
        token = None
        while True:
            page = self._bedrock.list_inference_profiles(typeEquals="APPLICATION", **({"nextToken": token} if token else {}))
            for p in page.get("inferenceProfileSummaries", []):
                if p["inferenceProfileName"] == name:
                    self._cache[ctx.tenant_id] = (p["inferenceProfileArn"], now + self._ttl)
                    return p["inferenceProfileArn"]
            token = page.get("nextToken")
            if not token:
                raise TenantError(f"no inference profile for {ctx.tenant_id}; onboard the tenant first")


def kb_filter(ctx: TenantContext, extra: dict | None = None) -> dict:
    """Bedrock Knowledge Bases retrieval filter that pins results to the caller's tenant."""
    tenant_clause = {"equals": {"key": "tenantId", "value": ctx.tenant_id}}
    return {"andAll": [tenant_clause, extra]} if extra else tenant_clause


def memory_namespace(ctx: TenantContext, kind: str = "facts") -> str:
    """AgentCore Memory namespace scoped by tenant and user."""
    return f"/tenant/{ctx.tenant_id}/user/{ctx.user_id}/{kind}"


class TokenBudget:
    """Monthly per-tenant token budget using an atomic, conditional DynamoDB update (no read-modify-write race)."""

    def __init__(self, dynamodb_client, table: str):
        self._ddb, self._table = dynamodb_client, table

    @staticmethod
    def period() -> str:
        return dt.date.today().strftime("%Y-%m")

    def charge(self, ctx: TenantContext, tokens: int) -> int:
        limit = TIER_DEFAULTS[ctx.tier]["monthly_tokens"]
        try:
            resp = self._ddb.update_item(
                TableName=self._table,
                Key={"pk": {"S": f"BUDGET#{ctx.tenant_id}#{self.period()}"}},
                UpdateExpression="ADD used :t",
                ConditionExpression="attribute_not_exists(used) OR used <= :max",
                ExpressionAttributeValues={":t": {"N": str(tokens)}, ":max": {"N": str(limit - tokens)}},
                ReturnValues="UPDATED_NEW",
            )
        except self._ddb.exceptions.ConditionalCheckFailedException as e:
            raise BudgetExceeded(f"{ctx.tenant_id} exceeded {limit} tokens for {self.period()}") from e
        return int(resp["Attributes"]["used"]["N"])


def converse(bedrock_runtime, resolver: InferenceProfileResolver, budget: TokenBudget, ctx: TenantContext,
             messages: list[dict], system: str) -> dict:
    """One tenant-scoped Bedrock Converse call with pre-flight budget reservation and true-up."""
    max_out = TIER_DEFAULTS[ctx.tier]["max_output_tokens"]
    budget.charge(ctx, max_out)                       # reserve worst case before calling the model
    resp = bedrock_runtime.converse(
        modelId=resolver.arn_for(ctx),
        system=[{"text": system}],
        messages=messages,
        inferenceConfig={"maxTokens": max_out},
        requestMetadata={"tenantId": ctx.tenant_id, "tier": ctx.tier},   # appears in invocation logs
    )
    usage = resp.get("usage", {})
    actual = usage.get("inputTokens", 0) + usage.get("outputTokens", 0)
    if actual > max_out:
        budget.charge(ctx, actual - max_out)          # true-up for input tokens
    return resp
