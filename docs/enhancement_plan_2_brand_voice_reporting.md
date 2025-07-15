# **Enhancement Plan 2: Implement On-Demand Brand Voice Reporting**

* **Objective:** To empower the `BrandStrategistAgent` to perform a holistic analysis of the brand's voice and generate a comprehensive, human-readable report on demand.

* **Key Agent Modifications:**

    * **`BrandStrategistAgent`:**
        * **New Pydantic Models:**
            ```python
            from pydantic import BaseModel
            from typing import List, Dict

            class BrandVoiceReport(BaseModel):
                executive_summary: str
                key_content_pillars: List[Dict[str, str]] # e.g., [{"pillar": "Humor", "description": "..."}]
                audience_persona_summary: str
                tone_of_voice_analysis: str
                language_style_details: str # Includes emoji and colloquialism usage
                hashtag_strategy_summary: str
            ```
        * **New Method:** `generate_brand_voice_report() -> BrandVoiceReport`.
        * **Method Logic:** This method will be prompted to analyze the entire Brand Voice Core. The prompt will guide the LLM to perform a step-by-step synthesis:
            1.  **Holistic Sampling:** "First, retrieve a diverse sample of at least 20-30 posts, ensuring examples from different content pillars (like Humor, Educação, Sazonalidade) are included to form a balanced view."
            2.  **Synthesize Findings:** "Next, analyze the sampled content to synthesize findings on key content pillars, the 'Calculover' audience persona, tone of voice, language style (including common emojis and colloquialisms), and successful hashtag strategies."
            3.  **Structured Output:** "Finally, structure the complete analysis into the `BrandVoiceReport` JSON format."

    * **`OrchestratorAgent`:**
        * **New Method:** Add a new method to trigger the `generate_brand_voice_report` method on the `BrandStrategistAgent`.
        * **Formatting Responsibility:** This method will receive the `BrandVoiceReport` Pydantic object and will be responsible for formatting its contents into a clean, human-readable Markdown report before returning it as the final output.

* **File System Changes:**
    * **Modified:** `src/agents/brand_strategist.py` (to add the new Pydantic model and method).
    * **Modified:** `src/agents/orchestrator.py` (to handle the report generation and formatting workflow).
    * **Modified:** `src/main.py` (to add the new CLI command).

* **CLI Command Updates:**
    * **New Command:** `report brand-voice`.
    * **Usage:** `python src/main.py report brand-voice`. This will trigger the new reporting workflow and print a well-structured Markdown report to the console.
