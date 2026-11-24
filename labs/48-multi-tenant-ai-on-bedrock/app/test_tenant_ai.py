import pytest

from tenant_ai import (BudgetExceeded, InferenceProfileResolver, TenantContext, TenantError, TokenBudget,
                       converse, kb_filter, memory_namespace)


class CCF(Exception):
    pass


class FakeDDB:
    class exceptions:
        ConditionalCheckFailedException = CCF

    def __init__(self):
        self.used = {}

    def update_item(self, Key, ExpressionAttributeValues, **_):
        pk = Key["pk"]["S"]
        t = int(ExpressionAttributeValues[":t"]["N"])
        mx = int(ExpressionAttributeValues[":max"]["N"])
        cur = self.used.get(pk)
        if cur is not None and cur > mx:
            raise CCF()
        self.used[pk] = (cur or 0) + t
        return {"Attributes": {"used": {"N": str(self.used[pk])}}}


class FakeBedrock:
    def __init__(self):
        self.calls = 0

    def list_inference_profiles(self, typeEquals, nextToken=None):
        self.calls += 1
        if nextToken is None:
            return {"inferenceProfileSummaries": [{"inferenceProfileName": "t-other-default", "inferenceProfileArn": "arn:o"}],
                    "nextToken": "p2"}
        return {"inferenceProfileSummaries": [{"inferenceProfileName": "t-acme01-default", "inferenceProfileArn": "arn:acme"}]}


class FakeRuntime:
    def __init__(self):
        self.last = None

    def converse(self, **kw):
        self.last = kw
        return {"output": {"message": {"role": "assistant", "content": [{"text": "ok"}]}},
                "usage": {"inputTokens": 900, "outputTokens": 100}}


ACME = TenantContext.from_claims({"custom:tenantId": "t-acme01", "custom:tier": "basic", "sub": "u-1"})


def test_claims_required():
    with pytest.raises(TenantError):
        TenantContext.from_claims({"sub": "u"})
    with pytest.raises(TenantError):
        TenantContext.from_claims({"custom:tenantId": "t-x", "custom:tier": "platinum"})


def test_resolver_paginates_and_caches():
    b = FakeBedrock()
    r = InferenceProfileResolver(b)
    assert r.arn_for(ACME) == "arn:acme" and b.calls == 2
    r.arn_for(ACME)
    assert b.calls == 2


def test_isolation_helpers():
    assert kb_filter(ACME) == {"equals": {"key": "tenantId", "value": "t-acme01"}}
    assert kb_filter(ACME, {"equals": {"key": "lang", "value": "en"}})["andAll"][0]["equals"]["value"] == "t-acme01"
    assert memory_namespace(ACME) == "/tenant/t-acme01/user/u-1/facts"


def test_budget_blocks_when_exhausted():
    ddb = FakeDDB()
    budget = TokenBudget(ddb, "budgets")
    budget.charge(ACME, 1_999_000)
    with pytest.raises(BudgetExceeded):
        budget.charge(ACME, 5_000)


def test_converse_uses_tenant_profile_metadata_and_trues_up():
    ddb, rt = FakeDDB(), FakeRuntime()
    converse(rt, InferenceProfileResolver(FakeBedrock()), TokenBudget(ddb, "b"), ACME,
             [{"role": "user", "content": [{"text": "hi"}]}], "be brief")
    assert rt.last["modelId"] == "arn:acme"
    assert rt.last["requestMetadata"]["tenantId"] == "t-acme01"
    assert rt.last["inferenceConfig"]["maxTokens"] == 800
    assert list(ddb.used.values())[0] == 1000        # 800 reserved + 200 true-up = 900 in + 100 out
