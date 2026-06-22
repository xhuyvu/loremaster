"""World-State — long-term campaign memory."""

from google.adk.agents import Agent


from mcp_servers.campaign_state_server.server import get_state, set_state


class WorldStateAgent(Agent):
    name: str = "world_state"
    model: str = "gemini-3.5-flash"
    instruction: str = (
        "You manage the campaign's long-term state: quest log, inventory, "
        "NPC relationships, alive/dead status, and world changes. "
        "Read state with get_state and write with set_state. "
        "All state mutations go through you — no raw DB access."
    )
    description: str = "Manages campaign state — quests, inventory, world"
    tools: list = [get_state, set_state]
