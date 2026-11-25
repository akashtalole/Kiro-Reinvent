#!/usr/bin/env bash
# Start a Kiro Crew agent run from another tool (Feature Preview: Settings → Developer → Feature Previews → Webhooks).
# Usage: KIROCREW_WEBHOOK_TOKEN=kc_whk_... ./webhook.sh "message for the agent"
set -euo pipefail
: "${KIROCREW_WEBHOOK_TOKEN:?set KIROCREW_WEBHOOK_TOKEN (create one in Settings → Webhooks)}"
MESSAGE="${1:?usage: webhook.sh \"message\"}"
URL="${KIROCREW_URL:-http://localhost:5476}/api/hooks/agent"
BODY=$(python3 -c 'import json,sys; print(json.dumps({"message": sys.argv[1]}))' "$MESSAGE")
curl -sS -X POST "$URL" \
  -H "Authorization: Bearer ${KIROCREW_WEBHOOK_TOKEN}" \
  -H "Content-Type: application/json" \
  --data "$BODY"
echo
