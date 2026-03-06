---
name: team-executor
description: Orchestrates a team of AI expert agents to plan and execute any goal, task, project, or feature from a braindump description. Use this skill whenever the user describes something they want built, accomplished, or executed — especially multi-step projects, feature requests, software development tasks, creative projects, research goals, or any ambiguous braindump of ideas that needs to be organized and acted upon. Triggers on phrases like "build this", "execute this", "make this happen", "here's what I need", "plan and build", or any substantial description of desired outcomes. Also use when the user pastes a braindump of ideas, goals, or requirements and wants them turned into reality. This skill assembles expert teams, creates detailed plans, and then executes them to completion autonomously.
---

# Team Executor

An autonomous multi-agent orchestration skill that transforms braindumps into executed results through two phases: expert planning and autonomous execution.

## Overview

This skill operates in two distinct phases:

**Phase 1 — Planning**: Organizes raw input, assembles a team of expert agents, has each analyze the goal from their domain expertise, and produces a comprehensive execution plan.

**Phase 2 — Execution**: A fresh team of agents autonomously executes the plan to completion with no human intervention required.

The key philosophy: experts plan, experts execute, and the output is production-ready.

---

## Phase 1: Planning

### Step 1: Organize the Input

The user's input is likely a braindump — scattered ideas, goals, requirements, and aspirations mixed together. Your first job is to make sense of it.

Read the input carefully and produce a structured interpretation:

1. **Identify distinct goals** — separate intertwined ideas into discrete objectives
2. **Deduplicate** — merge redundant or overlapping items
3. **Fill gaps** — infer missing details that are logically necessary (flag these as inferred)
4. **Establish logical flow** — order goals by dependency and priority
5. **Clarify ambiguity** — resolve vague language into concrete, actionable descriptions

Write this organized version to `docs/plans/goal-analysis.md`. This becomes the canonical reference for all agents.

### Step 2: Scan Available Skills

Before assembling the team, scan all available skills to understand what specialized capabilities exist:

```bash
# List all available skills
find /mnt/skills -name "SKILL.md" -type f 2>/dev/null
```

Read each SKILL.md's frontmatter (name + description) to build a capability inventory. These skills may be assigned to team agents who can benefit from them. Not every agent needs a skill — only assign one when it genuinely matches the agent's role.

### Step 3: Determine If R&D Is Needed

Some goals require research before planning can begin. Look for:

- References to technologies, APIs, or tools the team may not have full context on
- Ambiguous requirements that need investigation
- Integration points with external systems
- Unfamiliar domains or specialized knowledge areas

If R&D is needed, spawn R&D agents first (see `references/agent-templates.md` for the R&D agent template). R&D agents should:

- Search the codebase and project docs for existing patterns and conventions
- Read relevant documentation and source files
- Investigate technical feasibility
- Document findings in `docs/plans/research/` as markdown files

Wait for R&D to complete before assembling the planning team, since R&D findings inform which experts are needed.

### Step 4: Assemble the Planning Team

Based on the organized goals and any R&D findings, create a team of 3–7 expert agents. Each agent needs:

1. **A specific persona** — not just a job title, but a complete expert identity with deep domain knowledge, opinions, and a point of view. See `references/agent-templates.md` for persona construction guidelines.

2. **A clear analysis mandate** — what aspect of the goal they're responsible for evaluating

3. **An optional skill assignment** — if one of the available skills matches their role, include the skill path in their prompt so they can read and use it

4. **Access to project context** — point them at relevant files, docs, and the organized goal analysis

The team composition should cover all necessary perspectives. Common patterns:

- **Software projects**: architect, backend engineer, frontend engineer, devops/infra, QA/testing strategist
- **Data projects**: data engineer, analyst, ML engineer, domain expert
- **Content/creative**: strategist, writer, editor, designer, domain expert
- **Infrastructure**: systems architect, security engineer, SRE, networking specialist
- **Mixed projects**: pull from multiple patterns as needed

Every team MUST include a **Project Lead** agent whose job is to synthesize all other agents' input into the final plan.

### Step 5: Run the Planning Team

Spawn all expert agents. Each agent receives this prompt structure (customize per agent):

```
You are [PERSONA_DESCRIPTION].

## Your Assignment

Analyze the following project goals from your area of expertise. Provide:

1. **Assessment** — your expert evaluation of the goals as they relate to your domain
2. **Approach** — the specific technical/strategic approach you recommend
3. **Steps** — detailed, ordered steps for your domain's contribution
4. **Dependencies** — what you need from other team members
5. **Risks & Mitigations** — what could go wrong in your domain and how to prevent it
6. **Quality Standards** — what "production-ready" means for your deliverables
7. **Critical Details** — things that are easy to overlook but essential to get right

## Project Goals
[INSERT contents of docs/plans/goal-analysis.md]

## Project Context
[INSERT relevant file paths, existing code structure, docs, etc.]

## Available Skill (if assigned)
Read and follow: [SKILL_PATH]

## Important
- Your output must be actionable by a coding agent — no vague advice
- Assume the executor has no context beyond what you provide
- Specify exact file paths, commands, configurations, and code patterns
- Reference existing project code/patterns when relevant
- Everything you recommend must result in production-ready output
- Do NOT include timelines, deadlines, or time estimates
```

### Step 6: Aggregate Into Execution Plan

Once all agents have reported back, the **Project Lead** agent synthesizes everything into a single execution plan. If you didn't spawn a separate Project Lead, do this synthesis yourself.

The aggregation process:

1. **Collect all agent outputs** — read every agent's analysis
2. **Resolve conflicts** — where agents disagree, choose the approach that best serves the overall goal (document the reasoning)
3. **Merge dependencies** — create a unified dependency graph
4. **Order execution** — sequence steps across all domains into a logical execution order
5. **Eliminate redundancy** — remove duplicate steps that multiple agents independently suggested
6. **Add integration points** — where work from different agents connects, add explicit integration steps

### Step 7: Software Development Review Gate

**If the project involves software development** (code, APIs, infrastructure, etc.), spawn one additional agent before finalizing:

```
You are a Principal Software Engineer with 20+ years of experience across
startups and large-scale systems. You've seen every architecture pattern
succeed and fail. You review with an eye for:

- Production readiness (error handling, logging, monitoring, graceful degradation)
- Security (input validation, auth, secrets management, OWASP top 10)
- Maintainability (clear abstractions, documentation, test coverage expectations)
- Scalability (will this approach survive 10x growth?)
- Developer experience (is this plan clear enough for an agent to execute without ambiguity?)
- Consistency with existing codebase patterns and conventions

## Your Task
Review the following execution plan. For each section:
1. Flag anything that would NOT pass a production code review
2. Add missing steps that experienced engineers would expect
3. Strengthen vague instructions with specific implementation details
4. Ensure error handling and edge cases are addressed
5. Verify the plan follows existing project patterns (check the codebase)

Be constructive but thorough. The agents executing this plan will follow it literally.

## Execution Plan
[INSERT the draft plan]

## Project Codebase
[INSERT relevant file tree and key files]
```

Incorporate this reviewer's feedback into the final plan.

### Step 8: Write the Final Plan

Write the finalized plan to `docs/plans/execution-plan.md` using this structure:

```markdown
# Execution Plan: [Project Title]

## Overview
[2-3 sentence summary of what this plan accomplishes]

## Goals
[Numbered list of concrete objectives from the goal analysis]

## Architecture / Approach
[High-level approach with key decisions and their rationale]

## Execution Steps

### Phase N: [Phase Name]

#### Step N.M: [Step Name]
**Objective**: [What this step accomplishes]
**Details**:
[Specific, detailed instructions — file paths, code patterns, configs, commands]
**Inputs**: [What this step needs]
**Outputs**: [What this step produces]
**Quality Criteria**: [How to verify this step is done correctly]

[Repeat for all steps...]

## Integration Points
[Where different components connect and how to verify integration]

## Quality Assurance
[Testing strategy, validation steps, acceptance criteria]

## Risk Register
[Known risks and their mitigations]

## File Structure
[Expected project structure after execution]
```

The plan must be:
- **Self-contained** — an agent with no prior context can execute it
- **Specific** — exact file paths, code patterns, command sequences
- **Ordered** — steps are sequenced by dependency
- **Verifiable** — each step has clear completion criteria
- **Production-grade** — the output meets professional standards
- **Timeline-free** — no dates, deadlines, or time estimates anywhere

---

## Phase 2: Execution

Phase 2 uses a completely fresh team of agents. They receive only the execution plan and project context — not the Phase 1 deliberation history. This ensures clean execution without planning-phase bias.

### Step 9: Assemble the Execution Team

Read `docs/plans/execution-plan.md` and create execution agents based on the plan's phases and steps. Each execution agent:

1. **Has a focused scope** — responsible for a specific phase or group of related steps
2. **Has a complete persona** — expert identity matching the work they'll do (see `references/agent-templates.md`)
3. **Has the right skills** — assign available skills that match their work
4. **Operates autonomously** — makes all decisions independently based on project context

The execution team prompt structure:

```
You are [PERSONA_DESCRIPTION].

## Your Mission
Execute the following steps from the project execution plan. Work autonomously
and make all decisions yourself — do not wait for or request human input.

## Decision-Making Guidelines
- Root all decisions in the existing project code, docs, and conventions
- When multiple valid approaches exist, choose the one most consistent with the codebase
- If you encounter ambiguity, choose the most production-appropriate option
- Document significant decisions as code comments or in docs/

## Steps to Execute
[INSERT relevant steps from execution-plan.md]

## Project Context
[INSERT relevant file paths, existing patterns, dependencies]

## Available Skill (if assigned)
Read and follow: [SKILL_PATH]

## Critical Requirements
- All output must be production-ready — no TODOs, no placeholders, no stubs
- Follow existing project conventions and patterns
- Include proper error handling, logging, and documentation
- Write clean, maintainable, well-commented code
- Run and verify your work before considering a step complete
- If a step depends on another agent's output, check for it and adapt as needed
```

### Step 10: Execute

Spawn all execution agents. Key principles:

1. **Parallel where possible** — agents working on independent steps can run simultaneously
2. **Sequential where necessary** — respect dependency ordering from the plan
3. **No human input** — agents make all decisions autonomously using project context
4. **Verify as you go** — each agent should validate their work (run tests, lint, verify output)

### Step 11: Integration & Verification

After all execution agents complete, perform a final integration pass:

1. **Check all outputs exist** — verify every deliverable from the plan was produced
2. **Run integration checks** — if the project has tests, run them; if it has a build, build it
3. **Verify consistency** — ensure outputs from different agents are compatible
4. **Fix integration issues** — spawn targeted agents to resolve any conflicts
5. **Final quality check** — verify the result meets the plan's quality criteria

### Step 12: Report

Write a completion report to `docs/plans/execution-report.md`:

```markdown
# Execution Report: [Project Title]

## Summary
[What was accomplished]

## Completed Steps
[List of all executed steps with status]

## Key Decisions Made
[Significant autonomous decisions and their rationale]

## Files Created/Modified
[Complete list of all changes]

## Verification Results
[Test results, build status, integration check outcomes]

## Known Limitations
[Anything that couldn't be fully resolved]

## Next Steps (if any)
[Remaining work that requires human input or was out of scope]
```

---

## Guidance for the Orchestrator

You (the agent reading this skill) are the orchestrator. Here's how to think about your role:

**You are a CTO assembling and directing a world-class team.** You don't do the detailed work yourself — you identify what expertise is needed, assemble the right people, give them clear mandates, and synthesize their output.

**Be opinionated about team composition.** Don't just create generic "developer" agents. Create "Senior React Engineer who has migrated 3 large apps from class components to hooks and has strong opinions about state management" or "Security Engineer who previously worked on OWASP tooling and thinks about threat models before writing any code."

**Rich personas produce better output.** The more specific and opinionated your agent personas are, the better their analysis and execution will be. A "backend developer" gives generic advice. A "distributed systems engineer who has debugged production outages at scale and insists on idempotent operations and circuit breakers" gives battle-tested advice.

**Read the project first.** Before assembling any team, understand what already exists. Read the project structure, key source files, existing docs, and configuration. This context is essential for creating relevant agents and realistic plans.

**Don't over-team.** 3-5 agents is often enough for planning. More agents means more synthesis work and more potential for conflicts. Only add agents when they bring a genuinely distinct perspective.

**Phase 2 gets fresh context.** This is intentional. Execution agents should follow the plan, not the messy deliberation that produced it. The plan is the interface between Phase 1 and Phase 2.
