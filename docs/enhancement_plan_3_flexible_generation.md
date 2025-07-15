# Enhancement Plan 3: Enable Flexible and Autonomous Post Generation

*   **Objective:** To introduce powerful new CLI commands that allow for both flexible, user-guided content planning and fully autonomous, end-to-end post generation.

*   **Key Agent Modifications:**
    *   **`OrchestratorAgent`:**
        *   **New Method for Planning:** `plan_content_ideas(time_frame: str = None, num_ideas: int = None) -> List[PostIdea]`. This method will first call the `BrandStrategistAgent`'s `propose_content_plan` to get a strategic plan. Then, it will iterate through that plan, calling the `CreativeDirectorAgent` to generate a `PostIdea` for each strategic point.
        *   **New Method for Autonomous Generation:** `plan_and_develop_content(time_frame: str = None, num_ideas: int = None) -> List[Dict[str, Any]]`. This method will orchestrate the entire workflow autonomously. It will call `plan_content_ideas` to get the ideas, and then immediately loop through each `PostIdea`, calling `develop_post` to generate the full caption and image prompts.
    *   **`CreativeDirectorAgent`:**
        *   Ensure the `generate_ideas` method can accept the `PlannedPost` object from the `BrandStrategistAgent` as context to generate a relevant `PostIdea`.

*   **File System Changes:**
    *   **Modified:** `src/agents/orchestrator.py` (to add the new `plan_content_ideas` and `plan_and_develop_content` methods).
    *   **Modified:** `src/agents/creative_director.py` (to handle the new context type).
    *   **Modified:** `src/main.py` (to add the new high-level CLI commands).

*   **CLI Command Updates:**
    *   **New Command:** `plan`.
        *   **Usage:** `python src/main.py plan --for <time_frame>` OR `python src/main.py plan --num <number>`.
        *   **Functionality:** Triggers the `plan_content_ideas` workflow in the `OrchestratorAgent` and displays the generated `PostIdea` objects for the user to review.
        *   **Implementation Note:** The `--for` and `--num` parameters must be implemented as mutually exclusive to prevent ambiguous commands.
    *   **New Command:** `plan-and-develop`.
        *   **Usage:** `python src/main.py plan-and-develop --for <time_frame>` OR `python src/main.py plan-and-develop --num <number>`.
        *   **Functionality:** Triggers the fully autonomous `plan_and_develop_content` workflow, generating and displaying a complete content calendar with captions and image prompts.
        *   **Implementation Note:** The `--for` and `--num` parameters must be implemented as mutually exclusive.
