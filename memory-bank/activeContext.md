# Active Context: Calcularte Content Engine

**Version:** 1.1
**Date:** July 15, 2025

## 1. Current Focus

The current focus has been on the successful implementation of the core backend and command-line interface (CLI) for the "Calcularte Content Engine." This phase involved building out the multi-agent system and integrating it for a complete post-generation workflow.

## 2. Recent Changes

*   **Full Multi-Agent System Implemented:**
    *   `src/agents/base.py`: Created a `BaseAgent` class for common LLM interaction and context formatting.
    *   `src/agents/creative_director.py`: Implemented the `CreativeDirectorAgent` for brainstorming structured post ideas using Pydantic for output.
    *   `src/agents/copywriter.py`: Implemented the `CopywriterAgent` to write detailed Instagram captions adhering to brand voice and formatting.
    *   `src/agents/art_director.py`: Implemented the `ArtDirectorAgent` to generate specific image prompts, including a CTA slide.
    *   `src/agents/reviewer.py`: Implemented the `ReviewerAgent` to refine content based on user feedback.
    *   `src/agents/orchestrator.py`: Implemented the `OrchestratorAgent` as the central coordinator, fetching brand context and orchestrating calls to other specialist agents for post generation and refinement.
*   **CLI Updated:** The `src/main.py` CLI now exposes the full post-generation workflow with new commands:
    *   `plan-content <time_frame>`
    *   `generate-ideas <pillar> [--num <n>]`
    *   `develop-post <idea_title> <idea_pillar> <idea_defense> <idea_results> [--num-images <n>]`
    *   `refine-content <component_type> <original_content> <user_feedback> [--context-query <query>]`
*   **Strategic Planner Implemented:** Enhancement #1 is complete. The `BrandStrategistAgent` can now generate proactive content plans, which are accessible via the new `plan-content` command.
*   **Brand Voice Reporting Implemented:** Enhancement #2 is complete. The system can now generate a comprehensive brand voice report on demand via the `report brand-voice` command.

## 3. Next Steps

With the first two enhancements complete, the project will now proceed to the next item on the enhancement roadmap.

1.  **Implement Enhancement #3:** The immediate next step is to implement the "Enable Flexible and Autonomous Post Generation" enhancement as detailed in:
    *   `docs/enhancement_plan_3_flexible_generation.md`
2.  **Continue Roadmap:** After that, continue with the remaining enhancements:
    *   `docs/enhancement_plan_4_context_passing.md`
    *   `docs/enhancement_plan_5_llm_as_judge.md`
    *   `docs/enhancement_plan_6_session_memory.md`
    *   `docs/enhancement_plan_7_interactive_refinement.md`
2.  **Future Phase: Web Interface:** Once the core system is enhanced, the project will proceed with the development of the FastAPI backend and the React frontend.

## 4. Key Decisions and Considerations

*   **Orchestration via Code Confirmed:** The decision to use code-based orchestration for the `OrchestratorAgent` has proven effective for maintaining predictability and control over the complex multi-agent workflow.
*   **Structured Outputs:** Leveraging Pydantic models for structured outputs from agents (e.g., `PostIdea`, `ImagePrompt`) simplifies data handling and ensures consistency.
*   **Modular Agent Design:** The clear separation of concerns among agents facilitates development, testing, and future modifications.
