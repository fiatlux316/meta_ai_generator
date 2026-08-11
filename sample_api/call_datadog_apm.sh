#!/usr/bin/env bash
set -euo pipefail

# ../env.local 에서 DD_API_KEY, DD_APP_KEY 환경 변수를 가져오기 
. ../env.local

DD_API_KEY="${DD_API_KEY}"
DD_APP_KEY="${DD_APP_KEY}"
FROM_TIME="2026-08-05T09:00:00.000Z"
TO_TIME="2026-08-05T10:00:00.000Z"
QUERY="service:erody-bo-backend-20 status:error"
LIMIT=3

payload=$(cat <<EOF
{
  "data": {
    "type": "search_request",
    "attributes": {
      "filter": {
        "query": "${QUERY}",
        "from": "${FROM_TIME}",
        "to": "${TO_TIME}"
      },
      "sort": "-timestamp",
      "options": {
        "timezone": "Asia/Seoul"
      },
      "page": {
        "limit": ${LIMIT}
      }
    }
  }
}
EOF
)

curl -sS -X POST \
  -H "Content-Type: application/json" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}" \
  --data-binary "${payload}" \
  "https://api.datadoghq.com/api/v2/spans/events/search"

