# capture-issues

`capture-issues` converts a braindump, doc, spec, or conversation into GitHub issues in the current repo.

It optimizes for two things:

- **Fewer, larger issues.** One issue per coherent unit of work, grouped under milestones when the input spans several themes.
- **Detail the implementer can act on.** Issues are written for coding agents that never saw the originating conversation, so each one carries the intended architecture, the files to touch, signatures and data shapes, examples, edge cases, and acceptance criteria.

Issue bodies are drafted with the highest-capability model available and created directly, with no confirmation step.

## Install

```bash
npx skills add thatjuan/agent-skills --skill capture-issues
```
