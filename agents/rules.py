"""Rules Adjudicator — answers SRD questions via MCP."""

from google.adk.agents import Agent


def _query_srd(query: str) -> str:
    """Stub: will call SRD MCP server."""
    return f"[SRD lookup for '{query}' — stub]"


class RulesAdjudicatorAgent(Agent):
    name: str = "rules_adjudicator"
    model: str = "gemini-3.5-flash"
    instruction: str = (
        "You are a D&D 5e rules expert. Answer rules questions using only "
        "the SRD lookup tool. Never guess or homebrew an answer. "
        "If the SRD doesn't cover it, say so clearly."
    )
    description: str = "Answers D&D 5e rules questions via SRD lookup"
    tools: list = [_query_srd]
