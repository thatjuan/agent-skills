---
name: council
description: Adversarially improve anything (a design, writing, code, a plan, a prompt) with a council of Orca agents on models the user names, who score and critique each revision until every member rates it at least 9/10. Use when the user asks for a council, an adversarial critique-and-revise loop, or to iterate on something until reviewers agree it is a 9 out of 10.
---

# Council

You are the **author**. A **council** of Orca workers, one per model the user names, are your critics. Each round, every member scores the current version against a fixed **rubric** and writes a **verdict**; you triage the verdicts, revise, and convene the next round. The work is done when every member scores the same version at or above the **bar** (default 9/10, or the one the user sets).

Members only critique. You alone change the artifact, so it keeps one coherent hand and every change is traceable to a critique.

## Load Orca

Invoke the `orchestration` skill, resolve the Orca executable it describes, and load its version-matched guide; it is the single source of truth for command syntax, waking, `send`, and release. Running this skill is the user's request for supervision, so you are the coordinator. `ORCA status --json` must succeed first; if orchestration commands are rejected as disabled, tell the user to enable it under Orca Settings → Experimental and stop.

## Seat the council

1. **Models.** Seat one member per model named in the prompt; a model named twice seats two members. When the prompt names no models, ask which models sit on the council, in the same message as any priority questions (step 4), and wait for the answer before anything else.
2. **Agents.** Map each model to the Orca agent that serves it (Claude models → `claude`, OpenAI models → `codex`; the rest from the `--agent` list in `ORCA orchestration worker-start --help`) and pass its provider model id with `--model`. Pass `--effort` only when the user names one.
3. **Artifact.** Identify what is being improved and how a member will see it (**Evidence**). When the prompt asks for something that does not exist yet, make the first version yourself; that is round 1.
4. **Priorities.** Settle the priorities a fair score rests on: which quality wins when two conflict, the properties the work must have, and the conditions it is judged under (the audience, where it ships, what it competes with). Take them from the prompt first, then enrich them toward a better result: add what a demanding expert in this kind of work would also hold it to, and lift each stated priority to the standard the goal implies (a launch post that should be "clear" should also make a skeptical reader want to try the thing). Enrichment sharpens the user's priorities and never overrides one. Ask the user only when a priority is still unclear, meaning two reasonable readings would produce different rubrics: then ask 1–3 questions, each saying what its answer changes, and wait for the answers. When the priorities are clear, ask nothing.
5. **Rubric.** Write 4–7 criteria drawn from the user's goal, the audience, the priorities, and the artifact's kind, and for each one what a 10 looks like. Add these anchors for the overall score: 10 is the best example of its kind you have seen; 9 would ship to a demanding expert audience with nothing worth changing; 7 is competent and forgettable; 5 has a problem a user would notice. The rubric is fixed for the whole council, so every round is scored against the same goalposts.
6. **Record.** Create `.council/<slug>/` at the workspace root and add `.council/` to `.git/info/exclude`. Write the rubric to `rubric.md` there, headed by the priorities, each marked as stated by the user, added by the council, or answered by the user. Name each member after its model (`opus`, `gpt-5-5`, with `-2` for a repeat).
7. Show the user the members (model and agent), the priorities the council added, the rubric, the bar, and the round cap (default 6), then start.

## Evidence

Each round lives in `.council/<slug>/round-<n>/`, holding a pinned copy of the version under review so members judge exactly what you judged, even while you keep editing.

| Artifact               | What goes in the round directory                                                                                         |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Design, UI, a page     | Screenshots of every screen and state in scope, at phone and desktop widths, light and dark when both exist, plus the URL |
| Writing                | A copy of the text, and where it will be published                                                                       |
| Code                   | The diff against the starting point, and the commands that build and test it                                             |
| Anything else          | Whatever a demanding reviewer would ask to see before scoring it                                                         |

Members score the current version on its own merits. The previous round's directory is there to catch regressions, never to grade improvement.

## Member spec

Start every member in the same turn with `worker-start --worktree current --agent <agent> --model <id> --task-title "council: <member>" --spec-file .council/<slug>/spec-<member>.md`, then end your turn. Each spec carries:

- The user's goal, the audience, and any constraints, in the user's words, plus the priorities in `rubric.md`.
- The rubric file and the round directory to judge.
- The verdict to write to `round-<n>/<member>.md`:
  - **Score**: the overall score and one per criterion, each a whole number with a one-line reason.
  - **Blocking**: anything that by itself keeps the work below a 9.
  - **Changes**: ranked by impact, each naming the place in the artifact, the problem, and a concrete fix.
  - **Keep**: what works and must survive revision.
  - **Weakest point**: at a 9 or above, the one thing still most worth changing.
- The stance: you are a relentless, adversarial critic, judging as the most demanding member of the audience would. Every claim points at a specific place in the artifact. A score moves only when the artifact changes: a raised or lowered score names the change that moved it.
- Read the artifact and your own earlier verdicts; leave other members' verdicts unread until the change log quotes them. Edit nothing but your verdict file.
- Finish each round with `worker_done`, its summary holding your overall score and the path of your verdict.

Members learn the rubric and the anchors, never the bar or the round cap. A critic who knows the pass mark scores toward it.

## Run the rounds

Orca wakes you as members report. Once every member has reported:

1. **Tally.** Record each member's overall score for the round in `.council/<slug>/scores.md`.
2. **Pass check.** The council passes when every member scored this round's version at or above the bar and no Blocking item is open. On a pass, go to **Finish**.
3. **Triage** every Blocking item and Change into one disposition, written to `round-<n>/changelog.md` with the member it came from:
   - **Accept**: you will make the change.
   - **Reject**: it conflicts with the user's goal, the rubric, or another member's stronger point. State the reason on substance; the member may contest it.
   - **Escalate**: a taste call that belongs to the user, or two members deadlocked on opposite demands with equal support in the rubric. Ask the user and wait.

   Weigh critiques on their merit against the rubric. Two members agreeing does not make a point right, and a lone dissent can be the best note in the round.
4. **Revise.** Make every accepted change, protecting each member's Keep list. Verify the result the way the artifact demands (rebuild and screenshot a design, run the tests on code, reread prose end to end).
5. **Convene** round n+1: pin the new version in `round-<n+1>/`, then `send` each member the new round directory and the change log, asking for a fresh verdict. End your turn.

**Stop early** and report to the user when the round cap is reached, or when the lowest score has not risen for two rounds in a row. Report each member's last score, the open Blocking items, and the dispute keeping the council apart, then ask how to proceed: another round, a ruling from the user, or stop here.

## Finish

The improved artifact is in place where it started. Release every member as the orchestration guide describes, and confirm `worker-list --run <run_id> --terminal-state reclaimable --json` returns none.

Report to the user:

- The final score from each member, and how many rounds it took.
- The changes that moved the scores most, one line each.
- Critiques you rejected that a member still contested, with your reason.
- Where the record lives (`.council/<slug>/`), and that you will delete it unless they want to keep it.
