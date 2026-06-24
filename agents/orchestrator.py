"""DM Orchestrator — player-facing voice, routes intent."""

from google.adk.agents import Agent
from agents.rules import RulesAdjudicatorAgent
from agents.combat import CombatEngineAgent
from agents.npc import NpcPersonaAgent
from agents.world_state import WorldStateAgent


class OrchestratorAgent(Agent):
    name: str = "dm_orchestrator"
    model: str = "gemini-3.5-flash"
    instruction: str = (
        "You are the Dungeon Master. Narrate the world, describe scenes, "
        "and manage the flow of the game. "
        "Delegate to sub-agents for rules questions (rules_adjudicator), "
        "combat resolution (combat_engine), NPC dialogue (npc_persona), "
        "and world/campaign state changes (world_state). "
        "Ask world_state for campaign info and party roster to set the scene. "
        "Keep the game moving and fun."
    )
    description: str = "Main DM agent — narrates and delegates"
    sub_agents: list = [
        RulesAdjudicatorAgent(),
        CombatEngineAgent(),
        NpcPersonaAgent(),
        WorldStateAgent(),
    ]
