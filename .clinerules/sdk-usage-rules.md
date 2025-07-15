## Brief overview
This rule establishes the project's commitment to using the official `openai-agents` SDK for all agent-related development. It explicitly forbids the direct use of lower-level client APIs like `client.chat.completions.create` and `client.responses.create` for agentic workflows.

## SDK Usage Mandate
- **Primary Tooling:** All agent creation, execution, and interaction MUST be implemented using the `agents.Agent`, `agents.Runner`, and `agents.FunctionTool` classes from the `openai-agents` SDK.
- **Forbidden APIs:** The direct use of `client.chat.completions.create` and `client.responses.create` (including with `response_model`) for agent logic is strictly prohibited. These are considered low-level APIs that are abstracted away by the Agents SDK.
- **Rationale:** The Agents SDK provides a higher-level, more maintainable abstraction for building complex, multi-agent systems. It handles state management, tool calling, and structured output guarantees in a standardized way, which is critical for the long-term health of the project.

## Refactoring and Legacy Code
- **Existing Code:** Any existing code that uses the forbidden low-level APIs should be flagged for refactoring and migrated to the Agents SDK as soon as feasible.
- **New Code:** All new features and agents must be built on the `openai-agents` SDK from the outset.
