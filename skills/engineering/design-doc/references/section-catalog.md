# Section Catalog

Every section the article defines, grouped into six clusters. **This is a menu, not a mandate** — *"You generally don't need every single section for every doc. Choose the subset that makes sense for you."* For each section: its **purpose**, the **questions it answers**, a **good vs bad** illustration, and **include when**.

The article's ordering is preserved within clusters; a real doc presents sections roughly top-to-bottom in this order, so a cold reader is oriented before reaching the design.

---

## Cluster A — Front Matter (orient a cold reader)

### Title
**Purpose.** Name the project so people can refer to it. A good title is **short** (easy to say aloud), **distinctive** (makes clear which project it refers to), and **evocative** (conceptually represents the project).
**Good vs bad.** `RecencyBank` (short, distinctive, evokes a store of recently-used data) ✓ — `Project Flying Silver Horse` (long, nonsensical, says nothing) ✗.
**Include when.** Always.

### Metadata
**Purpose.** Make the doc locatable and attributable.
**Answers.** Who owns this? When was it written? Where is the canonical copy?
**Contents.** Author name **and email**, creation date, and an authoritative URL — *especially* if your org has shortlink redirects like `http://go/recency-bank`.
**Include when.** Always.

### Objective
**Purpose.** State the project's purpose in **one sentence**, in plain language any stakeholder understands.
**Good.** *"Improve application performance by adding a caching layer between the Trogdor web server and the Postgres database."*
**Include when.** Always. If you can't write the one-sentence objective, you're not ready to write the rest.

### Background
**Purpose.** Give the context and motivation a reader needs to evaluate the rest. This is where you defeat the most common failure — assuming shared context.
**Answers.** Why is the team taking this on? What problem does it solve? Were there previous attempts?
**Good.** *"When we launched the Trogdor web app in 2023, pages typically loaded in 100ms or less. After three years, median page loads have ballooned to 600ms… 95% of database lookups are for the same 3% of database rows."* — concrete, quantified, and it makes the proposed solution feel inevitable.
**Guiding rule.** *"Imagine what you'd say to a teammate or partner team before they read your design doc. Whatever they need to understand should be on the first page of your doc."*
**Include when.** Almost always.

### Related Documents
**Purpose.** Connect the reader to the surrounding paper trail.
**Contents.** PM or testing documents (test plans, functional specs), design docs for related systems, design docs for previous iterations.
**Include when.** There are relevant adjacent documents — usually on larger or cross-team projects.

### Glossary
**Purpose.** Define unfamiliar terms — especially internal tool and system names.
**Best practice.** *"When possible, use terms that your audience recognizes without having to refer to a glossary. Defining a term in a glossary is better than not defining it at all, but the best solution is to use recognizable terms or define them inline."* A glossary is the fallback, not the first move.
**Include when.** The doc unavoidably leans on internal jargon a partner-team reader won't know.

---

## Cluster B — Scope (the contract with your readers)

### Goals
**Purpose.** Describe the world **after** implementation — outcomes, not implementation.
**Good vs bad.** *"Minimize outages related to deploying new app versions"* ✓ (an outcome) — *"Add Kubernetes to our infrastructure"* ✗ (an implementation detail masquerading as a goal). The fix is to ask what the implementation is *for*.
**Include when.** Almost always — goals plus non-goals are the spine of the doc.

### Non-Goals
**Purpose.** Explicitly fence off what's out of scope, to kill assumptions a reader would otherwise make.
**Good.** *"Create a general-purpose, reusable caching system… Re-using this cache on other systems is out of scope."*
**Include when.** Almost always. The reader will *infer* scope you didn't intend; non-goals are how you stop them.

### Constraints
**Purpose.** Surface the hard limits the design must respect.
**Answers.** What constraints does budget, the client, the existing infrastructure, or a dependency impose?
**Include when.** Real external constraints shape the design space.

---

## Cluster C — The Design (how the built system behaves)

### Scenarios
**Purpose.** Paint how the finished system works in real-world practice — concrete, step-by-step user (or caller) workflows.
**Good.** *"Bob creates a custom report in his KeyMetrics dashboard. Bob navigates to the menu bar and clicks 'Share > as URL.' Bob emails the URL to his teammate, Charlie. Charlie clicks the link and sees an exact copy of Bob's report in read-only mode."* — named actors, concrete clicks, an observable end state.
**Include when.** The system has meaningful user- or caller-facing workflows. Scenarios are often the fastest way for a reviewer to catch a misunderstood requirement.

### Diagrams
**Purpose.** Show structure words struggle with.
**Show.** How data flows through the system; how components fit together; how the system interacts with its dependencies and clients; communication protocols.
**Rule — keep them editable.** Use flexible tools (Excalidraw, draw.io, Google Drawings) or diagram-as-code (Mermaid, D2, Graphviz). **Never** paste a photo of a whiteboard — *"they're stuck with that diagram forever because they can't edit the photo."* *"Link to the source drawing or code so that your teammates have a way to reproduce the diagram as well."*
**Include when.** The architecture, data flow, or component interaction is non-trivial.

### Interfaces
**Purpose.** Define how people or other systems interact with the project.
**By interface type.** Graphical → a UI sketch (sketch-level, not pixel-perfect). Software → the API or CLI semantics. File-based → the file format.
**Good.** A before/after of a Go type — `type Server struct { db PostgresDB }` evolving to depend on a `Store` interface (`type Server struct { db store.Store }`) — to show the dependency-injection seam the cache plugs into. Specify the *contract*, not every method body.
**Include when.** Anything else depends on this system's surface — almost always for services and libraries.

### Dependencies & Infrastructure
**Purpose.** Pin down what the system runs on and leans on.
**Answers.** What programming language(s)? On what hardware/service does the code run? Where does persistent data live?
**Strategic rule.** Spend your analysis on the dependencies that are **hard to change** later (language, storage backend) and don't agonize over the ones that *"you can replace in an afternoon"* (e.g. a third-party email provider).
**Include when.** Almost always — these are typically high-penalty-for-being-wrong choices.

---

## Cluster D — Operability (running it in production)

### Service Level Objectives (SLOs)
**Purpose.** State the measurable promises you make to clients or users.
**Typical axes.** Uptime/availability (% of time available), latency (how fast requests complete), scale (volume handled).
**Good vs bad.** *"Trogdor's 50th percentile latency for user-facing HTTP requests: ≤ 200ms"* ✓ — *"Performant on mobile"* ✗ (unmeasurable; nobody can tell if it's met).
**Include when.** The system makes availability/latency/scale promises — most user-facing services.

### Monitoring & Alerting
**Purpose.** Define how you'll know, in production, whether the SLOs hold.
**Answers.** If the service goes down, how do you find out? If performance degrades 100×, how do you know? What other events should page someone?
**Good.** *"Alert when Trogdor's 95th percentile latency for user-facing HTTP requests ≥ 3s."*
**Include when.** You set SLOs — monitoring is how you keep them honest.

### Logging
**Purpose.** Decide what the running system records.
**Answers.** What critical events get logged? Are there log levels? Where are logs stored? How long are they retained? Who can access them? **What sensitive data must be kept *out* of logs?**
**Include when.** Operability or auditing matters, or sensitive data could leak into logs.

### Timeline
**Purpose.** Break the project into milestones with stakeholder deliverable dates.
**Rule.** Choose milestones that *"create useful artifacts for stakeholders."* E.g. ship a UI on **dummy data** before the production plumbing — *"If it turns out you misunderstood the client's requirements, fake data lets you find out early."*
**Include when.** The project is large enough that sequencing and early de-risking matter.

---

## Cluster E — Risk & Compliance

### Security
**Purpose.** Make threats a design-time concern, not a post-launch scramble.
**Answers.** What threats did you consider? What is the attack surface? What are the trust boundaries?
**Rule.** Document your rationale *even when threats seem unlikely* — *"your explanation might prompt reviewers to identify threats you overlooked."*
**Include when.** Almost always for anything networked, multi-tenant, or handling untrusted input.

### Privacy
**Purpose.** Account for sensitive data end to end.
**Answers.** What sensitive data does the system handle? How long is it retained? Who has access? How is it protected (encryption, access controls)?
**Include when.** The system touches personal or sensitive data.

### Legal
**Purpose.** Surface regulatory and contractual obligations.
**Contents.** Regulatory compliance, contractual obligations, and — if relevant — open-source **license choices and the rationale** for them.
**Include when.** Compliance, contracts, or licensing are in play.

---

## Cluster F — Living Sections (track the unknowns)

### Open Issues
**Purpose.** Document what's still unresolved, so it's visible rather than forgotten.
**Each entry answers.** What is the problem? What options exist to resolve it? What is the immediate next step?
**Good next step.** *"Ask our tech lead to weigh in."* — concrete and assignable, not "TBD."
**Include when.** Anything material is still undecided (it usually is, early on).

### Resolved Issues
**Purpose.** Preserve the history of decisions once made.
**Rule.** When an open issue is resolved, **move** it here with the full discussion retained for posterity — future readers (and future you) will ask "why did we decide this?"
**Include when.** Open issues have been resolved.

### Alternatives Considered
**Purpose.** Show the strong roads not taken, and why.
**Rule — be brief.** *"Don't spend hours meticulously documenting every rejected design idea… All I need in the alternatives section is a few brief lines describing strong alternatives and why they didn't work."*
**Include when.** Almost always — it's how reviewers see that you considered the obvious option they're about to suggest.

---

## Right-Sizing the Subset

Two quick heuristics for choosing sections:

- **Penalty-for-being-wrong.** A section earns its place when it documents a decision that's costly to reverse. If getting it wrong costs an afternoon, cut it.
- **Reader-need.** A section earns its place when a cold reader or reviewer genuinely needs it to evaluate or build the system. Ceremony for its own sake is over-writing.

Example subsets:

| Project shape | Likely sections |
|---------------|-----------------|
| Small internal tool, one author, weeks of work | Objective · Background · Goals · Non-goals · Interfaces · Alternatives |
| User-facing service, one team, months of work | Front matter · Goals/Non-goals · Scenarios · Diagrams · Interfaces · Dependencies · SLOs · Monitoring · Open issues · Alternatives |
| Multi-year platform, cross-team, handles PII | Nearly all of them, with real depth in Security, Privacy, Legal, SLOs, and Constraints |
