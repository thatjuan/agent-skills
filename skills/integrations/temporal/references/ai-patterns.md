# Temporal AI Orchestration Patterns

Patterns and integrations for building durable AI agent systems, LLM pipelines, and ML workflows with Temporal.

## Table of Contents

- [Agent Loop Pattern](#agent-loop-pattern)
- [Multi-Agent Architectures](#multi-agent-architectures)
- [Human-in-the-Loop](#human-in-the-loop)
- [Tool Use and Function Calling](#tool-use-and-function-calling)
- [LLM Pipeline Patterns](#llm-pipeline-patterns)
- [Rate Limit and Retry Handling](#rate-limit-and-retry-handling)
- [Claim Check Pattern](#claim-check-pattern)
- [Fan-Out / Fan-In](#fan-out--fan-in)
- [Saga Pattern for AI Operations](#saga-pattern-for-ai-operations)
- [Framework Integrations](#framework-integrations)
- [Durable MCP](#durable-mcp)
- [AI-Specific Configuration](#ai-specific-configuration)
- [Error Classification](#error-classification)

## Agent Loop Pattern

The fundamental AI agent pattern: a Workflow maintains durable state and conversation history, Activities handle LLM calls and tool invocations.

### Python

```python
@dataclass
class AgentState:
    goal: str
    conversation_history: list[dict] = field(default_factory=list)

@activity.defn
async def call_llm(request: LLMRequest) -> LLMResponse:
    client = AsyncAnthropic(max_retries=0)  # Temporal handles retries
    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        messages=request.messages,
        tools=request.tools,
        max_tokens=4096,
    )
    return LLMResponse(content=response.content, stop_reason=response.stop_reason)

@activity.defn
async def execute_tool(name: str, params: dict) -> str:
    # Tool execution logic
    return result

@workflow.defn
class AIAgentWorkflow:
    @workflow.run
    async def run(self, state: AgentState) -> str:
        messages = [{"role": "user", "content": state.goal}]

        while True:
            response = await workflow.execute_activity(
                call_llm,
                LLMRequest(messages=messages, tools=TOOL_DEFINITIONS),
                start_to_close_timeout=timedelta(seconds=60),
                retry_policy=LLM_RETRY_POLICY,
            )

            if response.stop_reason == "end_turn":
                return response.text_content()

            for tool_use in response.tool_use_blocks():
                result = await workflow.execute_activity(
                    execute_tool, tool_use.name, tool_use.input,
                    start_to_close_timeout=timedelta(seconds=30),
                )
                messages.append(tool_result_message(tool_use.id, result))
```

### TypeScript

```typescript
import { proxyActivities } from '@temporalio/workflow';
import type * as activities from './activities';

const { callLLM, executeTool } = proxyActivities<typeof activities>({
  startToCloseTimeout: '60s',
  retry: {
    initialInterval: '1s',
    backoffCoefficient: 2,
    maximumInterval: '120s',
    maximumAttempts: 50,
    nonRetryableErrorTypes: ['AuthenticationError', 'InvalidInput'],
  },
});

export async function aiAgentWorkflow(goal: string): Promise<string> {
  const messages = [{ role: 'user', content: goal }];

  while (true) {
    const response = await callLLM({ messages, tools: TOOL_DEFINITIONS });

    if (response.stopReason === 'end_turn') {
      return response.textContent;
    }

    for (const toolUse of response.toolUseBlocks) {
      const result = await executeTool(toolUse.name, toolUse.input);
      messages.push({ role: 'tool', toolUseId: toolUse.id, content: result });
    }
  }
}
```

Deterministic execution differs from predetermined behavior: on replay, the agent replays identical recorded decisions. On initial runs, the LLM is free to make different choices.

## Multi-Agent Architectures

Three documented patterns:

### Agent Routing

An orchestrator Workflow routes users to specialized agents based on intent:

```python
@workflow.defn
class RouterWorkflow:
    @workflow.run
    async def run(self, user_input: str) -> str:
        intent = await workflow.execute_activity(
            classify_intent, user_input,
            start_to_close_timeout=timedelta(seconds=15),
        )
        return await workflow.execute_child_workflow(
            AGENT_REGISTRY[intent].run, user_input,
            id=f"agent-{intent}-{workflow.uuid4()}",
        )
```

### Task Delegation

An orchestrator decomposes work and delegates subtasks to specialized sub-agents:

```python
@workflow.defn
class OrchestratorWorkflow:
    @workflow.run
    async def run(self, task: ComplexTask) -> Result:
        plan = await workflow.execute_activity(
            create_plan, task,
            start_to_close_timeout=timedelta(seconds=30),
        )
        results = []
        for subtask in plan.subtasks:
            result = await workflow.execute_child_workflow(
                SpecialistAgent.run, subtask,
                id=f"specialist-{subtask.id}",
            )
            results.append(result)
        return await workflow.execute_activity(
            synthesize_results, results,
            start_to_close_timeout=timedelta(seconds=30),
        )
```

### DAPER Pattern

Detect, Analyze, Plan, Execute, Report -- a five-step autonomous problem-solving framework where each step is an Activity or Child Workflow.

## Human-in-the-Loop

Temporal Signals enable durable approval gates with zero-compute waiting:

### Python

```python
@dataclass
class ApprovalDecision:
    approved: bool
    reviewer: str
    notes: str = ""

@workflow.defn
class HumanInTheLoopAgent:
    def __init__(self):
        self._decision: ApprovalDecision | None = None

    @workflow.signal
    def submit_decision(self, decision: ApprovalDecision) -> None:
        self._decision = decision

    @workflow.query
    def get_pending_action(self) -> dict | None:
        return self._pending_action

    @workflow.run
    async def run(self, task: str) -> str:
        proposed_action = await workflow.execute_activity(
            plan_action, task,
            start_to_close_timeout=timedelta(seconds=30),
        )
        self._pending_action = proposed_action

        # Wait indefinitely (zero compute) or with timeout
        await workflow.wait_condition(lambda: self._decision is not None)

        if self._decision.approved:
            return await workflow.execute_activity(
                execute_action, proposed_action,
                start_to_close_timeout=timedelta(minutes=5),
            )
        return f"Rejected by {self._decision.reviewer}: {self._decision.notes}"
```

### TypeScript

```typescript
import * as wf from '@temporalio/workflow';

const approvalSignal = wf.defineSignal<[{ approved: boolean; reviewer: string }]>('approval');
const pendingQuery = wf.defineQuery<unknown>('pending');

export async function humanInTheLoopAgent(task: string): Promise<string> {
  let decision: { approved: boolean; reviewer: string } | undefined;

  wf.setHandler(approvalSignal, (d) => { decision = d; });

  const proposed = await planAction(task);
  wf.setHandler(pendingQuery, () => proposed);

  await wf.condition(() => decision !== undefined);

  if (decision!.approved) {
    return await executeAction(proposed);
  }
  return `Rejected by ${decision!.reviewer}`;
}
```

Signals persist in workflow history -- approval state survives crashes without re-requesting.

## Tool Use and Function Calling

Tools are implemented as Activities. Dynamic dispatch via `@activity.defn(dynamic=True)` (Python) or a tool registry:

```python
TOOL_REGISTRY = {
    "search_web": search_web_activity,
    "read_file": read_file_activity,
    "write_file": write_file_activity,
    "run_code": run_code_activity,
}

@workflow.defn
class ToolCallingAgent:
    @workflow.run
    async def run(self, prompt: str) -> str:
        messages = [{"role": "user", "content": prompt}]
        while True:
            response = await workflow.execute_activity(
                call_llm, LLMRequest(messages=messages, tools=list(TOOL_REGISTRY)),
                start_to_close_timeout=timedelta(seconds=60),
            )
            if not response.has_tool_calls:
                return response.text

            for tool_call in response.tool_calls:
                tool_fn = TOOL_REGISTRY[tool_call.name]
                result = await workflow.execute_activity(
                    tool_fn, tool_call.input,
                    start_to_close_timeout=timedelta(seconds=30),
                )
                messages.append(tool_result(tool_call.id, result))
```

The OpenAI Agents SDK integration provides `activity_as_tool` for generating tool schemas from Activity function signatures automatically.

## LLM Pipeline Patterns

### RAG Pipeline

```python
@workflow.defn
class RAGWorkflow:
    @workflow.run
    async def run(self, query: str) -> str:
        embedding = await workflow.execute_activity(
            generate_embedding, query,
            start_to_close_timeout=timedelta(seconds=15),
        )
        documents = await workflow.execute_activity(
            vector_search, embedding,
            start_to_close_timeout=timedelta(seconds=10),
        )
        return await workflow.execute_activity(
            generate_response,
            GenerateInput(query=query, context=documents),
            start_to_close_timeout=timedelta(seconds=60),
        )
```

### Batch Embedding Pipeline

```python
@workflow.defn
class EmbeddingPipeline:
    @workflow.run
    async def run(self, documents: list[str]) -> list[list[float]]:
        results = []
        for batch in chunk(documents, size=100):
            embeddings = await workflow.execute_activity(
                generate_embeddings_batch, batch,
                start_to_close_timeout=timedelta(seconds=30),
            )
            results.extend(embeddings)
            if workflow.info().is_continue_as_new_suggested():
                workflow.continue_as_new(documents[len(results):])
        return results
```

## Rate Limit and Retry Handling

### Disable Client-Level Retries

LLM client libraries have built-in retry logic that conflicts with Temporal:

```python
# Python
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

anthropic_client = AsyncAnthropic(max_retries=0)
openai_client = AsyncOpenAI(max_retries=0)
```

```typescript
// TypeScript
import OpenAI from 'openai';
const openai = new OpenAI({ maxRetries: 0 });
```

### Recommended Retry Policy

```python
LLM_RETRY_POLICY = RetryPolicy(
    initial_interval=timedelta(seconds=1),
    backoff_coefficient=2.0,
    maximum_interval=timedelta(seconds=120),
    maximum_attempts=50,
    non_retryable_error_types=["InvalidInput", "AuthenticationError", "BadRequest"],
)
```

### Parse Retry-After Headers

```python
@activity.defn
async def call_llm(request: LLMRequest) -> LLMResponse:
    try:
        return await client.messages.create(...)
    except RateLimitError as e:
        retry_after = int(e.response.headers.get("retry-after", 5))
        raise ApplicationError(
            "Rate limited",
            type="RateLimited",
            next_retry_delay=timedelta(seconds=retry_after),
        )
```

```typescript
export async function callLLM(request: LLMRequest): Promise<LLMResponse> {
  try {
    return await client.chat.completions.create(...);
  } catch (err: any) {
    if (err.status === 429) {
      const retryAfter = parseInt(err.headers?.['retry-after'] ?? '5');
      throw ApplicationFailure.create({
        message: 'Rate limited',
        type: 'RateLimited',
        nextRetryDelay: `${retryAfter}s`,
      });
    }
    throw err;
  }
}
```

## Claim Check Pattern

For large payloads (LLM responses, document collections) that exceed event history payload limits, offload to external storage:

```python
@activity.defn
async def process_and_store(data: LargeInput) -> str:
    result = await expensive_computation(data)
    key = f"results/{workflow_id}/{uuid4()}"
    await s3_client.put_object(Bucket="my-bucket", Key=key, Body=json.dumps(result))
    return key  # Store only the reference in workflow history

@activity.defn
async def retrieve(key: str) -> dict:
    obj = await s3_client.get_object(Bucket="my-bucket", Key=key)
    return json.loads(obj["Body"].read())
```

## Fan-Out / Fan-In

Parallel AI processing via concurrent Activities or Child Workflows:

```python
@workflow.defn
class ParallelInference:
    @workflow.run
    async def run(self, prompts: list[str]) -> list[str]:
        tasks = [
            workflow.execute_activity(
                call_llm, prompt,
                start_to_close_timeout=timedelta(seconds=60),
            )
            for prompt in prompts
        ]
        return await asyncio.gather(*tasks)
```

```typescript
export async function parallelInference(prompts: string[]): Promise<string[]> {
  return Promise.all(prompts.map((p) => callLLM(p)));
}
```

Task Queues enable routing inference to GPU-equipped workers:

```python
gpu_result = await workflow.execute_activity(
    run_inference, input_data,
    task_queue="gpu-workers",
    start_to_close_timeout=timedelta(minutes=10),
)
```

## Saga Pattern for AI Operations

Multi-step AI operations with compensation on failure:

```python
@workflow.defn
class ModelDeploymentWorkflow:
    @workflow.run
    async def run(self, config: DeployConfig) -> str:
        compensations = []
        try:
            compensations.append(("rollback_model_registry", config))
            await workflow.execute_activity(
                register_model, config,
                start_to_close_timeout=timedelta(minutes=5))

            compensations.append(("teardown_endpoint", config))
            await workflow.execute_activity(
                deploy_endpoint, config,
                start_to_close_timeout=timedelta(minutes=15))

            await workflow.execute_activity(
                run_smoke_tests, config,
                start_to_close_timeout=timedelta(minutes=10))

            return "deployed"
        except ActivityError:
            for comp, input in reversed(compensations):
                await workflow.execute_activity(
                    comp, input,
                    start_to_close_timeout=timedelta(minutes=5))
            raise
```

## Framework Integrations

### OpenAI Agents SDK

Custom Runner executes each agent invocation as a Temporal Activity:

```python
from agents import Agent, Runner

agent = Agent(name="assistant", instructions="You are helpful.")
result = await Runner.run(agent, input="Hello")  # Now durable via Temporal
```

`activity_as_tool` generates OpenAI-compatible tool schemas from Activity function signatures.

### Pydantic AI

`TemporalAgent` wraps any Pydantic AI agent, auto-offloading all I/O to Activities:

```python
from pydantic_ai.durable_exec.temporal import TemporalAgent

temporal_agent = TemporalAgent(my_pydantic_agent)
```

### Vercel AI SDK (TypeScript)

Plugin wraps `generateText()` calls in Activities:

```typescript
import { AiSDKPlugin } from '@temporalio/ai-sdk-plugin';

const worker = await Worker.create({
  plugins: [new AiSDKPlugin({ modelProvider: openai })],
  taskQueue: 'ai-queue',
  workflowsPath: require.resolve('./workflows'),
});
```

### Anthropic Claude API

Direct integration via Activities with Temporal-managed retries:

```python
@activity.defn
async def call_claude(messages: list[dict], tools: list[dict] | None = None) -> dict:
    client = AsyncAnthropic(max_retries=0)
    response = await client.messages.create(
        model="claude-sonnet-4-20250514",
        messages=messages,
        tools=tools,
        max_tokens=4096,
    )
    return response.model_dump()
```

### Model Context Protocol (MCP)

**Durable MCP**: Each MCP tool is backed by a Temporal Workflow, providing automatic retries, crash resilience, and audit trails. Enables long-running tools that would timeout in standard MCP servers.

## AI-Specific Configuration

### Activity Timeouts for LLM Calls

```python
# Short LLM call (classification, extraction)
short_llm_opts = {
    "start_to_close_timeout": timedelta(seconds=30),
    "retry_policy": LLM_RETRY_POLICY,
}

# Long LLM call (generation, reasoning)
long_llm_opts = {
    "start_to_close_timeout": timedelta(minutes=5),
    "retry_policy": LLM_RETRY_POLICY,
}

# Tool execution
tool_opts = {
    "start_to_close_timeout": timedelta(minutes=2),
    "heartbeat_timeout": timedelta(seconds=30),
}
```

### Workflow-Level Considerations

- Store conversation history in workflow variables (automatically durable)
- Long conversations may approach event history payload limits -- plan for summarization or Claim Check pattern
- Use `is_continue_as_new_suggested()` / `continueAsNewSuggested` for long-running agent loops
- Avoid Workflow-level timeouts for agent workflows (designed to be long-running)
- Use `start_to_close_timeout` on Activities for failure detection

## Error Classification

| Status Code | Category | Retry? |
|-------------|----------|--------|
| 400 | Bad request | No -- non-retryable |
| 401 | Authentication failure | No -- non-retryable |
| 403 | Forbidden | No -- non-retryable |
| 404 | Not found | No -- non-retryable |
| 408 | Request timeout | Yes |
| 409 | Conflict | Yes |
| 422 | Unprocessable entity | No -- non-retryable |
| 429 | Rate limited | Yes -- with Retry-After |
| 500+ | Server error | Yes |

```python
NON_RETRYABLE_ERRORS = [
    "InvalidInput",
    "AuthenticationError",
    "BadRequest",
    "NotFound",
    "PermissionDenied",
    "UnprocessableEntity",
]
```
