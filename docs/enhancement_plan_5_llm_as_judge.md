# Enhancement Plan 5: Implement an "LLM-as-a-Judge" Quality Loop

*   **Objective:** To implement an automated quality control loop that uses an "LLM-as-a-Judge" to review and request self-correction on generated content before it is presented to the user.

*   **Key Agent Modifications:**
    *   **New Agent: `EvaluatorAgent`**
        *   **Pydantic Model for Evaluation:**
            ```python
            from pydantic import BaseModel
            from typing import Literal

            class EvaluationResult(BaseModel):
                verdict: Literal["approved", "needs_improvement"]
                feedback: str
            ```
        *   **Method:** `evaluate_content(content: str, content_type: str, brand_principles: str) -> EvaluationResult`.
        *   **Method Logic:** This agent will receive the generated content (e.g., a caption), its type, and a summary of the brand voice principles. It will be prompted to act as a strict brand guardian and judge whether the content adheres to the principles. It will return an `EvaluationResult` object.
    *   **`OrchestratorAgent`:**
        *   **Modified Workflow:** After a specialist agent (e.g., `CopywriterAgent`) generates content, the `OrchestratorAgent` will enter a quality loop.
        *   **Loop Logic:**
            1.  Pass the generated content to the `EvaluatorAgent`.
            2.  If the `verdict` is "approved," exit the loop and proceed.
            3.  If the `verdict` is "needs_improvement," send the content back to the original creator agent along with the `feedback` from the `EvaluatorAgent`, requesting a revision.
            4.  Repeat the loop up to a maximum number of retries (e.g., 2) to prevent infinite loops.
    *   **`CopywriterAgent` / `ArtDirectorAgent`:**
        *   Modify their primary methods to accept an optional `feedback_for_revision` parameter, allowing them to refine their previous output based on the evaluator's feedback.

*   **File System Changes:**
    *   **New File:** `src/agents/evaluator.py` (to define the new `EvaluatorAgent`).
    *   **Modified:** `src/agents/orchestrator.py` (to implement the new quality control loop).
    *   **Modified:** `src/agents/copywriter.py` and `src/agents/art_director.py` (to handle revision requests).

*   **CLI Command Updates:**
    *   No direct CLI changes are needed. This internal improvement enhances the quality of all content generation commands. An optional flag like `--skip-evaluation` could be added for debugging or speed if necessary.
