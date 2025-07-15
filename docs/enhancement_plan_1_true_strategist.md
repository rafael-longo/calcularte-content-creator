# **Enhancement Plan 1: Evolve `BrandStrategistAgent` to True Strategist**

* **Objective:** To transform the `BrandStrategistAgent` from a reactive data retriever into a proactive, strategic planner capable of generating flexible, context-aware content plans.

* **Key Agent Modifications:**

    * **`BrandStrategistAgent`:**
        * **New Pydantic Models:** Define structured outputs for clarity and reliability.
            ```python
            from pydantic import BaseModel
            from typing import List, Optional
            from datetime import date

            class PlannedPost(BaseModel):
                day_or_sequence: str # e.g., "Monday", "Post 1"
                pillar: str
                reasoning: str

            class ContentPlan(BaseModel):
                plan: List[PlannedPost]
            ```
        * **New Method:** Add a new method: `propose_content_plan(time_frame: str, current_date: date, recent_post_themes: Optional[list] = None) -> ContentPlan`.
        * **Method Logic:** This method will contain a sophisticated system prompt instructing the LLM to perform a step-by-step analysis and return a `ContentPlan` object. The core logic for the prompt will be:
            1.  **Analyze Time & Seasonality:** "Based on the `current_date` and the requested `time_frame`, identify key seasonal opportunities (e.g., 'Dia dos Pais', 'Inverno', 'Black Friday')."
            2.  **Ensure Variety:** "Review the `recent_post_themes` to avoid suggesting topics that have been posted recently."
            3.  **Identify Top Pillars:** "Analyze the provided brand context to determine the most historically engaging content pillars (e.g., Humor, Educação, Sazonalidade)."
            4.  **Synthesize Plan:** "Combine these insights to create a balanced and timely content plan. Prioritize seasonal content if relevant. For a weekly plan, assign a pillar to each key posting day. For a numeric plan, create a diverse sequence. Justify each choice in the 'reasoning' field."

    * **`OrchestratorAgent`:**
        * Modify existing methods or add new ones to call the new `propose_content_plan` method on the `BrandStrategistAgent`, passing the required parameters.

* **File System Changes:**
    * **Modified:** `src/agents/brand_strategist.py` (to add the new Pydantic models and the `propose_content_plan` method).
    * **Modified:** `src/agents/orchestrator.py` (to integrate the new strategic planning capability).
    * **Modified:** `src/main.py` (to expose this new functionality via a new CLI command).

* **CLI Command Updates:**
    * **New Command:** A new command, `plan-content`, will be added to `src/main.py`. This command will trigger the new strategic planning workflow in the `OrchestratorAgent`.
    * **Usage:** `python src/main.py plan-content --for <time_frame>`, where `<time_frame>` can be "today", "week", "month", etc.
