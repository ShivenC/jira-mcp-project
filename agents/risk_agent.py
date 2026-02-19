class RiskAgent:
    """
    Risk Analysis / Priority Agent.

    Identifies high-priority tickets that require immediate attention,
    providing a filtered view of the most critical open issues.
    """

    def run(self, df):
        """
        Filter the ticket DataFrame for high-priority (High) entries.

        Parameters
        ----------
        df : pandas.DataFrame
            DataFrame containing at minimum a 'priority' column.

        Returns
        -------
        pandas.DataFrame
            Subset of *df* where priority is 'High'.  May be empty.
        """
        return df[df["priority"] == "High"].copy()
