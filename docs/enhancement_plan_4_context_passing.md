# Enhancement Plan 4: Deepen and Formalize Inter-Agent Context Passing

*   **Objective:** To make inter-agent context passing more intelligent and specific, ensuring specialist agents receive highly relevant, pre-digested information.

*   **Key Agent Modifications:**
    *   **`BrandStrategistAgent`:**
        *   **New Method:** `get_specialized_context(context_type: str, query: str, num_samples: int = 3) -> List[str]`.
        *   **Method Logic:** This method will accept a `context_type` (e.g., "empathetic_captions", "humorous_posts", "seasonal_examples") and use it to craft a highly specific query for the vector database. It will retrieve `num_samples` of the most relevant historical posts that match the requested context type.
    *   **`OrchestratorAgent`:**
        *   **Modified Logic:** Before calling specialist agents like `CopywriterAgent` or `ArtDirectorAgent`, the `OrchestratorAgent` will first call the `BrandStrategistAgent`'s `get_specialized_context` method.
        *   **Example Workflow:** When preparing to call the `CopywriterAgent`, the `OrchestratorAgent` might first call `get_specialized_context(context_type="empathetic_captions", query="post about mother's day")`. It will then pass the returned list of empathetic captions as focused context to the `CopywriterAgent`.

*   **File System Changes:**
    *   **Modified:** `src/agents/brand_strategist.py` (to add the new `get_specialized_context` method).
    *   **Modified:** `src/agents/orchestrator.py` (to integrate this more intelligent context-gathering step into its existing workflows).

*   **CLI Command Updates:**
    *   There are no direct CLI changes for this enhancement. This is an internal architectural improvement that will enhance the quality of the output from existing and future commands.
