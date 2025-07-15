# Calcularte Content Engine: CLI User Manual

This manual provides instructions for using the Command-Line Interface (CLI) of the Calcularte Content Engine. This tool allows you to generate and refine Instagram post content using an AI-powered multi-agent system.

---

## 1. Setup and Installation

Before using the CLI, ensure you have Python 3.11.8 and `pyenv` installed.

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/rafael-longo/calcularte-content-creator.git
    cd calcularte-content-creator
    ```

2.  **Set up Python Environment (using pyenv):**
    ```bash
    pyenv virtualenv 3.11.8 venv-calcularte-content-creator
    pyenv local venv-calcularte-content-creator
    ```
    This will create a `.python-version` file in your project directory, ensuring the virtual environment is automatically activated when you navigate into this folder.

3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set OpenAI API Key:**
    Create a file named `.env` in the root of the project directory and add your OpenAI API key:
    ```
    OPENAI_API_KEY=sk-YOUR_OPENAI_API_KEY_HERE
    ```
    Replace `sk-YOUR_OPENAI_API_KEY_HERE` with your actual OpenAI API key.

---

## 2. Core CLI Commands

All commands are executed using `python src/main.py <command>`.

### 2.1. `ingest` - Ingest Brand Data

This command loads historical Instagram post data into the ChromaDB vector database, which the `BrandStrategistAgent` uses to understand the Calcularte brand voice.

**Usage:**

```bash
python src/main.py ingest [--sample | --full]
```

*   `--sample`: (Default) Ingests data from `dataset_sample.jsonl`. This is recommended for quick testing and development.
*   `--full`: Ingests data from `dataset_instagram_calcularte_profile.jsonl`. This contains the full dataset and may take longer.

**Example:**

```bash
python src/main.py ingest --sample
```

### 2.2. `plan-content` - Generate a Strategic Content Plan

This command leverages the enhanced `BrandStrategistAgent` to generate a proactive, strategic content plan for a specified time frame. It considers seasonality, historical performance, and content variety.

**Usage:**

```bash
python src/main.py plan-content "<time_frame>"
```

*   `<time_frame>`: The duration for the content plan (e.g., "week", "month", "quarter"). Enclose in quotes if it contains spaces.

**Example:**

```bash
python src/main.py plan-content "week"
```

### 2.3. `ask-strategist` - Query Brand Strategist

This command allows you to query the `BrandStrategistAgent` to retrieve content from the brand's historical data that is semantically similar to your query. This is useful for understanding the brand's tone, style, and relevant topics.

**Usage:**

```bash
python src/main.py ask-strategist "<your_query_text>"
```

*   `<your_query_text>`: The text query you want to use to find relevant brand content. Enclose in quotes if it contains spaces.

**Example:**

```bash
python src/main.py ask-strategist "Como organizar as finanças do meu negócio artesanal?"
```

### 2.4. `generate-ideas` - Generate New Post Ideas

This command uses the `CreativeDirectorAgent` (orchestrated by the `OrchestratorAgent`) to brainstorm new Instagram post concepts based on a specified content pillar.

**Usage:**

```bash
python src/main.py generate-ideas "<content_pillar>" [--num <number_of_ideas>]
```

*   `<content_pillar>`: The main topic or strategic category for the post ideas (e.g., "Organização Financeira", "Precificação", "Marketing para Artesanato"). Enclose in quotes if it contains spaces.
*   `--num <number_of_ideas>`: (Optional) The number of ideas to generate. Defaults to 3.

**Example:**

```bash
python src/main.py generate-ideas "Produtividade para Artesãs" --num 2
```

### 2.4. `develop-post` - Develop a Full Post

This command takes a selected post idea (title, pillar, defense, and expected results) and uses the `OrchestratorAgent` to generate a complete Instagram caption (via `CopywriterAgent`) and a series of detailed image prompts (via `ArtDirectorAgent`).

**Usage:**

```bash
python src/main.py develop-post "<idea_title>" "<idea_pillar>" "<idea_defense>" "<idea_results>" [--num-images <number_of_content_images>]
```

*   `<idea_title>`: The catchy title of the post idea.
*   `<idea_pillar>`: The content pillar of the idea.
*   `<idea_defense>`: A brief justification for the idea.
*   `<idea_results>`: The expected outcomes of the post.
*   `--num-images <number_of_content_images>`: (Optional) The number of content image prompts to generate. The system will automatically add one final CTA slide prompt. Defaults to 3 content image prompts.

**Important:** Ensure you enclose each argument in quotes if it contains spaces.

**Example (using an idea generated from `generate-ideas`):**

```bash
python src/main.py develop-post "Descomplicando a Precificação: Seu Lucro na Ponta do Lápis!" "Precificação" "Este post oferece dicas práticas e mostra como o Calcularte simplifica a precificação para artesãs." "Aumentar o engajamento e direcionar tráfego para o Calcularte." --num-images 2
```

### 2.6. `refine-content` - Refine Content with Feedback

This command allows you to refine a specific piece of generated content (like a caption or an image prompt) using the `ReviewerAgent` (orchestrated by the `OrchestratorAgent`) based on your feedback.

**Usage:**

```bash
python src/main.py refine-content "<component_type>" "<original_content>" "<user_feedback>" [--context-query "<query_for_context>"]
```

*   `<component_type>`: The type of content to refine. Currently supported: `caption` or `prompt`.
*   `<original_content>`: The full text of the content you want to refine. Enclose in quotes.
*   `<user_feedback>`: Your specific feedback or instructions for refinement. Enclose in quotes.
*   `--context-query "<query_for_context>"`: (Optional) A query to help the `ReviewerAgent` fetch additional relevant brand context for the refinement. If not provided, the `original_content` will be used as the context query.

**Example (refining a caption):**

```bash
python src/main.py refine-content caption "Sabe aquela sensação de que o dinheiro escorre pelos dedos? 💸 Com o Calcularte, você vê para onde cada centavo vai! Precificar não precisa ser um bicho de sete cabeças! 💡 A gente te ajuda a dar o preço justo e ter lucro de verdade. **Calcularte** é a ferramenta que te dá clareza e controle. Chega de trabalhar de graça! ✅ O que você mais tem dificuldade na precificação? Conta pra gente nos comentários! 👇 Salve e compartilhe este post com uma amiga empreendedora! 🚀 (Conheça a ferramenta em) calcularte.com.br (link na bio!)" "Make the call to action more direct and add a strong sense of urgency."
```

---

This manual covers all current functionalities of the Calcularte Content Engine CLI. For any issues or further development, please refer to the project's system specifications and agent instruction set documentation.
