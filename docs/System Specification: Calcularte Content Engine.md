# **System Specification: Calcularte Content Engine**

**Version:** 1.9
**Date:** July 12, 2025
**Project Lead:** (Your Name)

---

### **1. Project Overview**

The "Calcularte Content Engine" is a multi-agent AI system designed to automate the creation of high-quality, on-brand Instagram posts for the "Calcularte" brand. The system will replicate the established collaborative workflow, from brand analysis to final content generation, providing a streamlined process for personal use via a simple web interface. The core objective is to leverage AI to consistently produce creative ideas, captions, and detailed image prompts that align with Calcularte's unique brand voice.

---

### **2. System Architecture**

The system will be built on a modular architecture, separating concerns for maintainability and scalability.

* **Frontend (Web UI):** A modern, browser-based interface built with **React, styled with Tailwind CSS and DaisyUI**. This is the user's command center for initiating and refining content generation.
* **Backend (API Server):** A Python-based server built with **FastAPI** that exposes endpoints for the frontend to communicate with the agentic system.
* **Multi-Agent System (Core Logic):** The "brain" of the operation, built in Python. It consists of a primary Orchestrator Agent that manages a team of specialized agents.
* **Brand Voice Core (Vector Database):** A local vector database (e.g., ChromaDB) that stores the embeddings of Calcularte's historical posts. This is essential for enabling semantic search, allowing agents to query the *meaning* and *tone* of the brand's voice, a task not suited for traditional SQL or NoSQL databases.

---

### **3. Core Component Specifications**

#### **3.1. Brand Voice Core (Vector Database)**

* **Function:** To store and provide semantic context of the Calcularte brand voice.
* **Process:**
    1.  **Ingestion:** A one-time script will load the historical posts from the raw data files. The full dataset is located in `dataset_instagram_calcularte_profile.jsonl`, with a smaller, representative sample available in `dataset_sample.jsonl` for development and testing.
    2.  **Chunking:** The text from each post (caption) will be split into smaller, semantically meaningful chunks.
    3.  **Embedding:** Each chunk will be converted into a vector embedding using the specified embedding model.
    4.  **Storage:** The embeddings and their corresponding text chunks will be stored in a local ChromaDB database.
* **Usage:** The `BrandStrategistAgent` queries this database to retrieve relevant examples of tone, language, topics, and hashtag usage to ensure all generated content is on-brand.
* **Raw Data Source:**
    The raw data is provided in JSONL format. The primary file is `dataset_instagram_calcularte_profile.jsonl`, containing the complete history of posts. A smaller, representative sample for development and testing is available in `dataset_sample.jsonl`.
* **Example Input Data Structure:**
    The input JSONL file contains one JSON object per line, representing a single post. The system will primarily use the `caption` field for semantic voice analysis and the `hashtags` field for topic modeling. All fields should be present.
    ```json
    [
      {
        "caption": "Metade do ano já foi! 😱 E eu sei que a sensação é de pura correria. Mas agenda cheia nem sempre significa caixa cheio, certo?...",
        "images": [
          "[https://scontent-sof1-1.cdninstagram.com/v/t39.30808-6/516453486_1174886521343084_5816116690062385368_n.jpg](https://scontent-sof1-1.cdninstagram.com/v/t39.30808-6/516453486_1174886521343084_5816116690062385368_n.jpg)?..."
        ],
        "hashtags": [
          "regra8020",
          "dicadenegocio",
          "planejamento",
          "gestao",
          "julho",
          "empreendedorismofeminino",
          "artesanatolucrativo",
          "calcularte"
        ],
        "type": "Sidecar",
        "timestamp": "2025-07-07T17:25:58.000Z",
        "likesCount": 22,
        "commentsCount": 1,
        "shortCode": "DL0JxrlgGHK",
        "id": "3671602592686825930",
        "url": "[https://www.instagram.com/p/DL0JxrlgGHK/](https://www.instagram.com/p/DL0JxrlgGHK/)",
        "displayUrl": "[https://scontent-sof1-1.cdninstagram.com/v/t39.30808-6/516453486_1174886521343084_5816116690062385368_n.jpg](https://scontent-sof1-1.cdninstagram.com/v/t39.30808-6/516453486_1174886521343084_5816116690062385368_n.jpg)?..."
      },
      {
        "caption": "💗 Muita gente pensa que o Calcularte é uma \"mega corporação\"... MAS... a verdade é que, desde o início, somos só um casal (Vanessa e Rafael) por trás dessa empresa!...",
        "images": [
          "[https://scontent-lga3-3.cdninstagram.com/v/t51.29350-15/315190176_791352931970740_3725896731422150110_n.webp](https://scontent-lga3-3.cdninstagram.com/v/t51.29350-15/315190176_791352931970740_3725896731422150110_n.webp)?..."
        ],
        "hashtags": [
          "calcularte",
          "precificação",
          "appartesanato",
          "appconfeitaria",
          "negocioartesanal",
          "empreendedorismo",
          "calculovers"
        ],
        "type": "Sidecar",
        "timestamp": "2022-11-10T23:53:38.000Z",
        "likesCount": 3693,
        "commentsCount": 100,
        "shortCode": "CkzLERdui1d",
        "id": "2968765251509169501",
        "url": "[https://www.instagram.com/p/CkzLERdui1d/](https://www.instagram.com/p/CkzLERdui1d/)",
        "displayUrl": "[https://scontent-lga3-3.cdninstagram.com/v/t51.29350-15/315190176_791352931970740_3725896731422150110_n.webp](https://scontent-lga3-3.cdninstagram.com/v/t51.29350-15/315190176_791352931970740_3725896731422150110_n.webp)?..."
      }
    ]
    ```

#### **3.2. Multi-Agent System**

The system will be orchestrated by a master agent that delegates tasks to a team of specialists.

* **Orchestrator Agent:**
    * **Role:** The project manager. It receives high-level goals from the backend.
    * **Function:** Decomposes the goal into sub-tasks and delegates them to the appropriate specialist agent. It is responsible for enriching all creative tasks with relevant context from the `BrandStrategistAgent` before delegation.

* **Context-Driven Tasking Principle:**
    * A core principle of this system is that no creative agent operates in a vacuum. Before delegating a task to a specialist (e.g., `CopywriterAgent`, `ArtDirectorAgent`), the **Orchestrator Agent** first queries the **`BrandStrategistAgent`** to retrieve relevant context (e.g., examples of tone, successful hashtags, persona details). This context is then bundled with the task instructions, ensuring all generated outputs are deeply and consistently aligned with the brand voice.

* **Specialist Agents (Team Members):**
    * **`BrandStrategistAgent`:**
        * **Function:** The brand guardian and single source of truth. It queries the Brand Voice Core (vector DB) to answer questions about brand voice, target audience, content pillars, and successful patterns. It provides this context exclusively to the Orchestrator.
    * **`CreativeDirectorAgent`:**
        * **Function:** The idea generator. Tasked with brainstorming new post concepts based on a given content pillar and the specific brand context provided by the Orchestrator.
        * **Output:** A list of structured ideas, each containing a Title, Content Pillar, Defense of Idea, and Expected Results.
    * **`CopywriterAgent`:**
        * **Function:** The writer. It receives a developed idea and writes the full, detailed Instagram caption, using the specific brand voice context and examples provided by the Orchestrator.
    * **`ArtDirectorAgent`:**
        * **Function:** The visual designer. It receives the post concept and caption, and generates a series of highly detailed prompts for an image generation LLM, using the post's concept and brand context provided by the Orchestrator.
    * **`ReviewerAgent`:**
        * **Function:** The quality control specialist. It takes a piece of generated content, user feedback, and relevant brand context from the Orchestrator to produce a precise, revised version.

#### **3.3. Backend (API Server - Python/FastAPI)**

* **Function:** To handle HTTP requests from the frontend and trigger the Orchestrator Agent.
* **Key Endpoints:**
    * `POST /api/ingest_brand_data`: Triggers the initial ingestion of the historical posts into the vector database.
    * `POST /api/generate_ideas`: Takes a topic or pillar as input, triggers the `CreativeDirectorAgent`, and returns a list of post ideas.
    * `POST /api/develop_idea`: Takes a selected idea title as input, triggers the full workflow (caption + prompts), and returns the complete post plan.
    * `POST /api/refine_component`: Takes a component (e.g., "caption", "prompt_3") and user feedback text as input, triggers the `ReviewerAgent`, and returns the refined content.

#### **3.4. Frontend (Web UI)**

* **Function:** A simple, intuitive interface for the user to manage the content creation process.
* **Key Pages/Sections:**
    * **Brand Setup:** A simple page with a file upload button to trigger the `/ingest_brand_data` endpoint.
    * **Dashboard:** The main workspace.
        * A button: "Gerar Novas Ideias de Post".
        * An area to display the generated ideas (Title, Defense). The user can click a "Desenvolver esta ideia" button on their chosen idea.
        * An area to display the fully developed post plan:
            * The complete caption is shown in a large, editable text area.
            * Each image prompt is shown in its own editable text area.
            * Next to each text area, a "Refinar" button allows the user to provide feedback and trigger the `/refine_component` endpoint for that specific part.

---

### **4. Key Workflow: Generating a New Post**

1.  User clicks "Gerar Novas Ideias de Post" on the UI.
2.  Frontend sends a request to `POST /api/generate_ideas`.
3.  Backend instructs the **Orchestrator Agent** with the goal: "Generate 3 new post ideas aligned with the brand voice."
4.  Orchestrator first queries the **`BrandStrategistAgent`** for key themes and successful patterns.
5.  Orchestrator then tasks the **`CreativeDirectorAgent`** with the goal, providing the retrieved context. The agent generates 3 ideas and returns them.
6.  Orchestrator returns the ideas to the Backend, which sends them to the Frontend.
7.  User selects an idea and clicks "Desenvolver esta ideia".
8.  Frontend sends a request to `POST /api/develop_idea` with the chosen idea.
9.  Orchestrator again queries the **`BrandStrategistAgent`** for relevant context (e.g., tone, language examples).
10. Orchestrator tasks the **`CopywriterAgent`** and **`ArtDirectorAgent`** with their respective goals, providing the necessary brand context to both.
11. The agents complete their tasks. The Orchestrator assembles the full plan and returns it.
12. The Frontend displays the full caption and all image prompts in their respective editable fields.

---

### **5. Proposed Technology Stack**

* **Language:** Python 3.10+
* **Backend Framework:** **FastAPI**
* **Agent/LLM Framework:** **OpenAI's Agents SDK**
* **Vector Database:** ChromaDB (for ease of local setup)
* **Embedding Model:** **OpenAI's `text-embedding-3-small` model**.
* **Core LLM:** **`gpt-4.1-mini`** via OpenAI's API.
* **Frontend:** **React** with **Tailwind CSS** and **DaisyUI**.
