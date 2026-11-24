import io
import json

import pytest

from tenant_telemetry import emf_record, emit_usage, tenant_span_attributes


def test_emf_shape():
    r = emf_record("t-acme01", "premium", "export", {"Requests": 1, "AITokens": 812}, requestId="r-1")
    cw = r["_aws"]["CloudWatchMetrics"][0]
    assert cw["Namespace"] == "SaaS/Tenants"
    assert ["TenantId"] in cw["Dimensions"]
    assert {m["Name"] for m in cw["Metrics"]} == {"Requests", "AITokens"}
    for dims in cw["Dimensions"]:          # every dimension key must be a top-level member
        assert all(d in r for d in dims)
    for m in cw["Metrics"]:                # every metric value must be a top-level member
        assert isinstance(r[m["Name"]], (int, float))


def test_rejects_unknown_metric():
    with pytest.raises(ValueError):
        emf_record("t-1", "basic", "x", {"Bogus": 1})


def test_emit_is_one_json_line():
    buf = io.StringIO()
    emit_usage("t-acme01", "basic", "search", {"LatencyMs": 41.5}, out=buf)
    line = buf.getvalue()
    assert line.endswith("\n") and json.loads(line)["TenantId"] == "t-acme01"


def test_span_attributes():
    assert tenant_span_attributes("t-1", "enterprise", "eu-west-1") == {
        "tenant.id": "t-1", "tenant.tier": "enterprise", "tenant.region": "eu-west-1"}
