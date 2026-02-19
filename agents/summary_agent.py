class SummaryAgent:
    """
    Executive Summary Agent.

    Produces a high-level narrative summary of all SOC tickets,
    including total counts, high-priority breakdown, and most
    common status.
    """

    def run(self, df):
        """
        Analyse the ticket DataFrame and return a plain-text summary.

        Parameters
        ----------
        df : pandas.DataFrame
            DataFrame containing at minimum 'priority' and 'status' columns.

        Returns
        -------
        str
            Human-readable executive summary string.
        """
        total = len(df)
        high_count = int((df["priority"] == "High").sum())
        most_common_status = df["status"].value_counts().idxmax()

        return (
            f"There are currently {total} active SOC tickets. "
            f"{high_count} are marked as High priority. "
            f"Most common status: {most_common_status}."
        )
