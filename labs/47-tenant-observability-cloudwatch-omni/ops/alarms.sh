#!/usr/bin/env bash
# Per-tier anomaly alarms + a per-tenant hard alarm for your biggest tenants. Idempotent (put-* calls).
set -euo pipefail
TOPIC_ARN="${TOPIC_ARN:?SNS topic for on-call}"
for TIER in basic premium enterprise; do
  aws cloudwatch put-anomaly-detector --namespace SaaS/Tenants --metric-name LatencyMs \
    --dimensions Name=Tier,Value="$TIER" --stat p95
  aws cloudwatch put-metric-alarm --alarm-name "latency-anomaly-$TIER" \
    --evaluation-periods 3 --comparison-operator GreaterThanUpperThreshold --threshold-metric-id ad1 \
    --metrics "[{\"Id\":\"m1\",\"ReturnData\":true,\"MetricStat\":{\"Metric\":{\"Namespace\":\"SaaS/Tenants\",\"MetricName\":\"LatencyMs\",\"Dimensions\":[{\"Name\":\"Tier\",\"Value\":\"$TIER\"}]},\"Period\":300,\"Stat\":\"p95\"}},{\"Id\":\"ad1\",\"Expression\":\"ANOMALY_DETECTION_BAND(m1, 2)\"}]" \
    --alarm-actions "$TOPIC_ARN" --treat-missing-data notBreaching
done
for TENANT in ${TOP_TENANTS:-}; do   # e.g. TOP_TENANTS="t-acme01 t-globex2"
  aws cloudwatch put-metric-alarm --alarm-name "ai-tokens-spike-$TENANT" --namespace SaaS/Tenants \
    --metric-name AITokens --dimensions Name=TenantId,Value="$TENANT" --statistic Sum --period 3600 \
    --evaluation-periods 1 --threshold "${TOKEN_LIMIT:-2000000}" --comparison-operator GreaterThanThreshold \
    --alarm-actions "$TOPIC_ARN" --treat-missing-data notBreaching
done
