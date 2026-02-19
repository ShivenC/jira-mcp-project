from .summary_agent import SummaryAgent
from .risk_agent import RiskAgent
from .mitigation_agent import MitigationAgent


class AgentRunner:
    """
    Multi-Agent Orchestrator.

    Coordinates the three specialist agents in a sequential pipeline:

      1. SummaryAgent    - executive narrative summary
      2. RiskAgent       - high-priority ticket identification
      3. MitigationAgent - repeated-IP detection & recommendations

    Each agent receives the same shared ticket DataFrame.  Results are
    collected into a single dict so callers (e.g. the Streamlit dashboard
    or a Copilot Agent integration) can consume them independently.
    """

    def __init__(self):
        self.summary_agent = SummaryAgent()
        self.risk_agent = RiskAgent()
        self.mitigation_agent = MitigationAgent()

    def run_all(self, df):
        """
        Run every agent against *df* and return their combined output.

        Parameters
        ----------
        df : pandas.DataFrame
            Ticket data with at least 'priority', 'status', and optionally
            'description' columns.

        Returns
        -------
        dict with keys:
            summary    : str       - output of SummaryAgent
            high_risk  : DataFrame - output of RiskAgent
            mitigation : dict      - output of MitigationAgent
        """
        return {
            "summary": self.summary_agent.run(df),
            "high_risk": self.risk_agent.run(df),
            "mitigation": self.mitigation_agent.run(df),
        }
