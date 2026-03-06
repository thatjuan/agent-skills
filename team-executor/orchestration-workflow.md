# Orchestration Workflow Reference

Quick reference for the orchestrator on how to manage agent spawning, communication, and synthesis.

## Spawning Agents

### With Subagents (Claude Code Teams)

When subagents are available, use them for parallel execution. Each agent runs as an independent subagent with its own context.

**Planning agents** can all run in parallel since they're analyzing the same input independently.

**Execution agents** should be spawned respecting the dependency graph:
- Independent steps → parallel
- Dependent steps → sequential (wait for predecessor to complete)
- Integration steps → after all dependencies complete

### Without Subagents (Sequential Fallback)

If subagents are not available, execute agents sequentially:

1. Run each planning agent one at a time
2. Collect outputs in `docs/plans/agent-outputs/`
3. Synthesize after all planning agents complete
4. Run execution agents in dependency order

This is slower but produces the same result.

## Agent Output Collection

### Planning Phase

Each planning agent should write their output to:
```
docs/plans/agent-outputs/{agent-role}.md
```

Example:
```
docs/plans/agent-outputs/architect.md
docs/plans/agent-outputs/backend-engineer.md
docs/plans/agent-outputs/frontend-engineer.md
docs/plans/agent-outputs/security-engineer.md
docs/plans/agent-outputs/project-lead-synthesis.md
```

### Research Phase

R&D agents write to:
```
docs/plans/research/{topic}.md
```

### Execution Phase

Execution agents work directly on the codebase. They document decisions in:
```
docs/plans/execution-log/{agent-role}.md
```

## Conflict Resolution

When planning agents disagree:

1. **Identify the conflict** — what specifically do they disagree on?
2. **Check project context** — does existing code/docs favor one approach?
3. **Apply pragmatism** — which approach is simpler, more maintainable, more aligned with project conventions?
4. **Document the decision** — in the execution plan, note "Chose X over Y because Z"

Common conflicts and resolutions:
- **Architecture style**: favor what's already in the codebase
- **Technology choice**: favor what the project already uses unless there's a compelling reason to change
- **Testing strategy**: favor more coverage over less, but be practical about test pyramid
- **Security vs convenience**: security wins, but find the least inconvenient secure approach

## Prompt Assembly Checklist

Before spawning any agent, verify you've included:

- [ ] Complete persona description (not just a title)
- [ ] The organized goal analysis
- [ ] Relevant project context (file tree, key files, existing patterns)
- [ ] Skill path (if assigned)
- [ ] Specific deliverable expectations
- [ ] Quality standards
- [ ] The instruction to be specific and actionable (not vague)
- [ ] For execution agents: the "no waiting for input" directive

## Phase Transition

The handoff from Phase 1 to Phase 2 is critical:

1. **Phase 1 produces**: `docs/plans/execution-plan.md`
2. **Phase 2 reads**: only `docs/plans/execution-plan.md` + project files
3. **Phase 2 does NOT read**: agent-outputs/, research/, goal-analysis.md
4. **Why**: execution agents need clean, synthesized instructions — not the messy deliberation that produced them

## Error Handling

If an agent fails or produces poor output:

1. **Check the prompt** — was the persona clear? Was context sufficient?
2. **Retry with refinement** — adjust the prompt and try again
3. **Decompose** — break the agent's scope into smaller pieces
4. **Escalate** — if a step genuinely can't be completed, document it as a blocker

## Verification Checklist

Before declaring Phase 2 complete:

- [ ] All planned steps have been executed
- [ ] Code compiles / builds without errors
- [ ] Tests pass (or are written and passing)
- [ ] No placeholder code (TODOs, stubs, "implement later")
- [ ] Documentation is updated
- [ ] Integration points are verified
- [ ] Execution report is written to `docs/plans/execution-report.md`
