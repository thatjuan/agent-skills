---
name: batch-implement
description: Implement every issue in a batch or GitHub milestone one at a time, using a fresh subagent for each issue and either one combined PR or one PR per issue.
---

# Batch implement

You are the coordinator. Work through every requested issue sequentially until the batch is complete. Create a fresh implementation subagent for each issue. You own the branches, commits, pushes, and pull requests.

This skill is self-contained. Use subagents directly. Do not invoke or depend on other skills or orchestration workflows.

## Ask first

Before starting repository work, collect these two choices. Treat a choice already stated by the user as answered and ask only what is missing. Ask both questions together when the interface supports it.

1. Ask, "What agent do you want to use for each issue?" Show `Auto` and every model currently available for subagent creation. If the user chooses a model, use it for every issue. If the user chooses `Auto`, select the best available model separately for each issue based on the work it requires.
2. Ask, "How should the work be delivered?" Show these options:
   - One feature branch for the whole batch, followed by one pull request.
   - One feature branch and one pull request per issue.

Wait for both answers before starting.

## Work through the batch

1. Resolve the complete issue list and its order. Use the user's order unless dependencies require another order.
2. Prepare the branch required by the selected delivery strategy.
3. Read the current issue in full, including its title, body, comments, acceptance criteria, and linked instructions.
4. Create a fresh subagent for that issue with the selected model. Give it the full issue instructions and enough repository and branch context to execute without guessing. Its scope is the current issue only.
5. Tell the subagent to implement the issue and run appropriate validation. It must not change branches or open a pull request.
6. Keep the coordinator's context clean. The subagent must send no reasoning, code excerpts, command output, or progress updates. It returns once, after finishing, with only:
   - A success or blocked verdict.
   - Short highlights of what it accomplished.
   - Validation results.
   - Notes the coordinator needs to know.
7. Wait for the final verdict. Do not start another issue until the current issue succeeds. If the subagent needs missing context, provide it and let the subagent finish.
8. Commit the completed issue, then create a fresh subagent for the next issue.

## Deliver

For a single feature branch, keep every completed issue on that branch. After all issues succeed, push the branch and open one pull request covering the whole batch.

For separate branches, push and open the current issue's pull request before starting the next issue on its own feature branch.

Finish with a concise list of issue outcomes and pull request links.
