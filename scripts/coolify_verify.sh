#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "ข้อผิดพลาด: กรุณาระบุ Proxy URL เช่น bash scripts/coolify_verify.sh https://proxy.example.com"
  exit 1
fi

BASE_URL="${1%/}"

check_endpoint() {
  local path="$1"
  local accepted="$2"
  local status
  status=$(curl -s -o /tmp/smlairouter-coolify-check.out -w "%{http_code}" "${BASE_URL}${path}" || true)

  if [[ " ${accepted} " == *" ${status} "* ]]; then
    echo "✅ CHECK ${path} -> HTTP ${status}"
  else
    echo "ข้อผิดพลาด: CHECK ${path} -> HTTP ${status} (expected: ${accepted})"
    if [[ -s /tmp/smlairouter-coolify-check.out ]]; then
      echo "รายละเอียด: $(tr '\n' ' ' < /tmp/smlairouter-coolify-check.out | cut -c1-200)"
    fi
    return 1
  fi
}

check_chat() {
  local status
  status=$(curl -s -o /tmp/smlairouter-coolify-chat.out -w "%{http_code}" \
    -H "Content-Type: application/json" \
    -X POST "${BASE_URL}/v1/chat/completions" \
    -d '{"model":"auto","messages":[{"role":"user","content":"ตอบว่า ok"}],"max_tokens":5}' || true)

  case "${status}" in
    200|401|403|422|502|503)
      echo "✅ CHECK /v1/chat/completions -> HTTP ${status}"
      ;;
    *)
      echo "ข้อผิดพลาด: CHECK /v1/chat/completions -> HTTP ${status} (expected: 200/401/403/422/502/503)"
      if [[ -s /tmp/smlairouter-coolify-chat.out ]]; then
        echo "รายละเอียด: $(tr '\n' ' ' < /tmp/smlairouter-coolify-chat.out | cut -c1-200)"
      fi
      return 1
      ;;
  esac
}

check_endpoint "/" "200"
check_endpoint "/v1/models" "200"
check_chat

echo "✅ Coolify smoke verification ผ่านทั้งหมด"
