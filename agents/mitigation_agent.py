import re


class MitigationAgent:
    """
    Mitigation Recommendation / Analysis Agent.

    Scans ticket descriptions for repeated attacker IP addresses and
    recommends firewall actions when recurring IPs are detected.
    """

    # Matches IPv4 addresses embedded in free-text descriptions
    _IP_PATTERN = re.compile(r"(\d+\.\d+\.\d+\.\d+)")

    def run(self, df):
        """
        Detect repeated attacker IPs and build a recommendation payload.

        Parameters
        ----------
        df : pandas.DataFrame
            DataFrame that may contain a 'description' column with raw
            SOC event log text.

        Returns
        -------
        dict with keys:
            flagged_ips : pandas.Series or None
                IP -> occurrence-count for IPs that appear more than once.
                ``None`` when no description column is present or no
                repeated IPs are found.
            recommendation : str or None
                Plain-text mitigation recommendation, or ``None``.
        """
        if "description" not in df.columns:
            return {"flagged_ips": None, "recommendation": None}

        extracted = df["description"].str.extract(self._IP_PATTERN)[0]
        ip_counts = extracted.value_counts()
        flagged = ip_counts[ip_counts > 1]

        if flagged.empty:
            return {"flagged_ips": None, "recommendation": None}

        return {
            "flagged_ips": flagged,
            "recommendation": "Block repeated IP addresses at firewall.",
        }
