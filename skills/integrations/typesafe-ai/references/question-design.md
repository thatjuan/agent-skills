# Question design

Rules for writing `instructions`, `criteria`, and `state`, with examples from the TypeSafe docs.

## 1. Choosing the primitive

Pick the type whose answer your code acts on directly: a Choice maps onto code paths, a Score onto a threshold, a Noul onto an `if`.

| The answer is... | Use | Answer field |
| --- | --- | --- |
| A yes/no fact about the state | Noul | `noul` (P(yes), 0 to 1) |
| One of N options with no order between them | Choice | `choice`, `probabilities`, `confidence` |
| A position on an ordered spectrum you can describe in steps | Score | `score`, `legend`, `probabilities`, `confidence` |

Noul 0.5 is not "medium". It means yes and no got equal probability. "Is this candidate strong in Python?" asked as a Noul gives a number that cannot be read as a skill level. Ask for the level with a Score whose levels are situations (no experience, some familiarity, daily use, deep expertise), or ask a yes/no with a definite condition:

```
Before: Noul  "Is this candidate strong in Python?"
After:  Noul  "Does the resume state that the candidate has used Python at work?"
        Score "How much Python experience does the candidate have?" with four described levels
```

When there is no in-between at all, use a Choice or several Nouls instead of a Score. When a Score's top has a rare extreme you act on differently ("abusive or threatening" above "very angry"), give it its own level.

(source: primitives.md, primitives/score.md, primitives/noul.md)

## 2. Instructions

Write the complete question in `instructions`. The question id is for your code only and is never sent to the model, so `refund_requested` with empty instructions tells the model nothing.

```python
questions = {
    "refund_requested": Noul(
        instructions="Does the customer request a refund?",
    ),
}
```

When the state is an object, point the question at the part it is about with a backticked dot-and-index path. Keep the backtick characters inside the string.

```python
questions = {
    "refund_requested": {
        "type": "noul",
        "instructions": "Does `ticket.messages[0].text` request a refund?",
    },
    "policy_supports_refund": {
        "type": "noul",
        "instructions": (
            "Does `refund_policy` support the refund requested "
            "in `ticket.messages[0].text`, given `order.charges`?"
        ),
    },
}
```

Phrase a Noul so a high probability means yes, as a question ("Is the customer asking for a human agent?") or a statement to judge as true ("the customer is requesting a refund"); try both on your data.

Ask for one snap judgment per question. "Does this message convey urgency?" is a good question. "Analyze this message and determine the best course of action" is a signal to split into several questions and combine them in code.

(source: primitives.md, primitives/noul.md)

## 3. Choice criteria

Option names and descriptions are both sent to the model, so write descriptions that separate the options from each other:

```python
criteria={
    "returns": "Exchanges, refunds, wrong or damaged items",
    "shipping": "Delivery status, delays, lost packages",
    "billing": "Charges, invoices, payment problems",
}
```

Add an `other` or `none of the above` option whenever the list might not cover every input, so the model can say none of the others fit:

```python
"other": "A return reason that fits none of the above",
```

Use `null` descriptions when the names are clear on their own: `criteria={"calm": None, "frustrated": None, "angry": None}`.

Give the full list. A Choice takes up to 255 options and each costs a few tokens, so send every team, category, or product rather than a shortlist. Past 255, narrow in two stages.

When two options keep getting confused, describe each with an object: what it covers, what belongs to the neighbour instead, and example inputs. Use the same field names on every option so the model compares like with like. `question`, `focus`, `what`, `not_for`, and `examples` are names you choose; none is reserved.

```
instructions: {
  question: 'Which returns topic is the customer asking about?',
  focus: 'Classify the information the customer wants.',
},
criteria: {
  return_policy: {
    what: 'Whether and how an item can be returned',
    not_for: 'Progress of a return already sent',
    examples: ["Can I return shoes I've worn once?", 'How long do I have to return an order?'],
  },
  return_status: {
    what: 'Progress of a return already sent',
    not_for: 'Whether and how an item can be returned',
    examples: ['Has my return arrived yet?', 'When will my refund be paid?'],
  },
},
```

(source: primitives/choice.md)

## 4. Score criteria

`criteria` is an ordered array of 2 to 10 level descriptions from the low end to the high end. Level number = array index. Use as many levels as you can describe distinctly; three is fine.

Describe situations, not degrees. Each level is judged on its own against the state, with no view of its number or its neighbours, so relative wording ("worse than the previous level") and numbers carry nothing. The docs show the cost on a misaligned-button report:

```
instructions: "Rate severity from 0 to 2, where 2 is worst"
criteria: ["0", "1", "2"]
→ score 0.57, confidence 0.35, probabilities 0: 0.43, 1: 0.57, 2: 0.0
```

The same report against descriptive levels scores 0.0 at confidence 1.0:

```python
criteria=[
    "Cosmetic; no impact to functionality",
    "Broken or degraded feature, but workaround exists",
    "Blocking issue; no workaround exists",
],
```

Keep each Score to one dimension. A level reading "punctual and smart and experienced" measures three things; an input high on one and low on another cannot be placed. Split into one Score per thing and weight them in code.

Read `score` as the probability-weighted mean of level numbers: with probabilities `{0: 0.0, 1: 0.7, 2: 0.3}`, `score = 0 x 0.0 + 1 x 0.70 + 2 x 0.30 = 1.30`. Different distributions produce the same score: 1.0 can be all probability on level 1, or half each on levels 0 and 2, so read `probabilities` and `confidence` alongside it. Round to the nearest level when code needs one outcome; use the fraction to rank.

Before weighting Scores of different lengths, divide each by its top level number so all sit on 0 to 1:

```python
def normalized(answers, question_id: str) -> float:
    """Put a score on 0 to 1 by dividing by its top level number."""
    top_level = len(TRIAGE_QUESTIONS[question_id].criteria) - 1
    return answers[question_id].score / top_level
```

Structured levels (`{what, examples}` objects) help when the model keeps landing between two neighbouring levels on inputs you consider clear. Examples only help when they look like real inputs, and higher confidence alone does not show the description got better; check against inputs with known levels.

(source: primitives/score.md)

## 5. Noul criteria

`criteria` is optional `{true, false}` descriptions. Add it when the yes/no boundary is subtle, and try the question with and without it.

```
is_repeat_contact: {
  type: 'noul',
  instructions: 'Has the customer contacted support about this before?',
  criteria: {
    true: 'Mentions a prior attempt, ticket, or that they have asked before',
    false: 'No sign of any previous contact',
  },
},
```

Make `true` the case your code acts on (escalate, quarantine, flag) and keep the instruction aligned with it: a Noul whose `true` means no performs worse. Both sides may be objects with `what`, `not_for`, and `examples`, as in `triage_ticket.py` below.

(source: primitives/noul.md, primitives/advanced.md, model-jaggedness/jev-1.13.md)

## 6. Structured instructions and criteria

Every `instructions` value, Choice option description, Score level, and Noul `true`/`false` is an `EntryType`: string, object, array, or null. Use structure when a question has several parts (keys label them) or when the supporting data is already JSON (a schema, a taxonomy, a database row); pass it as is instead of templating it into a string. A short, unambiguous question stays a string.

```json
"instructions": {
  "question": "Does the claimed sender identity conflict with the sending domain?",
  "compare": ["ticket.sender.display_name", "ticket.sender.email"],
  "focus": "Compare the named organization with the email domain."
}
```

To classify into a deep taxonomy, ask one Choice per level and walk the tree in code. Each option's value is the child's subtree, so the model sees what lives under a branch before committing:

```
criteria: {
  'Sporting Goods': {
    Cycling: ['Bike Bottles & Cages', 'Bike Lights', 'Helmets'],
    Fitness: ['Yoga Mats', 'Resistance Bands'],
    Outdoor: ['Tents', 'Sleeping Bags', 'Hydration Packs'],
  },
  'Home & Kitchen': {
    Drinkware: ['Water Bottles', 'Travel Mugs', 'Tumblers'],
    Cookware: ['Pots & Pans', 'Bakeware'],
  },
  'Baby & Toddler': ['Sippy Cups', 'Bottle Warmers', 'Bibs'],
},
```

Trimming rule: "If a branch is too large, trim the value to its direct children and a sample of leaves." Use `probabilities` to decide whether a close split is worth exploring on both branches.

(source: primitives/advanced.md)

## 7. State design

Use an object for most requests so each part has a descriptive name and its relationships stay clear; a string suits a single piece of text, an array a sequence of messages or records. Put related parts together when the decision compares them (the ticket, the order, the refund policy).

Include only the context the current questions need; filter and retrieve in code first, since unrelated material distracts the model. Put current facts in the state from your own knowledge base rather than relying on model weights.

```
Before: state = full customer record + every order + whole ticket thread
After:  state = {"ticket": {message, sender, links}, "customer": {plan, open_orders}, "policy": {...}}
```

State is text only. English is the primary training language; other languages, including CJK scripts, are accepted with lower accuracy, so test non-English inputs on your own content.

(source: concepts/state.md, concepts/how-to-build-with-system-one.md)

## 8. Confidence and probabilities

`confidence` (Choice and Score only; Noul has no confidence field) collapses the shape of `probabilities` into 0 to 1. Start with three bands: high acts automatically, medium adds a confirmation or review step, low does not act and routes to a person, asks for clarification, or falls back to another system.

Thresholds scale with stakes. A read-only action can run at moderate confidence; a destructive one needs a higher bar in the same request:

```python
if confidence < 0.5:
    # Model is genuinely unsure. Don't guess.
    route_to_human(user_message)

elif action.choice == "check_balance":
    # Low stakes. Showing the wrong screen is recoverable.
    show_balance(account_id)

elif action.choice == "approve_transfer":
    if confidence > 0.9:
        # High stakes, high confidence. Proceed with confirmation.
        confirm_then_execute(account_id)
    else:
        # High stakes, moderate confidence. Verify first.
        ask_user_to_confirm(account_id)
```

Start conservative, then tune by plotting confidence against accuracy on your own data. If you only want the best option, take the highest probability; no threshold is needed. If you have a statistical rule in mind, compute it from the full `probabilities` rather than from `confidence`. Runner-up probabilities are usable too: the Choice page copies a second team whenever its probability exceeds 0.25.

(source: confidence.md, primitives/choice.md, agent-skill.md)

## House-style example

Verbatim from the docs: deterministic checks first, a trimmed structured state, atomic questions in one request, weighted composition, and confidence gates in code.

```python
from typesafe_sdk import Choice, Noul, NoulCriteria, Score, TypeSafeClient


def triage_ticket(ticket, customer):
    # Handle deterministic states without calling a model.
    if ticket["status"] == "closed":
        return "no_action"

    open_orders = [
        order for order in customer["orders"] if order["status"] != "delivered"
    ]

    # Include only the structured context needed by the questions below.
    state = {
        "ticket": {
            "message": ticket["message"],
            "sender": ticket["sender"],
            "links": ticket["links"],
        },
        "customer": {
            "plan": customer["plan"],
            "open_orders": open_orders,
        },
        "policy": {
            "sensitive_credentials": ["password", "security code", "API key"],
        },
    }

    # Ask structured, atomic questions together so they run in parallel.
    questions = {
        "topic": Choice(
            instructions={
                "question": "Which team should handle `ticket.message`?",
                "focus": "Classify the customer's primary request.",
            },
            criteria={
                "billing": {
                    "what": "Charges, invoices, refunds, or subscriptions",
                    "not_for": "Order tracking or account access",
                    "examples": ["I was charged twice", "Where is my refund?"],
                },
                "orders": {
                    "what": "Order status, delivery, cancellation, or returns",
                    "not_for": "Charges or account access",
                    "examples": ["Where is my order?", "Cancel my shipment"],
                },
                "account": {
                    "what": "Login, profile, permissions, or security",
                    "not_for": "Charges or order tracking",
                    "examples": ["Reset my password", "I cannot sign in"],
                },
            },
        ),
        "requests_credentials": Noul(
            instructions={
                "question": "Does the message request a sensitive credential?",
                "compare": [
                    "`ticket.message`",
                    "`policy.sensitive_credentials`",
                ],
                "focus": "Look for a request to disclose the credential itself.",
            },
            criteria=NoulCriteria(
                true={
                    "what": "Asks the recipient to disclose a listed credential",
                    "examples": [
                        "Reply with your password",
                        "Send us your API key",
                    ],
                },
                false={
                    "what": "Does not ask the recipient to disclose a credential",
                    "not_for": "A legitimate instruction to reset a credential",
                    "examples": ["Use this link to reset your password"],
                },
            ),
        ),
        "sender_identity_mismatch": Noul(
            instructions={
                "question": "Does the claimed sender identity conflict with its domain?",
                "compare": [
                    "`ticket.sender.display_name`",
                    "`ticket.sender.email`",
                ],
                "focus": "Compare the named organization with the email domain.",
            },
            criteria=NoulCriteria(
                true={
                    "what": "Claims an organization unrelated to the email domain",
                    "examples": ["Acme Payroll sent from claim-bonus.example"],
                },
                false={
                    "what": "The identity and domain agree or make no conflicting claim",
                    "examples": ["Acme Payroll sent from acme.example"],
                },
            ),
        ),
        "unexpected_reward": Noul(
            instructions={
                "question": "Does the message announce an unexpected reward?",
                "inspect": "`ticket.message`",
                "focus": "Look for an unsolicited prize, payment, or reward claim.",
            },
            criteria=NoulCriteria(
                true={
                    "what": "Announces an unrequested prize, payment, or reward",
                    "examples": ["You were selected for a $1,000 bonus"],
                },
                false={
                    "what": "Contains no reward claim or discusses an expected payment",
                    "not_for": "A customer asking about a known refund or payroll deposit",
                    "examples": ["When will my approved refund arrive?"],
                },
            ),
        ),
        "refund_requested": Noul(
            instructions={
                "question": "Does the customer explicitly request a refund or credit?",
                "inspect": "`ticket.message`",
                "focus": "Require a requested remedy, not a billing complaint alone.",
            },
            criteria=NoulCriteria(
                true={
                    "what": "Directly asks for money back or an account credit",
                    "examples": ["Please refund the duplicate charge"],
                },
                false={
                    "what": "Does not ask for a refund or credit",
                    "not_for": "A complaint or billing question without a requested remedy",
                    "examples": ["Why was I charged twice?"],
                },
            ),
        ),
        "mentions_open_order": Noul(
            instructions={
                "question": "Does the message refer to a supplied open order?",
                "compare": [
                    "`ticket.message`",
                    "`customer.open_orders`",
                ],
                "focus": "Match an order id or other identifying details.",
            },
            criteria=NoulCriteria(
                true={
                    "what": "Refers to an open order by id or identifying details",
                    "examples": ["Where is order A-104?"],
                },
                false={
                    "what": "Does not identify any supplied open order",
                    "not_for": "A generic order question with no matching details",
                    "examples": ["How long does shipping usually take?"],
                },
            ),
        ),
        "frustration": Score(
            instructions={
                "question": "How frustrated does the customer appear?",
                "inspect": "`ticket.message`",
                "focus": "Judge expressed frustration, not issue severity.",
            },
            criteria=[
                {
                    "what": "Calm and matter-of-fact",
                    "signals": ["Neutral wording", "No complaint about the experience"],
                },
                {
                    "what": "Frustrated but civil",
                    "signals": ["Expresses annoyance", "Remains constructive"],
                },
                {
                    "what": "Very angry or threatening to leave",
                    "signals": ["Hostile language", "Threatens cancellation or churn"],
                },
            ],
        ),
    }

    with TypeSafeClient() as client:
        response = client.system_one(
            state=state,
            questions=questions,
        )

    # Compose independent spam signals with weights controlled by code.
    answers = response.answers
    spam_risk = (
        0.45 * answers["requests_credentials"].noul
        + 0.30 * answers["sender_identity_mismatch"].noul
        + 0.25 * answers["unexpected_reward"].noul
    )

    # Escalate uncertain judgments instead of guessing.
    spam_is_uncertain = 0.4 < spam_risk < 0.6
    if spam_is_uncertain or answers["topic"].confidence < 0.75:
        return route_to_human_review(ticket)
    if spam_risk >= 0.6:
        return quarantine_as_spam(ticket)

    # Let code decide which speculative answers matter on this path.
    if answers["topic"].choice == "billing":
        return route_to_billing(
            ticket,
            refund_requested=answers["refund_requested"].noul >= 0.7,
        )
    if answers["topic"].choice == "orders":
        return route_to_orders(
            ticket,
            mentions_open_order=answers["mentions_open_order"].noul >= 0.7,
        )

    priority = (
        "high"
        if answers["frustration"].confidence >= 0.7
        and answers["frustration"].score >= 1.5
        else "normal"
    )
    return route_to_account_support(ticket, priority=priority)
```

(source: concepts/how-to-build-with-system-one.md, `triage_ticket.py`)
