#!/usr/bin/env bash
# tenantctl — idempotent tenant lifecycle automation for a pooled multi-tenant SaaS on AWS.
# Designed to be driven by humans, CI, Kiro agents (via the tenant-ops skill) or Kiro Crew bots.
#
#   tenantctl.sh onboard  <tenant-id> <tier> <admin-email>   # basic | premium | enterprise
#   tenantctl.sh suspend  <tenant-id> <reason>
#   tenantctl.sh resume   <tenant-id>
#   tenantctl.sh offboard <tenant-id> <ticket-id>            # export → disable → delete (requires CONFIRM=<tenant-id>)
#   tenantctl.sh status   <tenant-id>
#
# Env: TENANTS_TABLE, DATA_TABLE, USER_POOL_ID, REST_API_ID, API_STAGE, EXPORT_BUCKET,
#      USAGE_PLAN_BASIC|PREMIUM|ENTERPRISE, BASE_MODEL_ARN (Bedrock foundation model / system profile ARN)
#      DRY_RUN=1 prints every AWS call instead of executing it.
set -euo pipefail

aws_() {
  if [[ "${DRY_RUN:-0}" == "1" ]]; then
    { printf 'DRY_RUN aws'; printf ' %q' "$@"; printf '\n'; } >&2
    [[ " $* " == *" --query "* ]] && echo "dry-run-id"
    return 0
  fi
  aws "$@"
}
need() { for v in "$@"; do [[ -n "${!v:-}" ]] || { echo "missing env $v" >&2; exit 2; }; done; }
log()  { printf '{"ts":"%s","tenant":"%s","action":"%s","detail":"%s"}\n' "$(date -u +%FT%TZ)" "$TENANT" "$1" "${2:-}" >&2; }
valid_id() { [[ "$1" =~ ^t-[a-z0-9]{4,32}$ ]] || { echo "tenant id must match ^t-[a-z0-9]{4,32}$" >&2; exit 2; }; }

cmd="${1:-}"; TENANT="${2:-}"; [[ -n "$cmd" && -n "$TENANT" ]] || { sed -n 2,12p "$0"; exit 2; }
valid_id "$TENANT"

case "$cmd" in
onboard)
  TIER="${3:?tier}"; EMAIL="${4:?admin email}"
  [[ "$TIER" =~ ^(basic|premium|enterprise)$ ]] || { echo "bad tier" >&2; exit 2; }
  need TENANTS_TABLE USER_POOL_ID BASE_MODEL_ARN
  PLAN_VAR="USAGE_PLAN_${TIER^^}"; need "$PLAN_VAR"
  log onboard.start "$TIER"
  # 1. tenant record (conditional → idempotent; re-running does not clobber)
  aws_ dynamodb put-item --table-name "$TENANTS_TABLE" \
    --item "{\"pk\":{\"S\":\"TENANT#$TENANT\"},\"tier\":{\"S\":\"$TIER\"},\"status\":{\"S\":\"ACTIVE\"},\"createdAt\":{\"S\":\"$(date -u +%FT%TZ)\"}}" \
    --condition-expression "attribute_not_exists(pk)" || log onboard.exists
  # 2. admin user bound to the tenant (custom:tenantId is the isolation key everywhere downstream)
  aws_ cognito-idp admin-create-user --user-pool-id "$USER_POOL_ID" --username "$EMAIL" \
    --user-attributes Name=email,Value="$EMAIL" Name=email_verified,Value=true Name=custom:tenantId,Value="$TENANT" \
    --desired-delivery-mediums EMAIL || log onboard.user_exists
  # 3. API key + tier usage plan (rate limits & quotas per tier → noisy-neighbour control)
  KEY_ID=$(aws_ apigateway create-api-key --name "$TENANT" --enabled --tags tenantId="$TENANT" --query id --output text)
  aws_ apigateway create-usage-plan-key --usage-plan-id "${!PLAN_VAR}" --key-id "$KEY_ID" --key-type API_KEY
  # 4. per-tenant Bedrock application inference profile → per-tenant AI cost in Cost Explorer
  aws_ bedrock create-inference-profile --inference-profile-name "$TENANT-default" \
    --model-source copyFrom="$BASE_MODEL_ARN" \
    --tags key=tenantId,value="$TENANT" key=tier,value="$TIER"
  log onboard.done "$TIER" ;;
suspend)
  REASON="${3:?reason}"; need TENANTS_TABLE
  aws_ dynamodb update-item --table-name "$TENANTS_TABLE" --key "{\"pk\":{\"S\":\"TENANT#$TENANT\"}}" \
    --update-expression "SET #s = :s, suspendedReason = :r" --expression-attribute-names '{"#s":"status"}' \
    --expression-attribute-values "{\":s\":{\"S\":\"SUSPENDED\"},\":r\":{\"S\":\"$REASON\"}}"
  for k in $(aws_ apigateway get-api-keys --name-query "$TENANT" --query 'items[].id' --output text); do
    aws_ apigateway update-api-key --api-key "$k" --patch-operations op=replace,path=/enabled,value=false; done
  log suspend "$REASON" ;;
resume)
  need TENANTS_TABLE
  aws_ dynamodb update-item --table-name "$TENANTS_TABLE" --key "{\"pk\":{\"S\":\"TENANT#$TENANT\"}}" \
    --update-expression "SET #s = :s REMOVE suspendedReason" --expression-attribute-names '{"#s":"status"}' \
    --expression-attribute-values '{":s":{"S":"ACTIVE"}}'
  for k in $(aws_ apigateway get-api-keys --name-query "$TENANT" --query 'items[].id' --output text); do
    aws_ apigateway update-api-key --api-key "$k" --patch-operations op=replace,path=/enabled,value=true; done
  log resume ;;
offboard)
  TICKET="${3:?ticket id required for offboarding}"; need TENANTS_TABLE DATA_TABLE EXPORT_BUCKET
  [[ "${CONFIRM:-}" == "$TENANT" ]] || { echo "refusing: set CONFIRM=$TENANT to offboard (ticket $TICKET)" >&2; exit 3; }
  log offboard.start "$TICKET"
  # export first (contractual data return), then disable, then delete
  aws_ dynamodb query --table-name "$DATA_TABLE" --key-condition-expression "pk = :p" \
    --expression-attribute-values "{\":p\":{\"S\":\"TENANT#$TENANT\"}}" --output json > "/tmp/$TENANT-export.json"
  aws_ s3 cp "/tmp/$TENANT-export.json" "s3://$EXPORT_BUCKET/offboarding/$TENANT/$TICKET.json" --sse aws:kms
  "$0" suspend "$TENANT" "offboarding:$TICKET"
  aws_ dynamodb update-item --table-name "$TENANTS_TABLE" --key "{\"pk\":{\"S\":\"TENANT#$TENANT\"}}" \
    --update-expression "SET #s = :s, offboardTicket = :t" --expression-attribute-names '{"#s":"status"}' \
    --expression-attribute-values "{\":s\":{\"S\":\"OFFBOARDED\"},\":t\":{\"S\":\"$TICKET\"}}"
  log offboard.done "$TICKET — data deletion runs after the contractual retention window" ;;
status)
  need TENANTS_TABLE
  aws_ dynamodb get-item --table-name "$TENANTS_TABLE" --key "{\"pk\":{\"S\":\"TENANT#$TENANT\"}}" --output json ;;
*) sed -n 2,12p "$0"; exit 2 ;;
esac
