#!/usr/bin/env bash
# Lab 56 helper: a harmless CloudWatch alarm on a custom metric, for exercising Ops Mission Control.
# Usage: AWS_REGION=us-east-1 ./test-alarm.sh create|fire|ok|delete
set -euo pipefail
NAME="KiroReinvent-Lab56-SyntheticErrors"
NS="KiroReinventLabs"
REGION="${AWS_REGION:?set AWS_REGION}"
case "${1:-}" in
  create)
    aws cloudwatch put-metric-alarm --region "$REGION" --alarm-name "$NAME" \
      --alarm-description "Lab 56 synthetic alarm. Safe to silence or delete. Runbook: no customer impact." \
      --namespace "$NS" --metric-name SyntheticErrors --statistic Sum --period 60 \
      --evaluation-periods 1 --threshold 1 --comparison-operator GreaterThanOrEqualToThreshold \
      --treat-missing-data notBreaching
    echo "created $NAME" ;;
  fire)
    aws cloudwatch set-alarm-state --region "$REGION" --alarm-name "$NAME" \
      --state-value ALARM --state-reason "Lab 56 test: forced into ALARM"
    echo "$NAME is now ALARM" ;;
  ok)
    aws cloudwatch set-alarm-state --region "$REGION" --alarm-name "$NAME" \
      --state-value OK --state-reason "Lab 56 test: reset"
    echo "$NAME is now OK" ;;
  delete)
    aws cloudwatch delete-alarms --region "$REGION" --alarm-names "$NAME"
    echo "deleted $NAME" ;;
  *) echo "usage: AWS_REGION=... $0 create|fire|ok|delete" >&2; exit 2 ;;
esac
