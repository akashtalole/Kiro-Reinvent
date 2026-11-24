"""Tenant-aware telemetry for a pooled multi-tenant service.

* `emit_usage()` writes CloudWatch Embedded Metric Format (EMF) to stdout. In Lambda / ECS with the
  CloudWatch agent, these lines become metrics (namespace SaaS/Tenants) with no API calls.
* `tenant_span_attributes()` gives OpenTelemetry attributes so every trace — including agent traces in
  CloudWatch Omni — can be sliced by tenant and tier.

Dimension sets are deliberately small: per-tenant metrics multiply cardinality and cost, so the
high-cardinality `TenantId` dimension is only used for the few metrics you bill or alarm on.
"""
from __future__ import annotations

import json
import sys
import time
from typing import TextIO

NAMESPACE = "SaaS/Tenants"
BILLABLE = {"Requests": "Count", "AITokens": "Count", "StorageGB": "Gigabytes", "LatencyMs": "Milliseconds"}


def emf_record(tenant_id: str, tier: str, feature: str, metrics: dict[str, float], **props) -> dict:
    unknown = set(metrics) - set(BILLABLE)
    if unknown:
        raise ValueError(f"unknown metrics {sorted(unknown)}; allowed: {sorted(BILLABLE)}")
    return {
        "_aws": {
            "Timestamp": int(time.time() * 1000),
            "CloudWatchMetrics": [{
                "Namespace": NAMESPACE,
                # per-tenant (for billing/alarms), per-tier (for capacity), per-feature (for product)
                "Dimensions": [["TenantId"], ["Tier"], ["Tier", "Feature"]],
                "Metrics": [{"Name": k, "Unit": BILLABLE[k]} for k in metrics],
            }],
        },
        "TenantId": tenant_id, "Tier": tier, "Feature": feature, **metrics, **props,
    }


def emit_usage(tenant_id: str, tier: str, feature: str, metrics: dict[str, float], out: TextIO = sys.stdout, **props) -> None:
    out.write(json.dumps(emf_record(tenant_id, tier, feature, metrics, **props)) + "\n")


def tenant_span_attributes(tenant_id: str, tier: str, region: str | None = None) -> dict[str, str]:
    attrs = {"tenant.id": tenant_id, "tenant.tier": tier}
    if region:
        attrs["tenant.region"] = region
    return attrs
