# Temporal TypeScript SDK Reference

Detailed reference for the `@temporalio/*` TypeScript packages.

## Table of Contents

- [Installation](#installation)
- [Project Structure](#project-structure)
- [Packages](#packages)
- [Workflows](#workflows)
- [Activities](#activities)
- [Client Usage](#client-usage)
- [Worker Setup](#worker-setup)
- [Signals, Queries, Updates](#signals-queries-updates)
- [Error Handling](#error-handling)
- [Activity Options](#activity-options)
- [Heartbeating](#heartbeating)
- [Cancellation](#cancellation)
- [Child Workflows](#child-workflows)
- [Continue-As-New](#continue-as-new)
- [Versioning and Patching](#versioning-and-patching)
- [Interceptors](#interceptors)
- [Sandbox and Bundling](#sandbox-and-bundling)
- [Testing](#testing)
- [Workflow APIs](#workflow-apis)
- [Activity Context APIs](#activity-context-apis)

## Installation

```bash
npx @temporalio/create@latest ./my-app
```

Or add to existing project:
```bash
npm install @temporalio/client @temporalio/worker @temporalio/workflow @temporalio/activity @temporalio/common
```

Node.js 18+ required.

## Project Structure

```
src/
  activities.ts    # Activity implementations (normal Node.js)
  workflows.ts     # Workflow definitions (sandboxed V8 isolate)
  worker.ts        # Worker setup
  client.ts        # Client code
```

## Packages

| Package | Purpose |
|---------|---------|
| `@temporalio/client` | `Client`, `Connection` for starting/signaling/querying |
| `@temporalio/worker` | `Worker`, `NativeConnection`, `bundleWorkflowCode` |
| `@temporalio/workflow` | Workflow APIs: `proxyActivities`, `sleep`, `condition`, `defineSignal`, etc. |
| `@temporalio/activity` | Activity context: `heartbeat`, `activityInfo`, `cancellationSignal` |
| `@temporalio/common` | Shared types: `ApplicationFailure`, `RetryPolicy` |
| `@temporalio/testing` | `TestWorkflowEnvironment`, `MockActivityEnvironment` |

All packages share the same version.

## Workflows

Workflows are async functions exported from the workflows file. The function name becomes the workflow type.

```typescript
import { proxyActivities, sleep } from '@temporalio/workflow';
import type * as activities from './activities';

const { greet } = proxyActivities<typeof activities>({
  startToCloseTimeout: '1 minute',
});

export async function greetingWorkflow(name: string): Promise<string> {
  const result = await greet(name);
  await sleep('1 day');
  return result;
}
```

Key pattern: import only **types** from activities (`import type * as`). Actual implementations are registered on the Worker. Activities are called via `proxyActivities<typeof activities>()`.

## Activities

Regular async functions in the standard Node.js environment:

```typescript
export async function greet(name: string): Promise<string> {
  return `Hello, ${name}!`;
}

export async function fetchData(url: string): Promise<unknown> {
  const res = await fetch(url);
  return res.json();
}
```

### Dependency Injection

```typescript
export interface DB {
  get(key: string): Promise<string>;
}

export const createActivities = (db: DB) => ({
  async greet(msg: string): Promise<string> {
    const name = await db.get('name');
    return `${msg}: ${name}`;
  },
});

// Worker registration
const worker = await Worker.create({
  activities: createActivities(realDb),
  ...
});
```

## Client Usage

```typescript
import { Client, Connection } from '@temporalio/client';

// Local
const connection = await Connection.connect();
const client = new Client({ connection });

// Temporal Cloud (API key)
const connection = await Connection.connect({
  address: '<namespace>.<account>.tmprl.cloud:7233',
  tls: true,
  apiKey: '<api-key>',
});
const client = new Client({ connection, namespace: '<namespace>.<account>' });

// Temporal Cloud (mTLS)
const connection = await Connection.connect({
  address: 'ns.tmprl.cloud:7233',
  tls: {
    clientCertPair: {
      crt: await fs.readFile('./client.pem'),
      key: await fs.readFile('./client.key'),
    },
  },
});
```

### Starting Workflows

```typescript
// Start and wait
const result = await client.workflow.execute(greetingWorkflow, {
  workflowId: 'greeting-1',
  taskQueue: 'my-queue',
  args: ['World'],
});

// Start (non-blocking)
const handle = await client.workflow.start(greetingWorkflow, {
  workflowId: 'greeting-1',
  taskQueue: 'my-queue',
  args: ['World'],
});
const result = await handle.result();

// Get handle to existing
const handle = client.workflow.getHandle('workflow-id');
```

### Handle Operations

```typescript
await handle.signal(approveSignal, { name: 'Alice' });
const status = await handle.query(statusQuery);
const prev = await handle.executeUpdate(setLanguageUpdate, { args: ['es'] });

const updateHandle = await handle.startUpdate(setLanguageUpdate, {
  args: ['fr'],
  waitForStage: WorkflowUpdateStage.ACCEPTED,
});
const updateResult = await updateHandle.result();

await handle.cancel();
await handle.terminate('reason');
const description = await handle.describe();
```

### Signal-With-Start

```typescript
await client.workflow.signalWithStart(myWorkflow, {
  workflowId: 'wf-1',
  taskQueue: 'my-queue',
  args: [{ foo: 1 }],
  signal: joinSignal,
  signalArgs: [{ userId: 'user-1' }],
});
```

## Worker Setup

```typescript
import { Worker, NativeConnection } from '@temporalio/worker';
import * as activities from './activities';

const connection = await NativeConnection.connect({ address: 'localhost:7233' });
const worker = await Worker.create({
  connection,
  workflowsPath: require.resolve('./workflows'),
  activities,
  taskQueue: 'my-task-queue',
});
await worker.run();
```

### Key WorkerOptions

| Option | Description |
|--------|-------------|
| `taskQueue` (required) | Task queue to poll |
| `workflowsPath` | Path to workflows file (dev -- bundles at startup) |
| `workflowBundle` | Pre-built bundle `{ codePath }` or `{ code }` (prod) |
| `activities` | Object mapping activity names to implementations |
| `connection` | `NativeConnection` instance |
| `namespace` | Default: `"default"` |
| `interceptors` | `{ workflowModules, activityInbound, activity }` |
| `sinks` | InjectedSinks for exporting data from workflows |
| `maxConcurrentActivityTaskExecutions` | Concurrent activity limit |
| `maxConcurrentWorkflowTaskExecutions` | Concurrent workflow task limit |
| `maxCachedWorkflows` | Workflow isolates kept in memory |
| `shutdownGraceTime` | Grace period during shutdown |
| `dataConverter` | Custom payload serialization |
| `reuseV8Context` | Performance optimization |

## Signals, Queries, Updates

Defined with `defineSignal`, `defineQuery`, `defineUpdate` and registered with `setHandler`:

```typescript
import * as wf from '@temporalio/workflow';

// Definitions (can live in a shared file)
export const approveSignal = wf.defineSignal<[{ name: string }]>('approve');
export const statusQuery = wf.defineQuery<string>('status');
export const setLangUpdate = wf.defineUpdate<string, [string]>('setLanguage');

export async function myWorkflow(): Promise<string> {
  let approved = false;
  let language = 'en';

  wf.setHandler(approveSignal, (input) => { approved = true; });

  wf.setHandler(statusQuery, () => approved ? 'approved' : 'pending');

  wf.setHandler(
    setLangUpdate,
    (newLang) => { const prev = language; language = newLang; return prev; },
    {
      validator: (newLang) => {
        if (!['en', 'es', 'fr'].includes(newLang)) throw new Error('Unsupported');
      },
    }
  );

  await wf.condition(() => approved);
  return `Done in ${language}`;
}
```

## Error Handling

### In Activities

```typescript
import { ApplicationFailure } from '@temporalio/common';

// Non-retryable
throw ApplicationFailure.create({
  message: 'Invalid input',
  type: 'ValidationError',
  nonRetryable: true,
});

// Custom retry delay
throw ApplicationFailure.create({
  message: 'Rate limited',
  nextRetryDelay: '15s',
});
```

### In Workflows

Unhandled errors that are NOT `ApplicationFailure` fail the **Workflow Task** (retried automatically). Throwing `ApplicationFailure` fails the **Workflow Execution**.

```typescript
import { ActivityFailure, ApplicationFailure } from '@temporalio/common';

try {
  await riskyActivity();
} catch (err) {
  if (err instanceof ActivityFailure && err.cause instanceof ApplicationFailure) {
    console.log('Activity failed:', err.cause.message);
  }
  throw err;
}
```

### On the Client

`handle.result()` throws `WorkflowFailedError` with a `cause` containing the failure chain.

## Activity Options

```typescript
const { myActivity } = proxyActivities<typeof activities>({
  startToCloseTimeout: '30s',
  scheduleToCloseTimeout: '5m',
  scheduleToStartTimeout: '10s',
  heartbeatTimeout: '5s',
  retry: {
    initialInterval: '1s',
    backoffCoefficient: 2,
    maximumInterval: '30s',
    maximumAttempts: 5,
    nonRetryableErrorTypes: ['ValidationError'],
  },
  taskQueue: 'specific-queue',
  cancellationType: ActivityCancellationType.WAIT_CANCELLATION_COMPLETED,
  activityId: 'custom-id',
});
```

`Duration` values accept strings (`'30s'`, `'1 minute'`, `'5m'`, `'1 day'`) or millisecond numbers.

### Local Activities

```typescript
import { proxyLocalActivities } from '@temporalio/workflow';

const { quickOp } = proxyLocalActivities<typeof activities>({
  startToCloseTimeout: '2s',
});
```

## Heartbeating

```typescript
import { heartbeat, activityInfo } from '@temporalio/activity';

export async function processLargeFile(path: string): Promise<void> {
  const startLine = activityInfo().heartbeatDetails?.line ?? 0;
  for (let line = startLine; line < totalLines; line++) {
    // process...
    heartbeat({ line }); // SDK throttles to 80% of heartbeatTimeout
  }
}
```

## Cancellation

```typescript
import {
  CancellationScope,
  isCancellation,
} from '@temporalio/workflow';

// Non-cancellable cleanup
await CancellationScope.nonCancellable(() => cleanup());

// Timeout scope
await CancellationScope.withTimeout(5000, () => someActivity());

// Handle external cancellation
try {
  await longRunningActivity();
} catch (err) {
  if (isCancellation(err)) {
    await CancellationScope.nonCancellable(() => cleanup());
  }
  throw err;
}
```

Activity cancellation detection:
```typescript
import { cancellationSignal } from '@temporalio/activity';

export async function cancellableActivity(): Promise<void> {
  const signal = cancellationSignal();
  await fetch(url, { signal });
}
```

## Child Workflows

```typescript
import { executeChild, startChild } from '@temporalio/workflow';

// Execute and wait
const result = await executeChild(childWorkflow, {
  args: ['arg1'],
  workflowId: 'child-1',
});

// Start and get handle
const childHandle = await startChild(childWorkflow, {
  args: ['arg1'],
  workflowId: 'child-2',
});
await childHandle.signal(someSignal, data);
const childResult = await childHandle.result();
```

## Continue-As-New

```typescript
import { continueAsNew, workflowInfo } from '@temporalio/workflow';

export async function loopingWorkflow(state: State): Promise<void> {
  // ... process ...

  if (workflowInfo().continueAsNewSuggested) {
    await continueAsNew<typeof loopingWorkflow>(updatedState);
  }
}
```

For a different workflow type:
```typescript
import { makeContinueAsNewFunc } from '@temporalio/workflow';

const continueAsOther = makeContinueAsNewFunc<typeof otherWorkflow>({
  taskQueue: 'other-queue',
});
await continueAsOther(args);
```

## Versioning and Patching

**Step 1 -- Add patch:**
```typescript
import { patched } from '@temporalio/workflow';

if (patched('my-change-id')) {
  await activityB();
} else {
  await activityA();
}
```

**Step 2 -- Deprecate (no old executions remain):**
```typescript
import { deprecatePatch } from '@temporalio/workflow';

deprecatePatch('my-change-id');
await activityB();
```

**Step 3 -- Remove call after retention window.**

## Interceptors

### Workflow Outbound (e.g., logging activity calls)

```typescript
// src/workflows/interceptors.ts
import {
  ActivityInput, Next, WorkflowOutboundCallsInterceptor, workflowInfo,
} from '@temporalio/workflow';

export class ActivityLogInterceptor implements WorkflowOutboundCallsInterceptor {
  async scheduleActivity(
    input: ActivityInput,
    next: Next<WorkflowOutboundCallsInterceptor, 'scheduleActivity'>,
  ): Promise<unknown> {
    console.log('Starting activity', input.activityType);
    return await next(input);
  }
}

export const interceptors = () => ({
  outbound: [new ActivityLogInterceptor()],
});
```

### Registration

```typescript
const worker = await Worker.create({
  interceptors: {
    workflowModules: [require.resolve('./workflows/interceptors')],
  },
  ...
});
```

## Sandbox and Bundling

### Sandbox Constraints

Workflow code runs in a V8 isolate with deterministic replacements:

| Replaced | Behavior |
|----------|----------|
| `Math.random()` | Seeded PRNG |
| `Date.now()` | Workflow clock |
| `setTimeout`/`clearTimeout` | Deterministic timers |

**Unavailable:** Node.js built-ins (`fs`, `path`, `process`, `crypto`, `http`), DOM APIs, `FinalizationRegistry`, `WeakRef`, dynamic `import()`.

### Production Bundling

Pre-build the workflow bundle for production:

```typescript
import { bundleWorkflowCode } from '@temporalio/worker';
import { writeFile } from 'fs/promises';

const { code } = await bundleWorkflowCode({
  workflowsPath: require.resolve('./workflows'),
});
await writeFile('./workflow-bundle.js', code);
```

Use in Worker:
```typescript
const worker = await Worker.create({
  workflowBundle: { codePath: './workflow-bundle.js' },
  activities,
  taskQueue: 'my-queue',
});
```

The `@temporalio/worker` version for `bundleWorkflowCode` and `Worker.create` must match exactly.

**esbuild alternative**: `build-temporal-workflow` package (9-11x faster, 94% less memory).

## Testing

### Workflow Testing (Time-Skipping)

```typescript
import { TestWorkflowEnvironment } from '@temporalio/testing';
import { Worker } from '@temporalio/worker';

let testEnv: TestWorkflowEnvironment;
beforeAll(async () => { testEnv = await TestWorkflowEnvironment.createTimeSkipping(); });
afterAll(async () => { await testEnv?.teardown(); });

test('workflow completes', async () => {
  const worker = await Worker.create({
    connection: testEnv.nativeConnection,
    taskQueue: 'test',
    workflowsPath: require.resolve('./workflows'),
    activities: { /* real or mock */ },
  });

  const result = await worker.runUntil(
    testEnv.client.workflow.execute(myWorkflow, {
      workflowId: uuid4(), taskQueue: 'test', args: ['input'],
    }),
  );
  expect(result).toEqual('expected');
});
```

### Mocking Activities

```typescript
const mockActivities: Partial<typeof activities> = {
  makeHTTPRequest: async () => '99',
};

const worker = await Worker.create({
  connection: testEnv.nativeConnection,
  taskQueue: 'test',
  workflowsPath: require.resolve('./workflows'),
  activities: mockActivities,
});
```

### Activity Unit Testing

```typescript
import { MockActivityEnvironment } from '@temporalio/testing';

const env = new MockActivityEnvironment({ attempt: 2 });
const result = await env.run(myActivity, arg1, arg2);
```

### Time Control

```typescript
await testEnv.sleep('25 hours'); // advance time manually
```

## Workflow APIs

| API | Purpose |
|-----|---------|
| `sleep(duration)` | Deterministic timer |
| `condition(fn, timeout?)` | Wait for predicate; returns `false` on timeout |
| `proxyActivities<T>(opts)` | Create type-safe activity proxy |
| `proxyLocalActivities<T>(opts)` | Local activity proxy |
| `defineSignal<Args>(name)` | Define signal type |
| `defineQuery<Ret, Args>(name)` | Define query type |
| `defineUpdate<Ret, Args>(name)` | Define update type |
| `setHandler(def, handler, opts?)` | Register signal/query/update handler |
| `executeChild(fn, opts)` | Execute child workflow |
| `startChild(fn, opts)` | Start child workflow (get handle) |
| `continueAsNew<T>(args)` | Continue-as-new |
| `patched(id)` | Version gate |
| `deprecatePatch(id)` | Deprecate version gate |
| `workflowInfo()` | Workflow metadata |
| `uuid4()` | Deterministic UUID |
| `log` | Workflow-safe logger |
| `Trigger<T>` | Programmatic promise resolution |

## Activity Context APIs

| API | Purpose |
|-----|---------|
| `heartbeat(details?)` | Send heartbeat with checkpoint data |
| `activityInfo()` | Metadata: `attempt`, `heartbeatDetails`, `workflowId`, etc. |
| `Context.current()` | Current activity context |
| `cancellationSignal()` | `AbortSignal` for cancellation |
| `cancelled()` | Promise that rejects on cancellation |
| `sleep(duration)` | Cancellation-aware sleep |
| `getClient()` | Temporal Client from within activity |
| `log` | Activity-safe logger |
