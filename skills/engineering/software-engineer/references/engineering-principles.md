# Engineering Principles

The eight non-negotiable standards that define the engineering quality bar, with the diagnostic questions, preferred remedies, and anti-patterns that operationalize them.

These were distilled from a brutal, "thermo-nuclear" code-**review** standard, then **inverted** to apply at design and authoring time. Each principle is written twice: an **Authoring frame** (build it this way from the start) and a **Review frame** (catch it on the finished diff). The authoring frame is the point — the cheapest place to fix a structural problem is before it is written. The review frame is the same bar, run against your own diff as a definition-of-done.

## Table of Contents

- [The Eight Standards](#the-eight-standards)
  - [1. Be Ambitious About Structural Simplification](#1-be-ambitious-about-structural-simplification)
  - [2. Respect The ~1000-Line File Boundary](#2-respect-the-1000-line-file-boundary)
  - [3. No Spaghetti Growth In Existing Code](#3-no-spaghetti-growth-in-existing-code)
  - [4. Bias To Clean Design Over Merely-Working Code](#4-bias-to-clean-design-over-merely-working-code)
  - [5. Direct, Boring, Maintainable Over Hacky Or Magical](#5-direct-boring-maintainable-over-hacky-or-magical)
  - [6. Type And Boundary Cleanliness](#6-type-and-boundary-cleanliness)
  - [7. Keep Logic In The Canonical Layer; Reuse Existing Helpers](#7-keep-logic-in-the-canonical-layer-reuse-existing-helpers)
  - [8. Atomic, Appropriately-Parallel Work](#8-atomic-appropriately-parallel-work)
- [Diagnostic Questions](#diagnostic-questions)
- [Preferred Remedies & Moves](#preferred-remedies--moves)
- [Anti-Patterns To Flag](#anti-patterns-to-flag)

---

## The Eight Standards

### 1. Be Ambitious About Structural Simplification

The highest-leverage engineering move is not writing better code — it is reframing the change so whole categories of code never need to exist. Branches, helpers, modes, conditionals, and layers that aren't written cost nothing to maintain.

Favor "code-judo" moves: changes that preserve behavior while making the implementation dramatically simpler, smaller, and more direct. **Delete complexity rather than rearrange it.** A refactor that moves complexity from one place to another without reducing it has done almost nothing.

**Authoring frame** — Before writing, ask whether the change can be framed so the complexity simply never appears. Pick the data model, the ownership boundary, or the default flow that makes the special cases evaporate. The best simplification is invisible in the diff because the complex version was never typed.

**Review frame** — On the finished diff, ask: is there a structural move that makes this dramatically simpler? If a plausible reframing would delete a whole branch, mode, or layer, the diff is not done. This is the single highest-priority finding.

### 2. Respect The ~1000-Line File Boundary

Roughly 1000 lines is a soft boundary that signals a file is carrying too much. Pushing a file from under 1k to over 1k lines is a strong smell that wants a very strong justification.

**Authoring frame** — Plan module boundaries up front. If the change you are about to make would grow a file across that line, extract the helper, subcomponent, or module *first*, then add your change to the new, focused home. Don't grow a god-file and promise to split it later.

**Review frame** — Did this diff enlarge a file past a healthy boundary? If so, the decomposition that should have happened first can happen now. A file crossing ~1000 lines without a strong reason is a presumptive blocker.

### 3. No Spaghetti Growth In Existing Code

The fastest way to rot a codebase is to bolt one more `if` onto an existing flow each time a requirement arrives. Each one is locally cheap and globally corrosive: scattered special cases, one-off branches, and mode flags accrete into logic no one can follow.

**Authoring frame** — When extending existing code, add a clean abstraction instead of another conditional. Push the new logic into a dedicated helper, state machine, policy object, dispatcher, or separate module. If you find yourself writing the second or third `if (mode === ...)` in the same function, the missing model is the real change.

**Review frame** — Be highly suspicious of new ad-hoc conditionals and one-off branches threaded into unrelated or stable flows. Repeated conditionals signal a missing model. Branching bolted into a stable path is a presumptive blocker.

### 4. Bias To Clean Design Over Merely-Working Code

"It works" is the floor, not the bar. If behavior can stay identical while the structure becomes meaningfully cleaner, write the cleaner version. Prefer removing moving pieces over spreading complexity around.

**Authoring frame** — When two implementations produce the same behavior, choose the one with fewer concepts, fewer branches, and fewer moving parts — even if it takes longer to find. Coding-agent execution removes the human-effort ceiling: the robust, clean version is the default, not a luxury.

**Review frame** — Does this change improve or worsen the local architecture? Did a cohesive module become more coupled, more stateful, or harder to scan? If the diff works but leaves the structure worse, it is not done.

### 5. Direct, Boring, Maintainable Over Hacky Or Magical

The next engineer reads this code at 2am during an incident. Write for them. Direct and boring beats clever and magical every time. Be deeply skeptical of generic mechanisms that hide a simple data-shape assumption, of thin abstractions, of identity wrappers, and of pass-through helpers that add a layer of indirection without adding clarity.

Legibility starts with names. A function, variable, or type whose name doesn't reveal what it does or holds is a defect in its own right — and if no honest name comes, the design itself is murky; fix the design, not just the label. The same goes for how callers navigate: a long `a.b().c().d()` chain couples the caller to structure it shouldn't know about — hide the walk behind one method on the first object.

**Authoring frame** — Write the boring version first. Reach for a generic mechanism only when there is real, present duplication that it collapses — not on speculation. An abstraction must earn its keep by removing more complexity than it adds. Name every new thing honestly before moving on. Prefer composition when inheritance would be refused — a subclass that ignores or overrides most of what it inherits is composition wanting to happen.

**Review frame** — Is the implementation direct and legible, or is it leaning on special cases and cleverness? Is this abstraction earning its keep, or is it a wrapper that only adds a hop? Do the names say what things do and hold? Thin abstractions, identity wrappers, mysterious names, and message chains are findings.

### 6. Type And Boundary Cleanliness

Types are where invariants live. `any`, `unknown`, needless optionality, and cast-heavy code erase the invariants the next reader needs. A silent fallback that papers over an unclear boundary turns a loud bug into a quiet one.

Two smells signal a type wanting to be born. **Primitive obsession**: a bare primitive or string standing in for a domain concept (an ID, a currency amount, an ISO code) that deserves its own small type. **Data clumps**: the same few fields or parameters travelling together through call after call — bundle them into one type and pass that.

**Authoring frame** — Prefer explicit, shared, typed models over loosely-shaped ad-hoc objects. Make the boundary explicit: if a value can be absent, model the absence; if a shape is uncertain, validate and narrow it at the boundary rather than casting past it. Don't reach for `any` to make the compiler quiet. When a domain concept or a recurring clump of fields shows up, give it a type of its own.

**Review frame** — Did this introduce casts, `any`/`unknown`, or needless optionals that obscure real invariants? Is unnecessary optionality hiding a contract that should be firm? Are primitives standing in for domain concepts, or the same parameters travelling in packs? A cast-heavy or fallback-papered boundary is a finding.

### 7. Keep Logic In The Canonical Layer; Reuse Existing Helpers

Every concept has a natural home — a package, service, module, or layer that owns it. Feature logic that leaks into shared paths, and implementation details that leak through public APIs, are how architectures drift. Bespoke one-off helpers that duplicate a canonical utility are how the same logic ends up implemented five subtly-different ways.

This applies at method scale too — **feature envy**: a method that reaches into another object's data more than its own belongs on the data it envies; move it. And it has two cohesion diagnostics at module scale: **shotgun surgery** (one logical change forces scattered edits across many files — gather what changes together into one module) and **divergent change** (one module keeps being edited for several unrelated reasons — split it so each piece changes for one reason).

**Authoring frame** — Before writing a helper, find the canonical one. Put feature logic in the package or module that already owns the concept, not in the first file you happened to open. Don't normalize architectural drift by adding to the wrong layer because it's convenient. Put each method on the object whose data it works with.

**Review frame** — Is this logic in the right file and layer? Did feature-specific logic leak into a shared module, or implementation details leak through an API? Does this duplicate an existing helper? Did one logical change scatter edits across many files, or is one file absorbing edits for unrelated reasons? Misplaced logic or a duplicated canonical utility is a presumptive blocker.

### 8. Atomic, Appropriately-Parallel Work

Two failure modes, opposite directions. **Non-atomic updates**: related changes applied half-way, leaving the system in a state that is neither old nor new — often worse than failing outright. **Needless serialization**: independent work run one-after-another for no reason when it could run together.

**Authoring frame** — Structure related updates so they apply atomically — together or not at all. Identify work with no dependency between the pieces and run it in parallel. (Don't over-index on micro-optimizations; this is about structure, not shaving milliseconds.)

**Review frame** — Is this orchestration more sequential than necessary — is independent work serialized for no reason? Are related updates left half-applied where an atomic flow belongs? Partial-update logic that reduces atomicity is a finding.

---

## Diagnostic Questions

Ask these as you design, as you write, and before you declare done. Each maps to one or more of the eight standards.

- Is there a structural move that makes this dramatically simpler? Can the change be reframed to need fewer concepts, branches, or layers?
- Does this improve or worsen the local architecture?
- Did I add branching where a better abstraction belongs?
- Did a cohesive module become more coupled, more stateful, or harder to scan?
- Is this logic in the right file and the right layer?
- Did this enlarge a file past a healthy (~1000-line) boundary?
- Are repeated conditionals signaling a missing model or helper?
- Is the implementation direct and legible, or is it leaning on special cases and cleverness?
- Is this abstraction earning its keep, or is it just a wrapper adding a hop?
- Does every new name honestly reveal what the thing does or holds — and if no honest name comes, what's murky about the design?
- Did I introduce casts, `any`/`unknown`, or ad-hoc shapes that obscure real invariants?
- Is a primitive standing in for a domain concept, or are the same few fields/params travelling together — is a type waiting to be born?
- Do callers walk long `a.b().c().d()` chains into structure they shouldn't know about?
- Does a method reach into another object's data more than its own?
- Would one logical change here force scattered edits across many files — or is one module changing for several unrelated reasons?
- Did I leak feature logic into a shared path, or implementation details across an API boundary?
- Is this orchestration more sequential, or less atomic, than it needs to be?

---

## Preferred Remedies & Moves

When a diagnostic fires, these are the moves that resolve it — ordered roughly from highest to lowest leverage.

- **Delete whole indirection layers** that don't earn their keep.
- **Reframe the state model** to eliminate conditionals — replace a chain of `if`s with a typed model or a dispatcher.
- **Change ownership boundaries** so the feature lives in its natural scope instead of leaking into shared code.
- **Simplify special cases** via a clearer default flow that absorbs them.
- **Extract pure functions and helpers** out of busy code.
- **Split large files** into focused modules along their natural seams.
- **Move feature logic behind a dedicated abstraction** — helper, state machine, policy object, module — instead of inline conditionals.
- **Separate orchestration from business logic** so each is testable and legible on its own.
- **Collapse duplicate branches** into one clearer flow.
- **Delete meaningless wrappers** and identity/pass-through helpers.
- **Reuse canonical helpers** instead of authoring near-duplicates.
- **Rename to an honest name** — and when no honest name comes, treat it as a design signal and fix the design.
- **Make type boundaries explicit** — model absence, validate-and-narrow at the edge instead of casting past it.
- **Give domain concepts their own type** — replace obsessive primitives, and bundle field/param clumps that travel together into one type.
- **Hide message chains** behind one method on the first object, so callers stop navigating internal structure.
- **Move a method onto the data it envies** instead of reaching across objects.
- **Replace refused inheritance with composition** when a subclass ignores or overrides most of what it inherits.
- **Move logic to the package or module** that already owns the concept.
- **Parallelize independent work**; **restructure related updates into atomic flows**.

---

## Anti-Patterns To Flag

In self-review, these are the smells that signal a standard was missed. They are listed roughly in priority order — structural regressions first.

- A complex implementation where a reframing would delete whole categories of complexity.
- A refactor that moves complexity around without reducing it.
- A file pushed across the ~1000-line boundary without a strong reason.
- New conditionals bolted into a stable, previously-clean path.
- One-off booleans or mode flags threaded through a flow.
- Feature logic leaking into a shared module.
- A generic "magic" mechanism hiding a simple, fixed data structure.
- Thin abstractions, identity wrappers, pass-through helpers that only add a hop.
- `any`/`unknown`, casts, and needless optionals muddying a contract.
- A name that hides what a function, variable, or type does or holds.
- A primitive or string standing in for a domain concept that deserves its own type.
- The same few fields or params travelling together uncaptured — a data clump wanting a type.
- Long `a.b().c().d()` message chains coupling callers to structure they shouldn't know.
- A method that reaches into another object's data more than its own.
- One logical change scattered across many files, or one module edited for unrelated reasons.
- A subclass or implementer that refuses most of what it inherits.
- Copy-pasted logic that should be a shared helper.
- Niche edge-case handling crammed into an already-busy function.
- Loss of modularity even though the tests still pass.
- "Temporary" branching that will calcify into permanent debt.
- A bespoke helper duplicating a canonical utility.
- Logic placed in the wrong layer or package.
- Sequential async where a parallel structure would be clearer and faster.
- Partial-update logic that reduces atomicity.
