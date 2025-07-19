# System Patterns: Calcularte Content Engine

**Version:** 1.1
**Date:** July 15, 2025

## 1. System Architecture

The system is designed with a modular, multi-agent architecture to separate concerns and promote scalability.

*   **Backend-Centric:** The core logic resides entirely in the Python backend, ensuring that the "brains" of the operation are independent of the user interface.
*   **Multi-Agent System:** A team of specialized AI agents, managed by an Orchestrator, handles the creative workflow. This pattern allows for clear task delegation and specialized logic for each step of the content creation process.
*   **Context-Driven Tasking:** A fundamental principle where no creative agent works in isolation. The Orchestrator enriches every task with relevant brand context before delegation, ensuring all outputs are aligned with the brand voice.

## 2. Key Design Patterns

*   **Autonomous Maestro Pattern:** The `MaestroAgent` acts as the central, autonomous controller. It interprets high-level user prompts, reasons about the best course of action, and uses a toolset of other specialized agents to accomplish the task. This "Agents as Tools" pattern promotes flexibility and emergent behavior over hard-coded workflows.
*   **Single Source of Truth:** The `BrandStrategistAgent`'s functions serve as the sole guardian of brand knowledge. All context and brand-related information are funneled through its tools, preventing inconsistencies and ensuring a unified brand voice.
*   **Semantic Caching (Vector Database):** The `BrandVoiceCore` (ChromaDB) acts as a semantic cache for the brand's historical content. This allows for efficient, meaning-based retrieval of brand voice examples, which is more powerful than simple keyword matching.
*   **Structured Data-Passing:** Pydantic models are the core mechanism for ensuring lossless, high-fidelity communication between the Maestro and the specialist agents. We use structured data contracts for all critical data exchanges in the creative workflow.
    *   **`PostIdea` Model:** The `CreativeDirectorAgent` produces a `PostIdea` object. The Maestro then passes this object *unaltered* to the `CopywriterAgent`'s tool, ensuring the caption is perfectly aligned with the original vision.
    *   **`ArtDirectorInput` Model:** To create visual prompts, the `MaestroAgent` assembles an `ArtDirectorInput` object, which contains both the original `PostIdea` and the final `caption`. This gives the `ArtDirectorAgent` complete context, linking the visual execution back to the core strategy and the written word.
*   **Strict Schema Compliance:** To guarantee the reliability of our agentic system, all Pydantic models used for agent outputs or tool inputs **MUST** adhere to the strict schema rules enforced by the OpenAI Agents SDK. This is a non-negotiable principle. For detailed rules and implementation guidance, see the canonical document: [Strict Pydantic Model Compliance for Agent Outputs](./pydantic_strict_schema_rule.md).

## 3. Component Relationships

```mermaid
graph TD
    subgraph Backend (CLI)
        A[Main CLI]
    end

    subgraph "Maestro's World"
        B[Maestro Agent]
        T[Toolset]
    end

    subgraph "Specialist Agents (as Tools)"
        D[CreativeDirectorTool]
        E[CopywriterTool]
        F[ArtDirectorTool]
        G[ReviewerTool]
        J[SessionAnalystTool]
        K[ContentPlannerTool]
        L[BrandReporterTool]
    end
    
    subgraph "Function Tools"
        C[BrandStrategist Tools]
    end

    subgraph Data
        I[Brand Voice Core - ChromaDB]
    end

    A -- "maestro 'prompt'" --> B
    B -- Uses --> T
    
    T --> C
    T --> D
    T --> E
    T --> F
    T --> G
    T --> J
    T --> K
    T --> L
    
    C -- Queries --> I
```

*   The **Main CLI** receives requests via the `maestro` command and triggers the **Maestro Agent**.
*   The **Maestro Agent** uses its **Toolset** to reason and act.
*   The **Toolset** contains all available tools:
    *   **Function Tools** from the `BrandStrategist` directly query the **Brand Voice Core (ChromaDB)**.
    *   **Specialist Agents** like the `CreativeDirector`, `Copywriter`, etc., are wrapped as tools that the Maestro can invoke.
