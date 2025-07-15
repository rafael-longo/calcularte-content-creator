from src.agents.base import BaseAgent

class ReviewerAgent(BaseAgent):
    def __init__(self):
        super().__init__()

    def refine_content(self, original_content: str, user_feedback: str, brand_context: dict) -> str:
        """
        Performs precise, targeted revisions on existing content based on user feedback.
        """
        formatted_context = self._format_context(brand_context)
        
        system_prompt = f"""
        You are the Reviewer Agent for 'Calcularte'. Your core directive is to perform precise, targeted revisions on existing content based on user feedback.

        Key Responsibilities:
        1.  **Interpret Feedback:** Analyze the user's instructions for refinement (e.g., "make this more inclusive," "add more detail").
        2.  **Contextual Editing:** Your revision must incorporate three inputs:
            *   The original text.
            *   The user's feedback.
            *   The relevant brand voice context provided by the Orchestrator.
        3.  **Surgical Changes:** Do not regenerate the content from scratch. Your goal is to modify the original piece to meet the new requirements while preserving the parts that were already correct.

        Brand Context for reference:
        {formatted_context}
        """

        user_message = f"""
        Original Content to revise:
        ---
        {original_content}
        ---

        User Feedback:
        ---
        {user_feedback}
        ---

        Please provide the revised content.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        response = self._call_llm(messages, temperature=0.5, max_tokens=500) # Lower temperature for less creativity, more adherence
        return response

if __name__ == "__main__":
    # Example usage (for testing purposes)
    reviewer = ReviewerAgent()
    
    # Dummy brand context for testing
    dummy_context = {
        "tone_voice": "empathetic, acolhedora, didática, inspiradora",
        "target_audience": "artesãs e confeiteiras",
    }

    original_caption = """
    Sabe aquela sensação de que o dinheiro escorre pelos dedos? 💸 Com o Calcularte, você vê para onde cada centavo vai!
    Precificar não precisa ser um bicho de sete cabeças! 💡 A gente te ajuda a dar o preço justo e ter lucro de verdade.
    **Calcularte** é a ferramenta que te dá clareza e controle. Chega de trabalhar de graça! ✅
    O que você mais tem dificuldade na precificação? Conta pra gente nos comentários! 👇
    Salve e compartilhe este post com uma amiga empreendedora! 🚀
    (Conheça a ferramenta em) calcularte.com.br (link na bio!)
    """
    user_feedback = "Can you make the language a bit more direct and less informal? Also, emphasize the 'control' aspect more."

    print("Refining content:")
    revised_content = reviewer.refine_content(original_caption, user_feedback, dummy_context)
    print(revised_content)
