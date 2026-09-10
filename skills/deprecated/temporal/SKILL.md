---
name: temporal
description: Expert Temporal.io workflow orchestration for Python and TypeScript. Use when code imports temporalio/sdk-python or @temporalio/* packages, user asks about durable execution, workflow orchestration, Temporal activities/workers/signals/queries, AI agent orchestration with Temporal, or building reliable distributed systems with Temporal.
---

# Temporal Workflow Orchestration

Expert-level knowledge for building durable, reliable distributed systems with Temporal.io. Covers the Python SDK (`temporalio`), TypeScript SDK (`@temporalio/*`), core platform concepts, and AI/LLM orchestration patterns.

## References

| File | When to Read |
|------|--------------|
| [core-concepts.md](references/core-concepts.md) | Architecture, determinism, timeouts, retry policies, advanced features |
| [python-sdk.md](references/python-sdk.md) | Python workflow/activity implementation, decorators, testing, client/worker setup |
| [typescript-sdk.md](references/typescript-sdk.md) | TypeScript workflow/activity implementation, sandboxing, bundling, testing |
| [ai-patterns.md](references/ai-patterns.md) | AI agent orchestration, LLM pipelines, human-in-the-loop, framework integrations |

## Platform Overview

Temporal provides **durable execution** -- application state survives process crashes, infrastructure failures, and deployments through event-sourced replay. The platform consists of the Temporal Service (server + persistence) and application code (Workers + Clients). Workers execute Workflow and Activity code on user infrastructure; the Temporal Service coordinates task dispatch, state persistence, and timer management.

### Key Primitives

| Primitive | Role |
|-----------|------|
| **Workflow** | Deterministic orchestration function; state persisted via event history |
| **Activity** | Non-deterministic unit of work (I/O, API calls, side effects) |
| **Worker** | Process that polls a task queue, executes workflows and activities |
| **Task Queue** | Named queue routing work from service to workers |
| **Signal** | Async fire-and-forget message into a running workflow |
| **Query** | Synchronous read-only state inspection (no event history) |
| **Update** | Synchronous state mutation with return value and validation |
| **Child Workflow** | Workflow spawned by another workflow; separate event history |
| **Schedule** | Server-managed recurring workflow execution |

### Determinism Contract

Workflow code replays from event history on recovery. Every replay produces the same sequence of Commands given the same Events. Non-deterministic operations (I/O, randomness, system time, threading) belong in Activities.

| Safe in Workflows | Use Instead Of |
|-------------------|----------------|
| `workflow.now()` / `Date.now()` (sandbox-replaced) | `datetime.now()` / native `Date.now()` |
| `workflow.random()` / `Math.random()` (sandbox-replaced) | `random.random()` / native `Math.random()` |
| `workflow.uuid4()` / `uuid4()` from `@temporalio/workflow` | `uuid.uuid4()` / `crypto.randomUUID()` |
| `workflow.sleep()` / `sleep()` from `@temporalio/workflow` | `asyncio.sleep()` / `setTimeout()` |
| Activity execution | Direct network/file I/O |

### Timeout Model

| Timeout | Scope | Applies To |
|---------|-------|------------|
| Workflow Execution Timeout | Entire chain (including Continue-As-New runs) | Workflow |
| Workflow Run Timeout | Single run in the chain | Workflow |
| Workflow Task Timeout | Single SDK processing step (default: 10s) | Workflow |
| Start-to-Close Timeout | Single activity attempt | Activity |
| Schedule-to-Close Timeout | Entire activity execution including retries | Activity |
| Schedule-to-Start Timeout | Time waiting in queue before worker pickup | Activity |
| Heartbeat Timeout | Interval between heartbeats from long-running activities | Activity |

Start-to-Close Timeout is the primary mechanism for detecting worker failures and is the most important timeout to set on activities.

### Retry Policy Defaults

| Property | Default |
|----------|---------|
| Initial Interval | 1 second |
| Backoff Coefficient | 2.0 |
| Maximum Interval | 100x Initial Interval |
| Maximum Attempts | Unlimited |
| Non-Retryable Error Types | None |

Activities retry by default. Workflows do not retry by default.

## SDK Quick Reference

### Python

**Package:** `temporalio` (pip install temporalio)

```python
from temporalio import workflow, activity
from temporalio.client import Client
from temporalio.worker import Worker

@activity.defn
async def greet(name: str) -> str:
    return f"Hello, {name}!"

@workflow.defn
class GreetingWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        return await workflow.execute_activity(
            greet, name,
            start_to_close_timeout=timedelta(seconds=10),
        )

# Client
client = await Client.connect("localhost:7233")
result = await client.execute_workflow(
    GreetingWorkflow.run, "World",
    id="greeting-1", task_queue="my-queue",
)

# Worker
worker = Worker(client, task_queue="my-queue",
    workflows=[GreetingWorkflow], activities=[greet])
await worker.run()
```

**Python decorators:** `@workflow.defn`, `@workflow.run`, `@workflow.init`, `@workflow.signal`, `@workflow.query`, `@workflow.update`, `@activity.defn`

**Sandbox:** Workflow code runs in an isolated sandbox. Use `with workflow.unsafe.imports_passed_through():` for importing activity types and dataclasses.

### TypeScript

**Packages:** `@temporalio/client`, `@temporalio/worker`, `@temporalio/workflow`, `@temporalio/activity`, `@temporalio/common`

```typescript
// activities.ts
export async function greet(name: string): Promise<string> {
  return `Hello, ${name}!`;
}

// workflows.ts
import { proxyActivities } from '@temporalio/workflow';
import type * as activities from './activities';

const { greet } = proxyActivities<typeof activities>({
  startToCloseTimeout: '10s',
});

export async function greetingWorkflow(name: string): Promise<string> {
  return await greet(name);
}

// client.ts
const handle = await client.workflow.start(greetingWorkflow, {
  workflowId: 'greeting-1', taskQueue: 'my-queue', args: ['World'],
});

// worker.ts
const worker = await Worker.create({
  workflowsPath: require.resolve('./workflows'),
  activities, taskQueue: 'my-queue',
});
await worker.run();
```

**Key pattern:** Workflows import only **types** from activities (`import type * as activities`). Actual implementations are registered on the Worker. Activities are accessed via `proxyActivities<typeof activities>()`.

**Sandbox:** Workflow code is bundled with Webpack into a V8 isolate. `Math.random()`, `Date.now()`, and `setTimeout` are replaced with deterministic versions. Node.js built-ins (`fs`, `path`, `crypto`, `http`) are unavailable in workflow code.

## Pattern Selection Guide

| Scenario | Pattern | Details |
|----------|---------|---------|
| External API call, DB query, file I/O | Activity | Non-deterministic work with automatic retry |
| Orchestrate multiple steps with state | Workflow | Deterministic coordination with durable state |
| Split work across services/teams | Child Workflow | Separate event history, independent workers |
| Event history approaching 50K events | Continue-As-New | Fresh history preserving workflow identity |
| Recurring execution | Schedule | Server-managed, pausable, overlap policies |
| Wait for external input | Signal + `wait_condition`/`condition` | Durable, zero-compute waiting |
| Read workflow state externally | Query | No event history cost |
| Mutate state with response | Update | Validated, synchronous, tracked |
| Multi-step with rollback | Saga (compensation list) | Reverse compensations on failure |
| Long-running with progress | Heartbeating activity | Failure detection + resumable progress |
| External completion (human approval) | Async Activity Completion | Task token for out-of-band completion |
| AI agent loop | Workflow + LLM Activity | Durable agent state, retried LLM calls |
| Parallel AI processing | Fan-out child workflows/activities | Concurrent execution with aggregation |
| Human-in-the-loop AI | Signal/Update handlers | Durable approval gates |

## AI Orchestration Overview

Temporal is infrastructure for production AI agent systems. The core pattern: a **Workflow** maintains durable agent state and conversation history, while **Activities** handle non-deterministic LLM calls, tool invocations, and external API requests.

Key properties for AI workloads:
- Completed Activity results are persisted via event sourcing -- crash recovery replays recorded LLM responses rather than re-querying (saves cost, preserves determinism)
- Retry policies handle rate limits (429), transient failures, and API timeouts automatically
- Signals enable human-in-the-loop approval gates with zero-compute waiting
- Task Queues route inference work to GPU-equipped workers
- Conversation history stored as workflow state is automatically durable

### Framework Integrations

| Framework | Integration Type |
|-----------|-----------------|
| OpenAI Agents SDK | Custom Runner; `activity_as_tool` helper |
| Pydantic AI | `TemporalAgent` wrapper; auto-offloads I/O to Activities |
| Vercel AI SDK | `AiSDKPlugin` for Worker; wraps `generateText()` in Activities |
| Anthropic Claude API | Direct `AsyncAnthropic` client in Activities; `max_retries=0` (Temporal handles retries) |
| LangChain | Activity-wrapped chain execution |
| Model Context Protocol | Durable MCP: each tool backed by a Workflow |

### AI-Specific Configuration

LLM client libraries have built-in retry logic that conflicts with Temporal's retry management. Disable client-level retries and let Temporal handle them:

```python
# Python - Anthropic
client = AsyncAnthropic(max_retries=0)

# Python - OpenAI
client = AsyncOpenAI(max_retries=0)
```

```typescript
// TypeScript - OpenAI
const client = new OpenAI({ maxRetries: 0 });
```

Recommended retry policy for LLM activities:

```python
RetryPolicy(
    initial_interval=timedelta(seconds=1),
    backoff_coefficient=2.0,
    maximum_interval=timedelta(seconds=120),
    maximum_attempts=50,
    non_retryable_error_types=["InvalidInput", "AuthenticationError"],
)
```

Parse `Retry-After` headers from 429 responses using `next_retry_delay` on `ApplicationError` / `ApplicationFailure`.

## Development Environment

```bash
# Install Temporal CLI
brew install temporal

# Start local dev server (gRPC :7233, Web UI :8233)
temporal server start-dev

# Persistent storage between restarts
temporal server start-dev --db-filename temporal.db

# Common CLI commands
temporal workflow start --task-queue my-queue --type MyWorkflow --input '{"key":"val"}'
temporal workflow list
temporal workflow describe --workflow-id my-id
temporal workflow signal --workflow-id my-id --name my-signal --input '"data"'
temporal workflow query --workflow-id my-id --name my-query
temporal workflow cancel --workflow-id my-id
```

## Versioning Strategy

Both SDKs provide a `patched()` / `deprecate_patch()` mechanism for evolving workflow code while existing executions are running:

1. **Add patch**: Branch on `patched("change-id")` -- new executions take new path, replaying executions take old path
2. **Deprecate patch**: Once all old executions complete, call `deprecate_patch("change-id")` and remove old code path
3. **Remove patch**: After retention window, remove the deprecate call entirely
