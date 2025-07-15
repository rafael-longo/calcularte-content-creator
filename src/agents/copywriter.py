from src.agents.base import BaseAgent

class CopywriterAgent(BaseAgent):
    def __init__(self):
        super().__init__()

    def write_caption(self, idea_title: str, idea_defense: str, brand_context: dict) -> str:
        """
        Writes a full, detailed Instagram caption based on a developed idea and brand context.
        """
        formatted_context = self._format_context(brand_context)
        
        system_prompt = f"""
        You are the Copywriter Agent for 'Calcularte'. Your core directive is to write compelling, empathetic, and valuable Instagram captions.

        Adhere strictly to the "amiga especialista" voice: empathetic, acolhedora (welcoming), didática (didactic), e inspiradora (inspiring). Use a friendly, colloquial Portuguese.

        Caption Structure:
        - Start with a hook that captures a core pain point or feeling of the "Calculover" (our target audience).
        - Develop the body of the text to educate and provide value.
        - Seamlessly connect the problem/solution to a feature or benefit of the Calcularte tool.
        - End with a clear Call to Action (CTA).

        Formatting:
        - Use emojis strategically to add emotion and break up text (e.g., ✨, 💡, 💰, 🩷, 🚀, ✅).
        - Use bolding (`**text**`) to highlight key concepts.
        - Keep paragraphs short and easy to read on mobile.

        Call to Action (CTA) - Standard Format:
        - An engaging question for the comments.
        - A directive to Save and/or Share the post.
        - A final call to visit the website: `(Conheça a ferramenta em) calcularte.com.br (link na bio!)`.

        Brand Context for reference:
        {formatted_context}
        """

        user_message = f"""
        Write an Instagram caption for the idea titled: "{idea_title}".
        The defense of this idea is: "{idea_defense}".
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        response = self._call_llm(messages, temperature=0.7, max_tokens=500)
        return response

if __name__ == "__main__":
    # Example usage (for testing purposes)
    copywriter = CopywriterAgent()
    
    # Dummy brand context for testing
    dummy_context = {
        "tone_voice": "empathetic, acolhedora, didática, inspiradora",
        "target_audience": "artesãs e confeiteiras, empreendedoras, buscam organização financeira e precificação justa",
        "content_pillars": ["Precificação", "Organização Financeira"],
        "successful_patterns": ["dicas práticas", "histórias de sucesso", "perguntas e respostas"],
        "examples_of_tone": [
            "Sabe aquela sensação de que o dinheiro escorre pelos dedos? 💸 Com o Calcularte, você vê para onde cada centavo vai!",
            "Precificar não precisa ser um bicho de sete cabeças! 💡 A gente te ajuda a dar o preço justo e ter lucro de verdade."
        ]
    }

    print("Writing caption for 'Descomplicando a Precificação':")
    caption = copywriter.write_caption(
        idea_title="Descomplicando a Precificação: Seu Lucro na Ponta do Lápis!",
        idea_defense="Muitas artesãs têm dificuldade em precificar corretamente, o que afeta a lucratividade. Este post oferece dicas práticas e mostra como o Calcularte simplifica isso.",
        brand_context=dummy_context
    )
    print(caption)
