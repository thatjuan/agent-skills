# Temporal Python SDK Reference

Detailed reference for the `temporalio` Python package.

## Table of Contents

- [Installation](#installation)
- [Project Structure](#project-structure)
- [Decorators](#decorators)
- [Workflows](#workflows)
- [Activities](#activities)
- [Client Usage](#client-usage)
- [Worker Setup](#worker-setup)
- [Signals, Queries, Updates](#signals-queries-updates)
- [Error Handling](#error-handling)
- [Activity Options and Timeouts](#activity-options-and-timeouts)
- [Heartbeating](#heartbeating)
- [Async Activity Completion](#async-activity-completion)
- [Child Workflows](#child-workflows)
- [Continue-As-New](#continue-as-new)
- [Versioning and Patching](#versioning-and-patching)
- [Schedules](#schedules)
- [Saga Pattern](#saga-pattern)
- [Dynamic Handlers](#dynamic-handlers)
- [Sandbox](#sandbox)
- [Testing](#testing)
- [Deterministic Utilities](#deterministic-utilities)

## Installation

```bash
pip install temporalio
```

Optional extras:
```bash
pip install temporalio[opentelemetry]   # tracing
pip install temporalio[pydantic]        # Pydantic data converter
pip install temporalio[openai-agents]   # OpenAI Agents SDK integration
```

Python 3.10+ required. Current version: 1.23.0.

## Project Structure

```
project/
  activities.py    # Activity definitions
  workflows.py     # Workflow definitions
  worker.py        # Worker setup
  starter.py       # Client code
```

## Decorators

| Decorator | Purpose | Parameters |
|-----------|---------|------------|
| `@workflow.defn` | Class as workflow definition | `name=`, `sandboxed=`, `dynamic=` |
| `@workflow.run` | Async entry-point method (exactly one per workflow) | |
| `@workflow.init` | Constructor receives workflow input before signals/updates | |
| `@workflow.signal` | Signal handler method | `name=`, `dynamic=`, `unfinished_policy=` |
| `@workflow.query` | Query handler method (sync, read-only) | `name=`, `dynamic=` |
| `@workflow.update` | Update handler method (async, returns value) | `name=`, `dynamic=`, `unfinished_policy=` |
| `@activity.defn` | Function/method as activity | `name=`, `dynamic=`, `no_thread_cancel_exception=` |

## Workflows

```python
from datetime import timedelta
from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from activities import my_activity, MyInput

@workflow.defn
class MyWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        return await workflow.execute_activity(
            my_activity,
            MyInput(name=name),
            start_to_close_timeout=timedelta(seconds=10),
        )
```

### @workflow.init

Receives workflow input before signal/update handlers run:

```python
@workflow.defn
class MyWorkflow:
    @workflow.init
    def __init__(self, input: MyInput) -> None:
        self.state = input.initial_state

    @workflow.run
    async def run(self, input: MyInput) -> str:
        return self.state
```

### Async Patterns

All workflow code runs in a custom asyncio event loop:

```python
# Durable timer
await asyncio.sleep(60)  # equivalent to workflow.sleep(60)

# Wait for condition
await workflow.wait_condition(lambda: self.approved)

# Wait with timeout
try:
    await workflow.wait_condition(lambda: self.approved, timeout=timedelta(hours=1))
except asyncio.TimeoutError:
    pass

# Wait for all handlers to finish
await workflow.wait_condition(workflow.all_handlers_finished)

# Mutex for concurrent handlers
self.lock = asyncio.Lock()
async with self.lock:
    pass
```

### Type Hints and Dataclasses

Best practice: use a single dataclass as argument (allows adding fields without breaking signatures):

```python
from dataclasses import dataclass

@dataclass
class OrderInput:
    customer_id: str
    items: list[str]
    total: float
```

Default data converter supports: `None`, `bytes`, Protobuf messages, `@dataclass`, JSON-serializable types, `UUID`, `datetime`, enums.

Pydantic support:
```python
from temporalio.contrib.pydantic import pydantic_data_converter
client = await Client.connect("localhost:7233", data_converter=pydantic_data_converter)
```

## Activities

```python
from temporalio import activity

# Async activity
@activity.defn
async def fetch_data(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()

# Sync activity (runs in thread pool; requires activity_executor on Worker)
@activity.defn
def process_file(path: str) -> str:
    with open(path) as f:
        return f.read()
```

## Client Usage

```python
from temporalio.client import Client, TLSConfig

# Local
client = await Client.connect("localhost:7233")

# Temporal Cloud (mTLS)
client = await Client.connect(
    "my-ns.tmprl.cloud:7233",
    namespace="my-ns.acct-id",
    tls=TLSConfig(
        client_cert=open("client-cert.pem", "rb").read(),
        client_private_key=open("client-key.pem", "rb").read(),
    ),
)

# Temporal Cloud (API key)
client = await Client.connect(
    "my-endpoint:7233",
    namespace="my-ns.acct-id",
    api_key="my-api-key",
    tls=True,
)

# Execute (start and wait)
result = await client.execute_workflow(
    MyWorkflow.run, "input",
    id="wf-123", task_queue="my-tq",
    execution_timeout=timedelta(hours=1),
)

# Start (non-blocking)
handle = await client.start_workflow(
    MyWorkflow.run, "input",
    id="wf-123", task_queue="my-tq",
)

# Get handle to existing workflow
handle = client.get_workflow_handle("wf-123")

# Handle operations
result = await handle.result()
await handle.signal(MyWorkflow.my_signal, signal_data)
query_result = await handle.query(MyWorkflow.my_query)
update_result = await handle.execute_update(MyWorkflow.my_update, data)
await handle.cancel()
await handle.terminate()
desc = await handle.describe()

# Start delay
handle = await client.start_workflow(
    MyWorkflow.run, "input",
    id="wf-delayed", task_queue="my-tq",
    start_delay=timedelta(hours=1),
)
```

## Worker Setup

```python
import asyncio
import concurrent.futures
from temporalio.client import Client
from temporalio.worker import Worker

async def main():
    client = await Client.connect("localhost:7233")
    with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
        worker = Worker(
            client,
            task_queue="my-task-queue",
            workflows=[WorkflowA, WorkflowB],
            activities=[activity_a, activity_b],
            activity_executor=executor,  # required for sync activities
        )
        await worker.run()

asyncio.run(main())
```

Key Worker parameters:
- `client` -- Connected client
- `task_queue` -- Task queue name
- `workflows` -- List of workflow classes
- `activities` -- List of activity functions
- `activity_executor` -- ThreadPoolExecutor or ProcessPoolExecutor for sync activities
- `workflow_runner` -- SandboxedWorkflowRunner (default) or UnsandboxedWorkflowRunner
- `interceptors` -- Middleware interceptors
- `max_concurrent_activities` -- Concurrent activity limit
- `max_concurrent_workflow_tasks` -- Concurrent workflow task limit

## Signals, Queries, Updates

### Signals

```python
@workflow.defn
class MyWorkflow:
    def __init__(self):
        self.approved = False

    @workflow.signal
    def approve(self, input: ApproveInput) -> None:
        self.approved = True

    @workflow.signal
    async def async_signal(self):
        async with self.lock:
            self.data = await workflow.execute_activity(
                fetch_data, start_to_close_timeout=timedelta(seconds=10))

    @workflow.run
    async def run(self) -> str:
        await workflow.wait_condition(lambda: self.approved)
        return "Approved!"
```

Sending signals:
```python
handle = await client.start_workflow(MyWorkflow.run, id="wf-1", task_queue="tq")
await handle.signal(MyWorkflow.approve, ApproveInput(name="boss"))

# Signal-with-start
await client.start_workflow(
    MyWorkflow.run, id="wf-1", task_queue="tq",
    start_signal="approve", start_signal_args=[ApproveInput(name="boss")],
)

# Cross-workflow signal
handle = workflow.get_external_workflow_handle_for(OtherWorkflow.run, "other-wf-id")
await handle.signal(OtherWorkflow.some_signal, "data")
```

### Queries

```python
@workflow.query
def get_status(self) -> str:
    return self.status

# Client-side
status = await handle.query(MyWorkflow.get_status)
```

### Updates

```python
@workflow.update
async def set_language(self, language: str) -> str:
    previous, self.language = self.language, language
    return previous

@set_language.validator
def validate_language(self, language: str) -> None:
    if language not in self.supported:
        raise ValueError(f"{language} not supported")

# Client-side
prev = await handle.execute_update(MyWorkflow.set_language, "fr")
update_handle = await handle.start_update(
    MyWorkflow.set_language, "es",
    wait_for_stage=client.WorkflowUpdateStage.ACCEPTED,
)
result = await update_handle.result()
```

## Error Handling

### Exception Hierarchy

All inherit from `TemporalError`:
- `ApplicationError` -- raised by user code; causes Workflow Execution failure
- `ActivityError` -- wraps activity exceptions; caught in workflows
- `ChildWorkflowError` -- child workflow failed
- `TimeoutError` -- timeout exceeded
- `CancelledError` -- cancellation

**Key distinction:** Plain Python exceptions (e.g., `ValueError`) in a workflow cause a Workflow Task failure (retried automatically). `ApplicationError` causes a Workflow Execution failure (terminates the workflow).

### Activity Errors

```python
from temporalio.exceptions import ApplicationError

# Non-retryable
raise ApplicationError("Invalid input", type="InvalidInput", non_retryable=True)

# Custom retry delay
raise ApplicationError(
    f"Rate limited on attempt {activity.info().attempt}",
    next_retry_delay=timedelta(seconds=3 * activity.info().attempt),
)
```

### Catching in Workflows

```python
from temporalio.exceptions import ActivityError, ApplicationError

try:
    result = await workflow.execute_activity(
        process_payment, details,
        start_to_close_timeout=timedelta(seconds=30),
        retry_policy=retry_policy,
    )
except ActivityError as e:
    workflow.logger.error(f"Payment failed: {e.cause}")
    raise ApplicationError(f"Payment failed: {e.cause}", type="PaymentError")
```

## Activity Options and Timeouts

At least one of `start_to_close_timeout` or `schedule_to_close_timeout` is required:

```python
from temporalio.common import RetryPolicy

result = await workflow.execute_activity(
    my_activity, my_input,
    start_to_close_timeout=timedelta(seconds=30),
    schedule_to_close_timeout=timedelta(minutes=5),
    schedule_to_start_timeout=timedelta(seconds=10),
    heartbeat_timeout=timedelta(seconds=5),
    retry_policy=RetryPolicy(
        initial_interval=timedelta(seconds=1),
        backoff_coefficient=2.0,
        maximum_interval=timedelta(minutes=1),
        maximum_attempts=5,
        non_retryable_error_types=["InvalidInput", "AuthError"],
    ),
    task_queue="specific-queue",
    cancellation_type=ActivityCancellationType.WAIT_CANCELLATION_COMPLETED,
    activity_id="custom-id",
)
```

Local activities (reduced overhead, same worker process):
```python
result = await workflow.execute_local_activity(
    my_activity, my_input,
    start_to_close_timeout=timedelta(seconds=5),
    local_retry_threshold=timedelta(seconds=10),
)
```

## Heartbeating

```python
@activity.defn
async def long_running(items: list[str]) -> str:
    for i, item in enumerate(items):
        activity.heartbeat(f"Processing item {i}")
        await process(item)
    return "done"

# Workflow side
await workflow.execute_activity(
    long_running, items,
    start_to_close_timeout=timedelta(minutes=30),
    heartbeat_timeout=timedelta(seconds=30),
)
```

## Async Activity Completion

```python
@activity.defn
async def request_approval(request_id: str) -> None:
    token = activity.info().task_token
    await store_token(request_id, token)
    activity.raise_complete_async()

# External completion
handle = client.get_async_activity_handle(task_token=stored_token)
await handle.complete("approved")
# or: await handle.fail(ApplicationError("rejected"))
```

## Child Workflows

```python
@workflow.defn
class ParentWorkflow:
    @workflow.run
    async def run(self, name: str) -> str:
        # Execute and wait
        result = await workflow.execute_child_workflow(
            ChildWorkflow.run, ChildInput(name),
            id="child-workflow-id",
            parent_close_policy=ParentClosePolicy.ABANDON,
        )

        # Start and get handle
        handle = await workflow.start_child_workflow(
            ChildWorkflow.run, ChildInput(name), id="child-2",
        )
        await handle.signal(ChildWorkflow.some_signal, "data")
        return await handle.result()
```

## Continue-As-New

```python
@workflow.defn
class LoopingWorkflow:
    @workflow.run
    async def run(self, state: dict) -> str:
        result = await workflow.execute_activity(
            process_batch, state,
            start_to_close_timeout=timedelta(seconds=30),
        )
        if workflow.info().is_continue_as_new_suggested():
            workflow.continue_as_new(result)
        return "done"
```

`workflow.continue_as_new()` raises `ContinueAsNewError` internally. Do not call from signal/update handlers.

## Versioning and Patching

**Step 1 -- Add patch:**
```python
if workflow.patched("my-patch"):
    result = await workflow.execute_activity(new_activity, ...)
else:
    result = await workflow.execute_activity(old_activity, ...)
```

**Step 2 -- Deprecate (all old executions completed):**
```python
workflow.deprecate_patch("my-patch")
result = await workflow.execute_activity(new_activity, ...)
```

**Step 3 -- Remove patch call entirely after retention window.**

## Schedules

```python
from temporalio.client import Schedule, ScheduleActionStartWorkflow, \
    ScheduleSpec, ScheduleIntervalSpec, ScheduleState

handle = await client.create_schedule(
    "my-schedule",
    Schedule(
        action=ScheduleActionStartWorkflow(
            MyWorkflow.run, "arg",
            id="scheduled-wf", task_queue="my-tq",
        ),
        spec=ScheduleSpec(
            intervals=[ScheduleIntervalSpec(every=timedelta(minutes=5))]
        ),
        state=ScheduleState(note="Every 5 minutes"),
    ),
)

# Pause
handle = client.get_schedule_handle("my-schedule")
await handle.pause(note="Maintenance")

# Delete
await handle.delete()
```

## Saga Pattern

```python
@workflow.defn
class OrderWorkflow:
    @workflow.run
    async def run(self, order):
        compensations = []
        try:
            compensations.append(("revert_inventory", order))
            await workflow.execute_activity(
                reserve_inventory, order,
                start_to_close_timeout=timedelta(seconds=10))

            compensations.append(("refund_payment", order))
            await workflow.execute_activity(
                charge_payment, order,
                start_to_close_timeout=timedelta(seconds=10))

            return {"status": "completed"}
        except ActivityError:
            for comp_name, comp_input in reversed(compensations):
                try:
                    await workflow.execute_activity(
                        comp_name, comp_input,
                        start_to_close_timeout=timedelta(seconds=10))
                except ActivityError:
                    workflow.logger.error(f"Compensation {comp_name} failed")
            raise ApplicationError("Order failed, rolled back", type="OrderFailed")
```

## Dynamic Handlers

```python
@workflow.defn(dynamic=True)
class DynamicWorkflow:
    @workflow.run
    async def run(self, args: Sequence[RawValue]) -> str:
        name = workflow.payload_converter().from_payload(args[0].payload, str)
        return f"Dynamic: {name}"

@activity.defn(dynamic=True)
async def dynamic_activity(args: Sequence[RawValue]) -> str:
    arg = activity.payload_converter().from_payload(args[0].payload, str)
    return f"Dynamic: {arg}"

@workflow.signal(dynamic=True)
async def dynamic_signal(self, name: str, args: Sequence[RawValue]) -> None:
    pass
```

## Sandbox

Workflow code runs in an isolated sandbox enforcing determinism:

```python
# Import pass-through for known-deterministic modules
with workflow.unsafe.imports_passed_through():
    import pydantic
    from my_activities import my_activity

# Disable sandbox for a block
with workflow.unsafe.sandbox_unrestricted():
    pass

# Disable per-workflow
@workflow.defn(sandboxed=False)
class MyWorkflow: ...

# Disable at worker level
from temporalio.worker.workflow_sandbox import UnsandboxedWorkflowRunner
worker = Worker(..., workflow_runner=UnsandboxedWorkflowRunner())

# Configure passthrough modules
from temporalio.worker.workflow_sandbox import SandboxedWorkflowRunner, SandboxRestrictions
worker = Worker(
    ...,
    workflow_runner=SandboxedWorkflowRunner(
        restrictions=SandboxRestrictions.default.with_passthrough_modules("pydantic")
    ),
)
```

## Testing

### Activity Testing

```python
from temporalio.testing import ActivityEnvironment

async def test_activity():
    env = ActivityEnvironment()
    heartbeats = []
    env.on_heartbeat = lambda *args: heartbeats.append(args[0])
    result = await env.run(my_activity, "input")
    assert result == "expected"
```

### Workflow Testing (Time-Skipping)

```python
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

async def test_workflow():
    async with await WorkflowEnvironment.start_time_skipping() as env:
        async with Worker(
            env.client, task_queue="test-tq",
            workflows=[MyWorkflow], activities=[my_activity],
        ):
            result = await env.client.execute_workflow(
                MyWorkflow.run, "input",
                id="test-wf", task_queue="test-tq",
            )
            assert result == "expected"
```

### Mocking Activities

```python
@activity.defn(name="my_activity")
async def mocked_activity(input: str) -> str:
    return "mocked result"

# Use in test Worker
async with Worker(
    env.client, task_queue="test-tq",
    workflows=[MyWorkflow], activities=[mocked_activity],
): ...
```

### Replay Testing

```python
from temporalio.worker import Replayer
from temporalio.client import WorkflowHistory

async def test_replay():
    replayer = Replayer(workflows=[MyWorkflow])
    await replayer.replay_workflow(WorkflowHistory.from_json(history_json))
```

## Deterministic Utilities

Available inside workflow code:

```python
workflow.now()       # deterministic datetime
workflow.time()      # deterministic float timestamp
workflow.random()    # seeded Random instance
workflow.uuid4()     # deterministic UUID
workflow.info()      # WorkflowInfo (workflow_id, run_id, etc.)
workflow.logger      # replay-safe logger (suppresses during replay)
```
