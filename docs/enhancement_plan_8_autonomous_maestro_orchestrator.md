# **Enhancement Plan 8: Implement the Autonomous Maestro Agent**

* **Objective:** To create a single, powerful, conversational entry point to the system (maestro command) managed by an autonomous MaestroAgent. This agent will interpret high-level user prompts and orchestrate the system's full capabilities by using specialist agents and functions as tools. This enhancement consolidates the goals of the previous plans for session querying and context-aware refinement.  
* **Core SDK Pattern: "Agents as Tools"**  
  * The MaestroAgent will be the primary agent that maintains control and uses other agents as tools to gather information and perform actions, as described in the OpenAI Agents SDK documentation.  
* **Key Sub-Tasks & Agent Modifications:**  
  1. **Create the MaestroAgent:**  
     * **Role:** The master project manager and central reasoner.  
     * **Instructions:** The system prompt will instruct the agent to deconstruct the user's prompt, plan a sequence of actions, execute the plan using its tools, and synthesize a final answer.  
  2. **Build the Session Analysis Tool:**  
     * A new SessionHistoryAnalystAgent will be created. Its purpose is to analyze the session history to answer questions or find specific content.  
     * This agent's capability will be exposed to the Maestro as a query\_session\_history(query: str) tool.  
  3. **Build the Context-Aware Refinement Tool:**  
     * A new RefinementRequestParserAgent will be created to parse natural language refinement commands into a structured format ({target, feedback}).  
     * The orchestration logic for finding the target content (using the SessionHistoryAnalystAgent), bundling its full context, and calling the ReviewerAgent will be created.  
     * This entire workflow will be exposed to the Maestro as a single refine\_content(request: str) tool.  
  4. **Expose Existing Capabilities as Tools:**  
     * The core functions of the deterministic OrchestratorAgent will be wrapped and exposed as tools for the Maestro, including:  
       * plan\_content(time\_frame: str \= None, num\_posts: int \= None)  
       * generate\_ideas(pillar: str, num\_ideas: int)  
       * develop\_post(idea: PostIdea)  
       * generate\_brand\_report()  
* **File System Changes:**  
  * **New Files:** src/agents\_crew/maestro.py, src/agents\_crew/session\_analyst.py, src/agents\_crew/refinement\_parser.py.  
  * **Modified:** src/agents\_crew/orchestrator.py (to make its methods tool-friendly), src/main.py (to add the new maestro command).  
* **CLI Command Updates:**  
  * **New Command:** maestro  
  * **Usage:** python src/main.py maestro "\<high\_level\_prompt\>"  
  * **Functionality:** This single command will serve as the entry point for all autonomous workflows, replacing the need for separate ask and refine commands.