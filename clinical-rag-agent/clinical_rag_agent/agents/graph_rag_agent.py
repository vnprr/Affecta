from clinical_rag_agent.agents.base_agent import BaseAgent


class GraphRagAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="graph_rag_agent", goal="Use graph relations when available and degrade gracefully.")

