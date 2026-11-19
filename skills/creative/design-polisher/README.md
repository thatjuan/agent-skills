# design-polisher

> Reviews an existing UI as a top-tier designer and files the polish as detailed GitHub issues, each with reference samples an implementer can execute.

## What it does

`design-polisher` looks at the interface you already have and raises its craft: typography, spacing, color, hierarchy, depth, motion, and state design. It runs the product, captures each screen in scope, reads the styling code behind it, and decides on a set of changes with exact values.

It then hands those proposals to [`capture-issues`](../../engineering/capture-issues/), which files them under one milestone. Each issue carries the design intent, the files affected, current and target values, links to real products that do the same thing well, a snippet in the project's own stack, and acceptance criteria a reviewer can check against a screenshot.

The product keeps its identity, layout, and features. The skill polishes; it does not redesign.

## When to use it

- *"Polish the main UI of this app and file issues for it."*
- *"Take the settings screens to the next level of design quality."*
- *"The onboarding flow works but looks flat. Refine it."*
- *"Review our dashboard as a designer and write up what to fix."*

**Not the right skill if** you want a new visual direction (→ [`creative-director`](../creative-director/)), a new screen designed from nothing, or issues from a written spec with no design review (→ [`capture-issues`](../../engineering/capture-issues/)).

## Example walkthrough

**Prompt**

> Polish the inbox and message view of our mail client.

**What the skill does**

1. **Scope.** Lists the screens and states: inbox list, message view, empty inbox, loading, selection, both themes.
2. **See the UI.** Runs the app, screenshots each one, then reads the theme tokens and the list and message components.
3. **Propose.** Settles on changes with exact values, favoring token-level fixes.
4. **File.** Creates a "Design polish" milestone with issues such as:

   **Tighten the inbox list's type hierarchy**
   > Sender, subject, and preview all render at 14px/400, so the eye has no entry point. Sender moves to 14px/600, subject stays 14px/400, preview drops to 13px at 60% foreground. Row height 64px to 60px.
   >
   > Reference: Linear's issue list, for the single weight step between title and metadata.
   >
   > Done when unread rows read sender-first at a glance in both themes, and read rows drop sender to 500.

## Installation

```bash
npx skills add thatjuan/agent-skills --skill design-polisher
```

It files through `capture-issues`, so install that too. Filing needs the `gh` CLI, authenticated for the repo.

## Bundled resources

| File | Purpose |
|------|---------|
| `SKILL.md` | The designer's brief, the review process, and what each issue must carry |

## Tips

- **Name the scope.** "The checkout flow" produces sharper issues than "the app".
- **Make the app runnable.** The review is of rendered screens. Tell the agent how to start the product, or supply screenshots.
- **Issues are created without a confirmation step**, as `capture-issues` does. Ask for the proposals first if you want to review them before anything is filed.
- **Say what is off limits.** Brand colors, a typeface, a layout you like: name them and the proposals work around them.
- **Hand the milestone to an implementer.** [`batch-implement`](../../engineering/batch-implement/) works through it issue by issue.

## Related skills

- [`capture-issues`](../../engineering/capture-issues/): files the issues
- [`creative-director`](../creative-director/): new concepts and visual directions
- [`batch-implement`](../../engineering/batch-implement/): implements the milestone
