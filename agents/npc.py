"""NPC Persona — in-character dialogue, distinct from narrator."""

from google.adk.agents import Agent


class NpcPersonaAgent(Agent):
    name: str = "npc_persona"
    model: str = "gemini-3.5-flash"
    instruction: str = (
        "You roleplay as the NPC the player is speaking to. "
        "Stay in character, use the NPC's voice and personality. "
        "Do not narrate — speak as the NPC. "
        "Only respond when the orchestrator calls you."
    )
    description: str = "In-character NPC dialogue"
