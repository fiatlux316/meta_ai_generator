#!/usr/bin/env bash
set -euo pipefail

# ../env.local 에서 DD_API_KEY, DD_APP_KEY 환경 변수를 가져오기 
. ../env.local

DD_API_KEY="${DD_API_KEY}"
DD_APP_KEY="${DD_APP_KEY}"
FROM_TIME="now-1h"
TO_TIME="now"
#QUERY="service:erody-bo-backend-20 status:error"
QUERY="service:erody-assist-service @http.status_code:[200 TO 599]"
LIMIT=3

payload=$(cat <<EOF
{
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
EOF
)

curl -sS -X POST \
  -H "Content-Type: application/json" \
  -H "DD-API-KEY: ${DD_API_KEY}" \
  -H "DD-APPLICATION-KEY: ${DD_APP_KEY}" \
  --data-binary "${payload}" \
  "https://api.datadoghq.com/api/v2/logs/events/search"

