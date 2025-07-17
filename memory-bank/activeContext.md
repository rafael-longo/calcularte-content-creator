# Active Context: Calcularte Content Engine

**Version:** 1.1
**Date:** July 15, 2025

## 1. Current Focus

The current focus has been on the successful implementation of the core backend and command-line interface (CLI) for the "Calcularte Content Engine." This phase involved building out the multi-agent system and integrating it for a complete post-generation workflow.

## 2. Recent Changes

*   **Flexible and Autonomous Generation Implemented (Enhancement #3):**
    *   **`OrchestratorAgent` Updated:** New methods `plan_content_ideas` and `plan_and_develop_content` were added to enable multi-step, autonomous workflows. The `generate_ideas` method was enhanced to accept strategic context from the `BrandStrategistAgent`.
    *   **`CreativeDirectorAgent` Updated:** The agent's instructions were updated to recognize and prioritize the `strategic_context` passed from the orchestrator, ensuring ideas are tightly aligned with the high-level plan.
    *   **CLI Upgraded:** Two powerful new commands were added to `src/main.py`:
        *   `plan`: Allows for flexible generation of content ideas based on a time frame or a specific number.
        *   `plan-and-develop`: Executes the entire content creation workflow autonomously, from planning to final post generation.
*   **Strategic Planner Implemented (Enhancement #1):** The `BrandStrategistAgent` can now generate proactive content plans, which are accessible via the `plan-content` command.
*   **Brand Voice Reporting Implemented (Enhancement #2):** The system can now generate a comprehensive brand voice report on demand via the `report brand-voice` command.
*   **Deepened Context Passing Implemented (Enhancement #4):**
    *   **`BrandStrategistAgent` Updated:** A new `get_specialized_context` method was added to retrieve highly focused, topic-specific examples from the vector database.
    *   **`OrchestratorAgent` Updated:** The `develop_post` workflow was enhanced. It now calls the `get_specialized_context` method to provide the `CopywriterAgent` with more relevant examples, improving the quality and consistency of generated captions.
*   **Multi-Level, Color-Coded Logging Implemented and Tested:** A custom `loguru` based tracing processor has been integrated and successfully tested. It provides detailed, color-coded logs of agent activities, tool calls, LLM generations, and handoffs, significantly enhancing observability. The `OrchestratorAgent` and `BrandStrategistAgent` have been refactored to utilize this new logging system.
*   **"LLM-as-a-Judge" Quality Loop Implemented (Enhancement #5):**
    *   **`EvaluatorAgent` Created:** A new agent was created to act as a brand guardian, reviewing content for quality and adherence to brand principles.
    *   **Generic Refinement Loop:** A generic `_evaluate_and_refine_content` method was implemented in the `OrchestratorAgent`. This reusable method creates a quality control loop that can handle both string and Pydantic model outputs, ensuring all generated content undergoes a review-and-refine cycle.
    *   **Specialist Agents Updated:** The `CopywriterAgent` and `ArtDirectorAgent` were updated to handle feedback from the `EvaluatorAgent` and revise their outputs accordingly.
*   **Persistent Session Memory Implemented (Enhancement #6):**
    *   **`src/main.py` Updated:** The main CLI file was updated to manage session state using a `.active_session` file. It now includes a `session` command group (`start`, `status`, `end`, `clear`) to control the active session.
    *   **Agents Updated:** The `OrchestratorAgent` and `BrandStrategistAgent` were refactored to accept and pass an optional `session` object to the `Runner.run_sync` calls, enabling conversation history to be maintained across commands.
    *   **`.gitignore` Updated:** The `sessions.db` and `.active_session` files are now ignored by Git.
*   **Robust Session Management Implemented (Enhancement #7):**
    *   **`src/main.py` Refactored:** The session management logic was completely overhauled. It now uses a persistent `sessions.db` file and automatically creates sessions if none are active. Configuration is loaded from the `.env` file.
    *   **Token Safeguard Added:** A new utility `src/utils/token_counter.py` was created using `tiktoken`. Before commands, the system checks the session size and prompts the user with options if a token limit is exceeded, preventing high costs.
    *   **`session inspect` Command:** A new CLI command was added to allow human-readable inspection of the active session's content for easier debugging.
*   **Critical Bug Fix (`asyncio` Event Loop):**
    *   **Agent Calls Hardened:** All calls to `Runner.run_sync` across the system (in `BrandStrategistAgent` and `OrchestratorAgent`) were replaced with `asyncio.run(Runner.run(...))`. This resolves a critical bug where agent calls would fail in the synchronous Typer CLI environment.
*   **Autonomous Maestro Agent Implemented (Enhancement #8):**
    *   **`MaestroAgent` Created:** A new, high-level orchestrator (`src/agents_crew/maestro.py`) was created to serve as the primary conversational entry point to the system.
    *   **"Agents as Tools" Architecture:** The project fully adopted the "Agents as Tools" pattern. A new `src/agents_crew/tools.py` file was created to define a comprehensive toolset for the Maestro.
    *   **FunctionTools:** Key methods from the `BrandStrategistAgent` were exposed as `FunctionTool`s.
    *   **AgentTools:** All specialist agents (`CreativeDirector`, `Copywriter`, `ArtDirector`, `Reviewer`, and the new `SessionHistoryAnalystAgent`) were wrapped using `.as_tool()`.
    *   **New `maestro` Command:** A new `maestro` command was added to `src/main.py`, allowing users to interact with the system via high-level, natural language prompts.

## 3. Next Steps

With the first eight enhancements complete, the project will now proceed to the remaining items on the core enhancement roadmap.

1.  **Implement Enhancement #9: Better Agents Instructions:**
    *   `docs/enhancement_plan_9_better_agents_instructions.md`
2.  **Implement Enhancement #10: Interactive CLI Refinement Loop:** Make the refinement process conversational.
    *   `docs/enhancement_plan_10_interactive_refinement.md`
3.  **Future Phase: Web Interface:** Once the core system is enhanced, a new project will be initiated for the development of the FastAPI backend and the React frontend.

## 4. Key Decisions and Considerations

*   **"Agents as Tools" as the Primary Orchestration Pattern:** The implementation of the `MaestroAgent` solidifies the "Agents as Tools" pattern as the primary strategy for autonomous orchestration. The Maestro agent reasons and calls specialist tools, rather than relying on hard-coded Python logic. This is a key architectural shift from the deterministic `OrchestratorAgent`.
*   **Orchestration via Code Confirmed:** The decision to use code-based orchestration for the `OrchestratorAgent` has proven effective for maintaining predictability and control over the complex multi-agent workflow.
*   **Structured Outputs:** Leveraging Pydantic models for structured outputs from agents (e.g., `PostIdea`, `ImagePrompt`) simplifies data handling and ensures consistency.
*   **Modular Agent Design:** The clear separation of concerns among agents facilitates development, testing, and future modifications.
*   **Generic Refinement Loop:** The implementation of a single, generic refinement method (`_evaluate_and_refine_content`) that can handle multiple content types (strings, Pydantic models) was a key decision to maintain DRY principles and create a more robust and maintainable codebase.
*   **Synchronous Wrapper for Async Operations:** The `asyncio.run()` pattern has been established as the correct way to call async agent functions from the synchronous Typer CLI, ensuring stability. This is a critical pattern to maintain for future development.
