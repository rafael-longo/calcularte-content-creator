# System Patterns: Calcularte Content Engine

**Version:** 1.1
**Date:** July 15, 2025

## 1. System Architecture

The system is designed with a modular, multi-agent architecture to separate concerns and promote scalability.

*   **Backend-Centric:** The core logic resides entirely in the Python backend, ensuring that the "brains" of the operation are independent of the user interface.
*   **Multi-Agent System:** A team of specialized AI agents, managed by an Orchestrator, handles the creative workflow. This pattern allows for clear task delegation and specialized logic for each step of the content creation process.
*   **Context-Driven Tasking:** A fundamental principle where no creative agent works in isolation. The Orchestrator enriches every task with relevant brand context before delegation, ensuring all outputs are aligned with the brand voice.

## 2. Key Design Patterns

*   **Orchestrator-Worker Pattern:** The `OrchestratorAgent` acts as the central controller, decomposing high-level goals into sub-tasks and delegating them to a team of worker agents (`CreativeDirectorAgent`, `CopywriterAgent`, etc.). This pattern centralizes control and simplifies the workflow logic.
*   **Single Source of Truth:** The `BrandStrategistAgent` serves as the sole guardian of brand knowledge. All context and brand-related information are funneled through this agent, preventing inconsistencies and ensuring a unified brand voice.
*   **Semantic Caching (Vector Database):** The `BrandVoiceCore` (ChromaDB) acts as a semantic cache for the brand's historical content. This allows for efficient, meaning-based retrieval of brand voice examples, which is more powerful than simple keyword matching.
*   **Structured Outputs:** Pydantic models are used to define the expected output format for agents like `CreativeDirectorAgent` and `ArtDirectorAgent`, ensuring consistent and machine-readable results.

## 3. Component Relationships

```mermaid
graph TD
    subgraph Backend (CLI / FastAPI)
        A[Main CLI / API Endpoints]
    end

    subgraph Multi-Agent System
        B[Orchestrator Agent]
        C[BrandStrategistAgent]
        D[CreativeDirectorAgent]
        E[CopywriterAgent]
        F[ArtDirectorAgent]
        G[ReviewerAgent]
        H[BaseAgent (Common Utilities)]
    end

    subgraph Data
        I[Brand Voice Core - ChromaDB]
    end

    A --> B
    B --> C
    B --> D
    B --> E
    B --> F
    B --> G
    C --> I
    D --> H
    E --> H
    F --> H
    G --> H
```

*   The **Main CLI / API Endpoints** receive requests and trigger the **Orchestrator Agent**.
*   The **Orchestrator Agent** queries the **BrandStrategistAgent** for context.
*   The **BrandStrategistAgent** queries the **Brand Voice Core** to retrieve relevant information.
*   The **Orchestrator Agent** delegates tasks to the other specialist agents (`CreativeDirectorAgent`, `CopywriterAgent`, `ArtDirectorAgent`, `ReviewerAgent`), providing them with the necessary context.
*   All specialist agents inherit from `BaseAgent` for common functionalities.
