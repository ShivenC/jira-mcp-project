# mcp_tools.py
#
# MCP tool definitions for the Jira SOC ticket automation pipeline.
# These tools are consumed by the MCP server and can be invoked by
# Copilot Agent integrations.

import re
from typing import List

ticket_store: List[dict] = []

_IP_PATTERN = re.compile(r"\d+\.\d+\.\d+\.\d+")


def get_all_tickets() -> List[dict]:
    """Return all tickets currently held in the in-memory store."""
    return ticket_store


def find_repeated_ips() -> dict:
    """
    Scan ticket descriptions for IPv4 addresses that appear more than once.

    Returns a dict mapping each repeated IP to its occurrence count.
    """
    counts: dict = {}
    for ticket in ticket_store:
        description = ticket.get("description", "")
        for ip in _IP_PATTERN.findall(description):
            counts[ip] = counts.get(ip, 0) + 1
    return {ip: count for ip, count in counts.items() if count > 1}


def summarize_tickets() -> dict:
    """
    Return a high-level summary of the tickets in the store.

    Keys: total, high_priority, status_counts
    """
    total = len(ticket_store)
    high_priority = sum(1 for t in ticket_store if t.get("priority") == "High")
    status_counts: dict = {}
    for ticket in ticket_store:
        status = ticket.get("status", "Unknown")
        status_counts[status] = status_counts.get(status, 0) + 1
    return {
        "total": total,
        "high_priority": high_priority,
        "status_counts": status_counts,
    }

