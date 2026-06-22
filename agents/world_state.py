"""World-State — long-term campaign memory."""

from google.adk.agents import Agent


def _get_state(key: str) -> str:
    """Stub: will call Campaign State MCP server."""
    return f"[get_state('{key}') — stub]"


def _set_state(key: str, value: str) -> str:
    """Stub: will call Campaign State MCP server."""
    return f"[set_state('{key}', '{value}') — stub]"


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
    tools: list = [_get_state, _set_state]
