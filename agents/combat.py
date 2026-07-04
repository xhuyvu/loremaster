"""Combat Engine — initiative, HP, conditions via dice MCP."""

from google.adk.agents import Agent


from mcp_servers.campaign_state_server.server import (
    apply_damage,
    end_combat,
    get_combat_state,
    set_combat_state,
)
from mcp_servers.dice_server.server import roll_dice


class CombatEngineAgent(Agent):
    name: str = "combat_engine"
    model: str = "gemini-3.5-flash"
    instruction: str = (
        "You manage D&D combat: initiative, HP tracking, conditions, "
        "and dice rolls. Use the dice rolling tool for all random rolls. "
        "Use get_combat_state to read the current combat state "
        "(combatants, initiative order, HP, conditions, round, turn). "
        "Use set_combat_state to initialize combat or update the full state, "
        "apply_damage for damage/healing, and end_combat when combat ends. "
        "Report results clearly for the DM Orchestrator to narrate."
    )
    description: str = "Manages combat — initiative, HP, conditions, dice rolls"
    tools: list = [roll_dice, get_combat_state, apply_damage, set_combat_state, end_combat]
