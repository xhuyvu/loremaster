"""Combat Engine — initiative, HP, conditions via dice MCP."""

from google.adk.agents import Agent


from mcp_servers.dice_server.server import roll_dice


class CombatEngineAgent(Agent):
    name: str = "combat_engine"
    model: str = "gemini-3.5-flash"
    instruction: str = (
        "You manage D&D combat: initiative, HP tracking, conditions, "
        "and dice rolls. Use the dice rolling tool for all random rolls. "
        "Report results clearly for the DM Orchestrator to narrate."
    )
    description: str = "Manages combat — initiative, HP, conditions, dice rolls"
    tools: list = [roll_dice]
