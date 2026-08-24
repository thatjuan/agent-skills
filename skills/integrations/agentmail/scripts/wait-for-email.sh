#!/usr/bin/env bash
# Poll an AgentMail inbox until a matching message arrives, then print it as JSON.
#
# Exits 0 with the full message on stdout, or 1 on timeout. By default only
# messages that arrive AFTER the script starts count, so a stale copy of last
# run's verification mail never satisfies this run.
#
#   wait-for-email.sh --inbox agent@agentmail.to --from noreply@example.com
#   wait-for-email.sh --inbox agent@agentmail.to --subject "Verify" --extract-code
#
# Requires: curl, python3, and AGENTMAIL_API_KEY in the environment.
set -euo pipefail

API=${AGENTMAIL_API_BASE:-https://api.agentmail.to}
INBOX=${AGENTMAIL_INBOX_ID:-}
FROM=""
SUBJECT=""
AFTER=""
TIMEOUT=120
INTERVAL=5
EXTRACT_CODE=0

usage() {
  sed -n '2,11p' "$0" | sed 's/^# \{0,1\}//'
  cat <<'USAGE'

Flags:
  --inbox <id>       Inbox address. Defaults to $AGENTMAIL_INBOX_ID.
  --from <substr>    Match sender by substring.
  --subject <substr> Match subject by substring.
  --after <iso8601>  Only messages after this timestamp. Defaults to now.
  --timeout <sec>    Give up after this long. Default 120.
  --interval <sec>   Seconds between polls. Default 5.
  --extract-code     Print the first 4-8 digit code in the body instead of JSON.
  -h, --help         This text.
USAGE
}

while [ $# -gt 0 ]; do
  case "$1" in
    --inbox) INBOX=$2; shift 2 ;;
    --from) FROM=$2; shift 2 ;;
    --subject) SUBJECT=$2; shift 2 ;;
    --after) AFTER=$2; shift 2 ;;
    --timeout) TIMEOUT=$2; shift 2 ;;
    --interval) INTERVAL=$2; shift 2 ;;
    --extract-code) EXTRACT_CODE=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown flag: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[ -n "${AGENTMAIL_API_KEY:-}" ] || { echo "AGENTMAIL_API_KEY is not set" >&2; exit 2; }
[ -n "$INBOX" ] || { echo "--inbox is required (or set AGENTMAIL_INBOX_ID)" >&2; exit 2; }
[ -n "$AFTER" ] || AFTER=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Build the query string with python3 so substrings with spaces or @ survive.
QS=$(python3 - "$AFTER" "$FROM" "$SUBJECT" <<'PY'
import sys, urllib.parse
after, sender, subject = sys.argv[1:4]
params = [("limit", "10"), ("after", after), ("ascending", "false")]
if sender:
    params.append(("from", sender))
if subject:
    params.append(("subject", subject))
print(urllib.parse.urlencode(params))
PY
)

deadline=$(( $(date +%s) + TIMEOUT ))
while [ "$(date +%s)" -lt "$deadline" ]; do
  body=$(curl -sS -H "Authorization: Bearer $AGENTMAIL_API_KEY" \
    "$API/v0/inboxes/$INBOX/messages?$QS") || true

  msg_id=$(printf '%s' "$body" | python3 -c '
import json, sys
try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)
if isinstance(data, dict) and data.get("name", "").endswith("Error"):
    print("ERROR:" + data.get("message", "request failed"), file=sys.stderr)
    sys.exit(0)
for m in (data.get("messages") or []):
    print(m["message_id"])
    break
')

  if [ -n "$msg_id" ]; then
    full=$(curl -sS -H "Authorization: Bearer $AGENTMAIL_API_KEY" \
      "$API/v0/inboxes/$INBOX/messages/$msg_id")
    if [ "$EXTRACT_CODE" -eq 1 ]; then
      printf '%s' "$full" | python3 -c '
import json, re, sys
m = json.load(sys.stdin)
body = m.get("extracted_text") or m.get("text") or m.get("extracted_html") or m.get("html") or ""
found = re.search(r"\b(\d{4,8})\b", body)
if not found:
    print("no code found in message body", file=sys.stderr)
    sys.exit(1)
print(found.group(1))
'
    else
      printf '%s\n' "$full"
    fi
    exit 0
  fi

  sleep "$INTERVAL"
done

echo "timed out after ${TIMEOUT}s waiting for a message in $INBOX" >&2
exit 1
