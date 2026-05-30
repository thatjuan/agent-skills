# Domain Standards

Per-domain engineering standards layered on top of the eight standards in `engineering-principles.md`. An agent reads the section matching the layer it is building in. These were distilled from a set of expert personas and reframed as standards a single coding agent applies to its own work — not as identities to role-play.

## Table of Contents

- [Architecture Standards](#architecture-standards)
- [Backend Standards](#backend-standards)
- [Frontend Standards](#frontend-standards)
- [Data Standards](#data-standards)
- [DevOps / Infrastructure Standards](#devops--infrastructure-standards)
- [Security Standards](#security-standards)
- [Testing / QA Standards](#testing--qa-standards)
- [Production-Readiness Baseline](#production-readiness-baseline)

---

## Architecture Standards

Architecture is decided in layers: data model first, then domain logic, then interfaces, then infrastructure. The right abstraction boundaries matter more than the right technology choices.

- **Separate concerns cleanly.** Each component has one job and an explicit interface to its neighbors.
- **Model the domain, not the UI or the wire format.** Data models reflect what the system *is*, not how one screen happens to render it or how one API happens to serialize it.
- **Make operations idempotent where possible.** Re-running a step should be safe.
- **Prefer config-driven behavior over hard-coded logic** where the behavior is expected to vary.
- **Choose graceful degradation over hard failure.** Identify extension points and likely evolution paths, and structure so the system can evolve without a rewrite.
- **Resist both over-engineering and "we'll refactor later."** Build what is needed now, structured so it can grow. Decide build-vs-buy deliberately: reach for an existing, well-supported tool over a bespoke one unless the bespoke version is genuinely warranted.

## Backend Standards

- **APIs are versioned contracts.** Design them deliberately, version them, document them. A breaking change to a contract is a breaking change to every consumer.
- **The database schema is the foundation.** Get it right early; it is the most expensive thing to change later.
- **Validate input at the boundary and trust nothing from outside.** Whitelist over blacklist; parameterize every query.
- **Every external call can fail.** Wrap them with timeouts, retries, and circuit breakers. Network calls without a failure plan are incidents waiting to happen.
- **Transactions are atomic.** Partial success is often worse than clean failure — structure related writes so they commit together or not at all.
- **Migrations are reversible and safe on live systems.** No migration assumes downtime or a clean slate unless that is explicitly guaranteed.
- **Logging and observability are features, not afterthoughts.** Think in failure modes first, happy paths second: data consistency, race conditions, connection pooling, query cost, and caching strategy are part of the design, not a later pass.

## Frontend Standards

- **Every view works on mobile and desktop.** Responsive is the default, not a follow-up ticket.
- **Markup is accessible** — semantic HTML, ARIA labels where needed, full keyboard navigation, sensible focus management.
- **Respect performance budgets** — lazy loading, code splitting, optimized assets. The happy path is roughly 60% of the work.
- **Type safety on, strict mode.** Components are composable, testable, and reusable rather than monolithic.
- **Handle every UI state**: loading, empty, error, and partial — not just the populated success case.
- **Use error boundaries so a failure degrades gracefully** instead of blanking the screen.
- **Design for the edge cases users actually hit**: slow networks, stale caches, concurrent tabs, the browser back button, and deep links.

## Data Standards

- **Schema-first.** Define data contracts before writing pipelines; a pipeline against an undefined schema produces undefined results.
- **Processing is idempotent.** Every pipeline can safely re-run without double-counting or corrupting state.
- **Validate at every boundary.** Bad data in means bad decisions out — catch it at ingestion, not in the dashboard.
- **Observability for data**: freshness, row counts, and schema-drift alerts. Know when a feed goes stale before a stakeholder does.
- **Backfill capability is built in.** Any pipeline can reprocess historical data deterministically.
- **Every dataset has an owner, a description, and an SLA.** Think explicitly about partitioning, incremental vs full loads, slowly-changing dimensions, and deduplication — and about the difference between "eventually consistent" and "actually broken."

## DevOps / Infrastructure Standards

- **Infrastructure is code.** No manual console configuration that can't be reproduced from a repo.
- **Environment parity.** Dev, staging, and production are as identical as practical; "works on staging" should mean something.
- **Secrets are managed** in a vault or environment, rotatable, and never committed, logged, or baked into images.
- **Health checks and readiness probes for every service.**
- **CI runs the tests** — unit, integration, and smoke — before anything ships.
- **Deployments are boring and reversible.** Prefer blue/green or canary over big-bang; a rollback is one command.
- **Monitoring and alerting catch problems before users do**, and disaster recovery is real: backups exist, restore procedures are tested, runbooks are written. The governing questions are always "what happens when this fails?" and "how do we roll back?"

## Security Standards

Threats before features. Approach each surface by asking "how would I break this?"

- **Authentication** uses strong, standard protocols (OAuth 2.0, OIDC). No custom crypto, ever.
- **Authorization** enforces least privilege via role-based or attribute-based access control. Check authz on every protected action, not just at the front door.
- **Input validation**: whitelist over blacklist, parameterized queries, never `eval()` untrusted input. The OWASP Top 10 is addressed systematically for every web-facing component.
- **Secrets** live in a vault or environment, are rotatable, and are never logged or committed.
- **Data protection**: encryption at rest and in transit, deliberate PII handling, defined retention policies.
- **Dependencies** are pinned, vulnerability-scanned, and kept to a minimal surface area.
- **Audit logging** records who did what, when, and from where. Security findings come with concrete mitigations, not vague warnings.

## Testing / QA Standards

Design a testing approach that catches real bugs while staying maintainable and fast — don't just write tests.

- **Follow the test pyramid**: many unit tests, fewer integration tests, minimal end-to-end. Inverting it produces a slow, flaky suite.
- **Test behavior, not implementation.** A test coupled to internals breaks on every refactor and protects nothing. A good test suite is the best spec a project has.
- **Cover edge cases and error paths**, not only happy paths.
- **Flaky tests are worse than no tests** — they erode trust in the whole suite. Fix or delete them.
- **Performance testing for anything user-facing; security testing for anything that handles user data.**
- **Acceptance criteria are objectively verifiable**, with defined fixtures and test-environment requirements.

## Production-Readiness Baseline

Independent of layer, code is not production-ready until:

- **Error handling is deliberate.** Every failure path is considered; errors carry enough context (correlation IDs, structured fields) to diagnose without a repro.
- **Logging is structured**, at appropriate levels, and never leaks secrets or PII.
- **Observability exists**: the system exposes the metrics, logs, and traces needed to answer "is it healthy?" and "why did that request fail?"
- **Graceful degradation is designed in.** A dependency being slow or down degrades the experience rather than taking the whole system with it.
- **No placeholders, TODOs, or stubs** ship. Every path is complete, and the change has been run and verified — not just written.
