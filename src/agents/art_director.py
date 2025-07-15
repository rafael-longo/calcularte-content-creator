from typing import List
from pydantic import BaseModel, Field
from src.agents.base import BaseAgent

class ImagePrompt(BaseModel):
    prompt: str = Field(description="A single paragraph of text in English, detailing the image generation prompt.")

class ArtDirectorAgent(BaseAgent):
    def __init__(self):
        super().__init__()

    def generate_image_prompts(self, post_concept: str, caption: str, brand_context: dict, num_prompts: int = 3) -> List[ImagePrompt]:
        """
        Generates a series of highly detailed prompts for an image generation LLM.
        Includes a final CTA slide prompt.
        """
        formatted_context = self._format_context(brand_context)
        
        system_prompt = f"""
        You are the Art Director Agent for 'Calcularte'. Your core directive is to translate a post concept into a series of detailed, effective prompts for an image generation LLM.

        Key Responsibilities:
        1.  **Prompt Format:** Every prompt must be a **single paragraph of text in English**.
        2.  **Contextual Detail:** Do not use general terms. Be highly specific. Instead of "a craft," specify "a beautifully crocheted amigurumi fox."
        3.  **Scene Setting:** Describe the environment, background, and lighting to create a mood (e.g., `cozy studio`, `softly blurred background`, `warm and inviting light`). Mention specific props that add to the story (e.g., `a copper kettle`, `baskets of yarn`).
        4.  **Brand Palette:** Explicitly mention the brand colors in every relevant prompt, using `teal green` and `pastel pink accents`.
        5.  **Human Element:** When appropriate, include a person (e.g., `a young female artisan`) and describe their action and emotional expression (e.g., `with a gentle, slightly worried expression`, `confidently placing the final piece`).
        6.  **Embedded Text:**
            *   All text to be rendered on the image must be included in the prompt, **enclosed in double quotes** (`"..."`) and written **in Portuguese**.
            *   Specify the text's content, position (e.g., `Overlay text across the top`, `at the bottom right corner`), and desired font style (e.g., `in a large, elegant title`, `in a smaller script font`).
        7.  **CTA Slide:** The final prompt must always be for the standard CTA graphic, following the established layout and text. This CTA prompt should be the last one generated.

        Brand Context for reference:
        {formatted_context}

        Output format must be a JSON array of ImagePrompt objects.
        """

        user_message = f"""
        Generate {num_prompts} image prompts for the post concept: "{post_concept}".
        The caption for this post is: "{caption}".
        Remember to include the standard CTA slide as the last prompt.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.8, # Higher temperature for creativity
                response_model=List[ImagePrompt] # This tells the LLM to output a list of ImagePrompt objects
            )
            return response
        except Exception as e:
            print(f"Error generating image prompts: {e}")
            return []

if __name__ == "__main__":
    # Example usage (for testing purposes)
    art_director = ArtDirectorAgent()
    
    # Dummy brand context for testing
    dummy_context = {
        "brand_colors": "teal green and pastel pink accents",
        "visual_style": "clean, modern, inviting, focus on handmade products and financial clarity",
        "target_audience_visuals": "images that resonate with female artisans and small business owners"
    }

    print("Generating image prompts for 'Descomplicando a Precificação':")
    prompts = art_director.generate_image_prompts(
        post_concept="A post about simplifying pricing for artisans.",
        caption="""Sabe aquela sensação de que o dinheiro escorre pelos dedos? 💸 Com o Calcularte, você vê para onde cada centavo vai!
        
        Precificar não precisa ser um bicho de sete cabeças! 💡 A gente te ajuda a dar o preço justo e ter lucro de verdade.
        
        **Calcularte** é a ferramenta que te dá clareza e controle. Chega de trabalhar de graça! ✅
        
        O que você mais tem dificuldade na precificação? Conta pra gente nos comentários! 👇
        Salve e compartilhe este post com uma amiga empreendedora! 🚀
        (Conheça a ferramenta em) calcularte.com.br (link na bio!)
        """,
        brand_context=dummy_context,
        num_prompts=2 # Request 2 content prompts + 1 CTA prompt
    )
    
    if prompts:
        for i, prompt_obj in enumerate(prompts):
            print(f"\n--- Prompt {i+1} ---")
            print(f"Prompt: {prompt_obj.prompt}")
    else:
        print("No image prompts generated.")
