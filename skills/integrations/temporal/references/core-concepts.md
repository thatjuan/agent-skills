# Temporal Core Concepts

Detailed reference for Temporal.io platform architecture, execution model, and advanced features.

## Table of Contents

- [Architecture](#architecture)
- [Durable Execution Model](#durable-execution-model)
- [Workflow Execution Lifecycle](#workflow-execution-lifecycle)
- [Activity Execution](#activity-execution)
- [Retry Policies](#retry-policies)
- [Signals, Queries, and Updates](#signals-queries-and-updates)
- [Child Workflows vs Activities](#child-workflows-vs-activities)
- [Continue-As-New](#continue-as-new)
- [Schedules](#schedules)
- [Saga Pattern](#saga-pattern)
- [Visibility and Search Attributes](#visibility-and-search-attributes)
- [Interceptors](#interceptors)
- [Data Converters and Codecs](#data-converters-and-codecs)
- [Namespaces and Multi-Tenancy](#namespaces-and-multi-tenancy)
- [Temporal Cloud vs Self-Hosted](#temporal-cloud-vs-self-hosted)

## Architecture

### Server Components

The Temporal Server comprises four independently scalable services communicating via gRPC:

| Service | Port | Purpose |
|---------|------|---------|
| **Frontend** | 7233 | Stateless API gateway; rate limiting, authorization, validation, routing |
| **History** | 7234 | Persists workflow event history; scaling unit is History Shards (configured before DB integration, cannot change afterward) |
| **Matching** | 7235 | Hosts task queues; matches workers to tasks |
| **Worker** | internal | Background system workflows and replication |

**History Shards**: Workflows are assigned to shards via hash of `(Workflow ID, Namespace)`. Recommended ratio: 1 History Service process per 500 shards. Production deployments range from 1 shard (testing) to 128,000 shards (large-scale).

### Workers

Application processes that poll the Temporal Service for tasks, execute Workflow and Activity code, and report results. The Temporal Service never executes user code -- Workers do, meaning data stays on user infrastructure.

### Clients

SDK-provided objects communicating with the Frontend Service (port 7233) to start workflows, send signals, issue queries, send updates.

### Task Queues

Dispatch mechanism between service and workers. Workers poll specific task queues. Workflow Tasks and Activity Tasks are dispatched to separate logical queues even when sharing the same name. Enable load balancing across multiple workers and service-specific routing.

### Namespaces

Unit of isolation within Temporal:
- Workflow ID uniqueness is per-Namespace
- Traffic from one Namespace does not impact others
- Configuration (retention periods, archival) is per-Namespace
- Default Namespace is `"default"`

## Durable Execution Model

### Event Sourcing

Every step of a Workflow Execution is recorded as an **Event** in a durable **Event History**. Workflow code produces **Commands** (e.g., "schedule this Activity"); the service maps Commands to Events.

### Replay

When a Worker resumes a Workflow (after crash or cache eviction):
1. Workflow code re-executes from the beginning
2. SDK feeds previously recorded Event results instead of performing side effects
3. Commands generated during replay are validated against existing history
4. Once caught up, the Workflow resumes normal execution

### What Makes Code Non-Deterministic

**Intrinsic non-determinism:**
- Random numbers, system time, UUIDs generated inline
- Threading outside Temporal APIs
- Network calls or file I/O in Workflow code
- Mutable global state
- Non-deterministic iteration order (e.g., `set` iteration)

**Non-deterministic code changes:**
- Modifying Workflow code while existing executions are running
- Reordering or removing Temporal API calls

A mismatch between generated Commands and existing Events produces a **non-deterministic error**.

## Workflow Execution Lifecycle

### States

**Open:** Running

**Closed (6 statuses):**
- Completed -- finished successfully
- Failed -- ended with error
- Canceled -- cancellation requested and accepted
- Terminated -- forcefully stopped (no cleanup)
- Timed Out -- exceeded configured timeout
- Continued-As-New -- closed and immediately started new Run

### Identity

`(Namespace, Workflow ID, Run ID)` uniquely identifies a Workflow Execution.

- **Workflow ID**: User-defined; must be unique within Namespace for concurrent executions (configurable via ID Reuse Policy)
- **Run ID**: System-generated UUID per Run in a chain

### Timeout Types

| Timeout | Scope | Default |
|---------|-------|---------|
| Workflow Execution Timeout | Entire chain including Continue-As-New | None |
| Workflow Run Timeout | Single run | None |
| Workflow Task Timeout | Single SDK processing step | 10 seconds |

## Activity Execution

### Timeout Types

| Timeout | Scope | Recommendation |
|---------|-------|----------------|
| **Start-to-Close** | Single attempt | Set on every activity; primary failure detection mechanism |
| Schedule-to-Close | Entire execution including retries | Controls overall duration |
| Schedule-to-Start | Time in queue before pickup | Identifies worker fleet problems; does not trigger retries |

### Heartbeating

Long-running activities emit periodic heartbeats indicating progress:
- Combined with Heartbeat Timeout: if no heartbeat within timeout, activity task fails and retries
- SDK throttles heartbeat RPCs to 80% of timeout interval (30s min / 60s max)
- Heartbeats carry progress data for resuming interrupted activities
- Activities must heartbeat to receive cancellation notifications

### Async Activity Completion

An Activity Function can return without completing the Activity Execution. External systems complete it later via Task Token or Activity ID -- useful for human-in-the-loop and callback patterns.

## Retry Policies

| Property | Default | Description |
|----------|---------|-------------|
| Initial Interval | 1s | Wait before first retry |
| Backoff Coefficient | 2.0 | Multiplier per successive retry |
| Maximum Interval | 100x Initial (100s) | Cap on retry wait time |
| Maximum Attempts | Unlimited | Total attempts (1 = no retries) |
| Non-Retryable Error Types | None | Error types that bypass retry |

Activities automatically retry with default policy. Workflows do not retry by default.

**Non-Retryable Errors**: Matched against the `type` field of ApplicationFailure. For permanent failures (invalid input, bad credentials) that will never succeed on retry.

## Signals, Queries, and Updates

### Queries (Read-only)

- Examine current state without blocking
- No Event History entries (zero persistence cost)
- Work on completed workflows
- Cannot mutate state

### Signals (Async write)

- Fire-and-forget; no response tracking or error feedback
- No Worker availability confirmation required
- Unlimited concurrent messaging
- Create Event History entries

### Updates (Sync tracked write)

- Sender awaits completion response or error
- Create Event History entries
- Subject to per-Workflow concurrency limits
- Support validators for input rejection

## Child Workflows vs Activities

| Aspect | Child Workflow | Activity |
|--------|---------------|----------|
| API Access | Full Workflow APIs (deterministic constraints apply) | No deterministic constraints |
| Cancellation | Can survive Parent (ABANDON policy) | Canceled with Parent |
| Event History | Separate history | Shares Parent's history |
| Timeout | Can run for years | Bounded by activity timeouts |
| Tracking | Complete event history | Input, output, retry attempts only |

**When to use Child Workflows:**
1. Workload partitioning (single Workflow cap: ~50K events)
2. Separate service Workers
3. Resource management via Workflow ID uniqueness
4. Periodic logic with Continue-As-New in child

Recommended max: 1,000 Child Workflows per Parent. When in doubt, use an Activity.

## Continue-As-New

Closes a Workflow Execution and immediately starts a fresh Run with new Event History, preserving the Workflow ID. Prevents unbounded history growth.

Key properties:
- Child Workflows do not carry over when Parent uses Continue-As-New
- If a Child uses Continue-As-New, Parent sees the chain as a single execution
- Message deduplication does not work across Continue-As-New boundaries
- Finish running all message handlers before continuing as new
- `workflow.info().is_continue_as_new_suggested()` (Python) / `workflowInfo().continueAsNewSuggested` (TypeScript) indicates when history is growing large

## Schedules

Server-managed recurring workflow execution (replaces legacy Cron Workflows):
- More configuration options than cron
- Can be updated, paused while running
- Overlap policies (skip, buffer, cancel, terminate previous)
- Created via Client API or CLI

## Saga Pattern

Compensating transactions for multi-step operations:
1. Track compensating actions for each completed step
2. On failure, execute compensations in reverse order
3. Each Activity must be idempotent
4. Use idempotency keys to prevent duplicate operations

## Visibility and Search Attributes

**Visibility**: APIs for viewing, filtering, and searching Workflow Executions using SQL-like List Filters.

**Search Attributes**: Indexed metadata key-value pairs on Workflow Executions.
- 21 default attributes (ExecutionStatus, WorkflowId, WorkflowType, StartTime, CloseTime, TaskQueue, etc.)
- Custom attribute types: Bool, Int, Double, Datetime, Keyword, KeywordList, Text
- Not encrypted (must be readable for indexing)
- Size limits: 2KB per value, 40KB total, 255 chars max per value

## Interceptors

Modify inbound and outbound SDK calls (middleware pattern). Common uses: tracing (OpenTelemetry), authorization, logging.

Types:
- `WorkflowInboundCallsInterceptor`: Intercepts workflow execution, signals, queries
- `WorkflowOutboundCallsInterceptor`: Intercepts outbound calls (scheduling activities, starting timers)
- `ActivityInboundCallsInterceptor`: Intercepts activity execution
- `WorkflowClientCallsInterceptor`: Intercepts client operations

Interceptors form a chain, each accepting `(input, next)`.

## Data Converters and Codecs

**Data Converter** transforms application objects to/from bytes for Temporal payloads.

**Default processing order:** null -> byte arrays -> Protobuf JSON -> JSON

**Components:**
- **Payload Converter**: Application types to/from Payloads
- **Payload Codec**: Bytes-to-bytes transformation (encryption, compression)
- **Failure Converter**: Error serialization control

Custom Data Converters do not apply to Search Attributes (they remain unencoded for indexing).

## Namespaces and Multi-Tenancy

**Self-hosted:** Unlimited Namespaces. Custom authorizers on Frontend for access control. Nexus enables cross-Namespace communication.

**Temporal Cloud:** Up to 100 Namespaces. Independent auth (API keys or mTLS per tenant). Built-in RBAC. Isolated rate limits. Multi-region data replication.

## Temporal Cloud vs Self-Hosted

| Aspect | Cloud | Self-Hosted |
|--------|-------|-------------|
| Operations | Fully managed | User deploys and manages |
| Namespaces | Up to 100 | Unlimited |
| HA | Built-in namespace HA | Configure multi-cluster replication |
| Retention | 30-90 days | Unlimited (storage-bounded) |
| Latency | ~2x lower than self-hosted | Depends on infrastructure |
| Scaling | Automatic | Manual (DB + 4 services) |
| Security | mTLS, API keys, RBAC built-in | Custom authorizer |
| Visibility | Advanced Visibility by default | Configure Elasticsearch or SQL stores (v1.20+) |
