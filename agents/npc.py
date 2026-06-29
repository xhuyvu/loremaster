"""NPC Persona — in-character dialogue, distinct from narrator."""

from google.adk.agents import Agent
from mcp_servers.campaign_state_server.server import get_npc


class NpcPersonaAgent(Agent):
    name: str = "npc_persona"
    model: str = "gemini-3.5-flash"
    instruction: str = (
        "You roleplay as the NPC the player is speaking to. "
        "Use get_npc to load your personality, knowledge, and stats, "
        "then stay in character using that profile. "
        "Do not narrate — speak as the NPC. "
        "Only respond when the orchestrator calls you."
    )
    description: str = "In-character NPC dialogue with persistent profile"
    tools: list = [get_npc]
