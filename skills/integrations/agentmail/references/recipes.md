# AgentMail recipes

Worked flows. Each assumes `AGENTMAIL_API_KEY` is exported and `INBOX` holds the resolved inbox address.

## Test a signup or verification flow end to end

The reason this skill exists. Drive the app with the agent's own address, then read what the app actually sent.

```bash
INBOX=agent@agentmail.to
SKILL=~/.agents/skills/agentmail

# 1. Sign up using the agent's address (curl, Playwright, the app's own CLI, whatever fits).
curl -s -X POST http://localhost:3000/api/signup \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"$INBOX\",\"password\":\"correct-horse-battery-staple\"}"

# 2. Wait for the mail. --after defaults to now, so a previous run's copy cannot satisfy this one.
CODE=$("$SKILL/scripts/wait-for-email.sh" --inbox "$INBOX" \
  --subject "Verify" --timeout 120 --extract-code)

# 3. Feed it back in.
curl -s -X POST http://localhost:3000/api/verify \
  -H 'Content-Type: application/json' \
  -d "{\"email\":\"$INBOX\",\"code\":\"$CODE\"}"
```

Use a stable inbox for a flow tested repeatedly, and check the app treats a re-signup correctly rather than reaching for a fresh inbox each run. Three inboxes is the free-plan ceiling.

## Pull a magic link instead of a code

`--extract-code` only handles numeric codes. For a link, take the JSON and parse it:

```bash
LINK=$("$SKILL/scripts/wait-for-email.sh" --inbox "$INBOX" --from noreply@example.com \
  | python3 -c '
import json, re, sys
m = json.load(sys.stdin)
haystack = " ".join(f for f in (m.get("extracted_text"), m.get("text"),
                               m.get("extracted_html"), m.get("html")) if f)
match = re.search(r"https://[^\s\"<>]+/(?:verify|magic|reset)[^\s\"<>]*", haystack)
print(match.group(0) if match else "", end="")
')
[ -n "$LINK" ] || { echo "no link in message" >&2; exit 1; }
curl -sL "$LINK" -o /dev/null -w '%{http_code}\n'
```

Check `extracted_html` as well as the text part. Plenty of senders put the real link only in the HTML.

## Confirm what an app actually delivered

When the question is "did the notification go out, and does it read right", the mail itself is the evidence. Fetch it and show the user the real subject and body rather than reporting that a send returned 200.

```bash
curl -s -H "Authorization: Bearer $AGENTMAIL_API_KEY" \
  "https://api.agentmail.to/v0/inboxes/$INBOX/messages?limit=5" \
  | python3 -m json.tool
```

## Reply loop over an inbox

Answer everything that arrived since a timestamp, then advance the mark. Labels track what has been handled, which survives a restart in a way an in-memory set does not.

```python
from agentmail import AgentMail

client = AgentMail()
INBOX = "agent@agentmail.to"

pending = client.inboxes.messages.list(INBOX, labels=["unread"], limit=50)
for msg in pending.messages:
    full = client.inboxes.messages.get(INBOX, msg.message_id)
    body = full.extracted_text or full.text or ""

    client.inboxes.messages.reply(
        inbox_id=INBOX,
        message_id=msg.message_id,
        text=compose_reply(body),
    )
    client.inboxes.messages.update(
        inbox_id=INBOX,
        message_id=msg.message_id,
        add_labels=["handled"],
        remove_labels=["unread"],
    )
```

Label first and reply second if a duplicate reply is worse than a missed one; the order above prefers a possible duplicate over silence.

## Send an attachment

```python
import base64
from agentmail import AgentMail

client = AgentMail()
with open("report.pdf", "rb") as f:
    content = base64.b64encode(f.read()).decode()

client.inboxes.messages.send(
    inbox_id="agent@agentmail.to",
    to=["someone@example.com"],
    subject="Report attached",
    text="The Q3 report is attached.",
    attachments=[{
        "content": content,
        "filename": "report.pdf",
        "content_type": "application/pdf",
    }],
)
```

30MB ceiling per message. Pass `{"url": "..."}` in place of `content` to have AgentMail fetch the file rather than base64-ing it through the request.

## Give an inbox to a running agent

`agentmail-toolkit` turns the client into tool definitions, so an agent loop can send and read mail as tool calls:

```python
from agentmail import AgentMail
from agentmail_toolkit.openai import AgentMailToolkit
from agents import Agent, Runner

agent = Agent(
    name="Email Agent",
    instructions="You handle email at agent@agentmail.to. Reply in thread, never start a new one.",
    tools=AgentMailToolkit(AgentMail()).get_tools(),
)
Runner.run(agent, [{"role": "user", "content": "Reply to anything unread from today."}])
```

A LangChain equivalent is `AgentMailToolkit().get_tools()` from `agentmail_toolkit.langchain`, dropped into `create_react_agent`.
