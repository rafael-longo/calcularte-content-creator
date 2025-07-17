# Active Context: Calcularte Content Engine

**Version:** 1.1
**Date:** July 15, 2025

## 1. Current Focus

The current focus has been on the successful implementation of the core backend and command-line interface (CLI) for the "Calcularte Content Engine." This phase involved building out the multi-agent system and integrating it for a complete post-generation workflow.

## 2. Recent Changes

*   **"LLM-as-a-Judge" Quality Loop:** An `EvaluatorAgent` exists to act as a brand guardian, reviewing content for quality and adherence to brand principles. It is not yet integrated into the Maestro's toolset.
*   **Persistent Session Memory Implemented (Enhancement #6):**
    *   **`src/main.py` Updated:** The main CLI file was updated to manage session state using a `.active_session` file. It now includes a `session` command group (`start`, `status`, `end`, `clear`) to control the active session.
    *   **Agents Updated:** The agents were refactored to accept and pass an optional `session` object to the `Runner.run_sync` calls, enabling conversation history to be maintained across commands.
    *   **`.gitignore` Updated:** The `sessions.db` and `.active_session` files are now ignored by Git.
*   **Robust Session Management Implemented (Enhancement #7):**
    *   **`src/main.py` Refactored:** The session management logic was completely overhauled. It now uses a persistent `sessions.db` file and automatically creates sessions if none are active. Configuration is loaded from the `.env` file.
    *   **Token Safeguard Added:** A new utility `src/utils/token_counter.py` was created using `tiktoken`. Before commands, the system checks the session size and prompts the user with options if a token limit is exceeded, preventing high costs.
    *   **`session inspect` Command:** A new CLI command was added to allow human-readable inspection of the active session's content for easier debugging.
*   **Critical Bug Fix (`asyncio` Event Loop):**
    *   **Agent Calls Hardened:** All calls to `Runner.run_sync` across the system were replaced with `asyncio.run(Runner.run(...))`. This resolves a critical bug where agent calls would fail in the synchronous Typer CLI environment.
*   **Autonomous Maestro Agent Implemented (Enhancement #8):**
    *   **`MaestroAgent` Created:** A new, high-level orchestrator (`src/agents_crew/maestro.py`) was created to serve as the primary conversational entry point to the system.
    *   **"Agents as Tools" Architecture:** The project fully adopted the "Agents as Tools" pattern. A new `src/agents_crew/tools.py` file was created to define a comprehensive toolset for the Maestro.
    *   **FunctionTools:** Key methods from the `BrandStrategistAgent` were exposed as `FunctionTool`s.
    *   **AgentTools:** All specialist agents (`CreativeDirector`, `Copywriter`, `ArtDirector`, `Reviewer`, and the new `SessionHistoryAnalystAgent`) were wrapped using `.as_tool()`.
    *   **New `maestro` Command:** A new `maestro` command was added to `src/main.py`, allowing users to interact with the system via high-level, natural language prompts.
*   **Enhanced Agent Instructions and Creativity Implemented (Enhancement #9):**
    *   **`MaestroAgent` Enhanced:** Instructions were overhauled to embody the "Amiga Especialista" persona, promoting a more strategic, context-aware, and empathetic approach to orchestration.
    *   **`CreativeDirectorAgent` Enhanced:** Instructions were updated with "Creative Mandates" to encourage diverse content formats and avoid clichés.
    *   **`EvaluatorAgent` Enhanced:** Instructions were updated to include specific brand principles, making the quality control loop more aligned with Calcularte's core values.
    *   **`ArtDirectorAgent` Enhanced:** The agent's workflow was transformed into a two-step process: creating a visual storyboard and then generating prompts, allowing for more dynamic and narrative-driven carousel planning.
    *   **"Creative Wildcard" System Implemented:** A new `propose_wildcard_angle` tool was added to the `MaestroAgent`'s toolset, enabling the generation of unexpected and highly creative post angles to break out of creative ruts.

## 3. Next Steps

With the first nine enhancements complete, the project will now proceed to the final item on the core enhancement roadmap.

1.  **Implement Enhancement #10: Interactive CLI Refinement Loop:** Make the refinement process conversational.
    *   `docs/enhancement_plan_10_interactive_refinement.md`
2.  **Future Phase: Web Interface:** Once the core system is enhanced, a new project will be initiated for the development of the FastAPI backend and the React frontend.

## 4. Key Decisions and Considerations

*   **"Agents as Tools" as the Primary Orchestration Pattern:** The implementation of the `MaestroAgent` solidifies the "Agents as Tools" pattern as the primary strategy for autonomous orchestration. The Maestro agent reasons and calls specialist tools, rather than relying on hard-coded Python logic.
*   **Structured Outputs:** Leveraging Pydantic models for structured outputs from agents simplifies data handling and ensures consistency.
*   **Modular Agent Design:** The clear separation of concerns among agents facilitates development, testing, and future modifications.
*   **Synchronous Wrapper for Async Operations:** The `asyncio.run()` pattern has been established as the correct way to call async agent functions from the synchronous Typer CLI, ensuring stability. This is a critical pattern to maintain for future development.
