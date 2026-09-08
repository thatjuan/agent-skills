# batch-implement

`batch-implement` works through every issue in a batch or GitHub milestone one at a time. The coordinator creates a fresh subagent for each issue and keeps each agent's intermediate output out of its context.

Before work starts, the skill asks which available model should implement the issues, or whether the coordinator should choose automatically. It also asks how to deliver the work:

- One feature branch and one pull request for the whole batch.
- One feature branch and one pull request per issue.

The skill is self-contained and does not invoke other skills or orchestration workflows.

## Install

```bash
npx skills add thatjuan/agent-skills --skill batch-implement
```
