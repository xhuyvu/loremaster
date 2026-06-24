"""World-State — long-term campaign memory."""

from google.adk.agents import Agent


from mcp_servers.campaign_state_server.server import (
    add_pc,
    get_campaign,
    get_party,
    get_state,
    init_campaign,
    set_state,
)


class WorldStateAgent(Agent):
    name: str = "world_state"
    model: str = "gemini-3.5-flash"
    instruction: str = (
        "You manage the campaign's long-term state: campaign info, party roster, "
        "quest log, inventory, NPC relationships, alive/dead status, and world "
        "changes. Use init_campaign/get_campaign for campaign setup, "
        "add_pc/get_party for the party, and get_state/set_state for other state. "
        "All state mutations go through you."
    )
    description: str = "Manages campaign state — campaign, party, quests, inventory"
    tools: list = [get_state, set_state, init_campaign, get_campaign, add_pc, get_party]
