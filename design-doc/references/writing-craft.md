# Writing Craft

A design doc is a **writing** artifact, and most fail as writing before they fail as engineering. The source is a chapter in *Refactoring English* — a book about writing well as a software engineer — so the craft is not decoration; it's half the value. Run these as a self-edit pass over every draft.

## The Governing Test: Make It Stand on Its Own

> Imagine what you'd say to a teammate or partner team before they read your design doc. Now realize that **some readers will see the doc before hearing any explanation from you.**

You will not be in the room. The doc gets forwarded, read at 11pm, reviewed by a partner team you've never met. So everything a reader needs to understand the project belongs **on the first page** — in the Objective and Background — not in your head.

**The self-test.** Hand the draft (mentally) to a competent engineer on an adjacent team who has heard nothing about the project. Can they, by the end of page one, state what you're building and why? If not, the front matter is under-written.

This single test drives most of the rules below.

## Rule 1 — Plain-Language Objective

The Objective is one sentence, readable by *any* stakeholder — including non-engineers. No internal nouns, no architecture.

- ✓ *"Improve application performance by adding a caching layer between the Trogdor web server and the Postgres database."*
- ✗ "Introduce an LRU-evicting read-through tier keyed on the Trogdor DAO hash to amortize Postgres egress." (True, maybe — but it fails the stakeholder test.)

## Rule 2 — Goals Are Outcomes, Not Implementations

State the world you want *after* launch. If a "goal" names a technology, you've probably written a solution and skipped the goal.

| ✗ Implementation-as-goal | ✓ Outcome |
|---|---|
| Add Kubernetes to our infrastructure | Minimize outages related to deploying new app versions |
| Rewrite the API in Go | Cut p99 request latency below 100ms |
| Introduce a message queue | Decouple checkout from email sending so a mail outage can't fail a purchase |

The test: ask **"what is that *for*?"** until the answer stops being a technology.

## Rule 3 — Be Measurable, Not Vague

Anything you'll be held to — especially SLOs — must be something a metric can confirm or deny.

- ✗ "Performant on mobile." (Whose phone? Which percentile? Met or not — nobody can say.)
- ✓ "Trogdor's 50th percentile latency for user-facing HTTP requests ≤ 200ms."
- ✓ "Alert when 95th percentile latency ≥ 3s."

Replace every soft adjective (*fast, scalable, reliable, performant, secure*) with a number, a percentile, and a unit — or move it out of the section that implies a promise.

## Rule 4 — Prefer Recognizable Terms; Define Inline; Glossary Last

Reader friction compounds. Three tiers, best to worst:

1. **Best** — use a term the audience already recognizes, so no definition is needed.
2. **Good** — define it **inline**, the first time it appears: "…the Trogdor DAO (the data-access layer every page renders through)…"
3. **Fallback** — put it in the Glossary. *"Defining a term in a glossary is better than not defining it at all, but the best solution is to use recognizable terms or define them inline."*

A glossary is where definitions go when inlining would clutter the prose — not the first place to send your reader.

## Rule 5 — Keep Diagrams Editable, and Link the Source

A diagram is only useful if the next person can change it.

- **Never** paste a photo of a whiteboard. *"They're stuck with that diagram forever because they can't edit the photo."*
- Use flexible editors (Excalidraw, draw.io, Google Drawings) or diagram-as-code (Mermaid, D2, Graphviz).
- *"Link to the source drawing or code so that your teammates have a way to reproduce the diagram as well."*

Diagram-as-code has a second payoff: it diffs and reviews like the rest of the doc.

## Rule 6 — Right-Size the Detail

The fastest way to ruin a design doc is to write the implementation in it.

> If you specify every possible detail in a design doc, you've essentially written the implementation during the design phase. That would defeat the whole purpose of a design doc.

Apply the **penalty-for-being-wrong** filter to *prose*, not just to decisions: if a detail is cheap to change in code later (the exact pagination size, a log field name, a button's placement), it doesn't belong here. Specify the contract and the irreversible choices; let the reversible ones be discovered in code.

## Rule 7 — Be Brief Where Brevity Is the Point

Some sections are explicitly meant to be short. The Alternatives Considered section is the archetype:

> Don't spend hours meticulously documenting every rejected design idea… All I need in the alternatives section is a few brief lines describing strong alternatives and why they didn't work.

A reader scanning Alternatives wants to confirm you considered the obvious option and see the one-line reason you passed — not read a literature review.

## Rule 8 — Name the Project Well

The Title is the first writing decision and the one people repeat most. Aim for three qualities:

- **Short** — easy to say aloud in a standup.
- **Distinctive** — unambiguous about which project it means.
- **Evocative** — conceptually represents what it does.

`RecencyBank` (a store of recently-accessed rows) hits all three. `Project Flying Silver Horse` hits none.

## General Craft (consistent with the book's philosophy)

Beyond the article's explicit rules, the surrounding *Refactoring English* philosophy carries cleanly into design docs:

- **Lead with the conclusion.** Put the decision or the point first; supporting detail after. Reviewers read top-down and bail early.
- **Cut filler words.** *Just, really, basically, actually, simply, in order to.* They add length and subtract authority.
- **Prefer concrete over abstract.** "600ms median page load" lands; "suboptimal performance" doesn't.
- **Short sentences, active voice.** "The cache invalidates on write" beats "Invalidation of the cache is performed upon the occurrence of a write."
- **One idea per paragraph.** A reviewer should be able to skim topic sentences and follow the argument.

## The Self-Edit Pass (run before circulating)

1. Page-one stand-alone test — would a cold partner-team engineer understand *what* and *why* by the end of the Background?
2. Every soft adjective in a promise-bearing section replaced with a measurable value.
3. Every "goal" re-checked: is it an outcome, or a smuggled-in implementation?
4. Every internal term: recognizable → inline → glossary, in that priority.
5. Every diagram editable and source-linked.
6. Every section re-checked against penalty-for-being-wrong: is anything here just the implementation written early?
7. Alternatives section trimmed to a few honest lines.
