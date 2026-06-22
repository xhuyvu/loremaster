"""Agents package — all ADK Agent subclasses."""

from agents.guard import GuardAgent, Guard
from agents.orchestrator import OrchestratorAgent
from agents.rules import RulesAdjudicatorAgent
from agents.combat import CombatEngineAgent
from agents.npc import NpcPersonaAgent
from agents.world_state import WorldStateAgent

__all__ = [
    "GuardAgent",
    "Guard",
    "OrchestratorAgent",
    "RulesAdjudicatorAgent",
    "CombatEngineAgent",
    "NpcPersonaAgent",
    "WorldStateAgent",
]


def demo():
    """Self-check: instantiate every agent."""
    agents = [
        ("guard", GuardAgent()),
        ("orchestrator", OrchestratorAgent()),
        ("rules", RulesAdjudicatorAgent()),
        ("combat", CombatEngineAgent()),
        ("npc", NpcPersonaAgent()),
        ("world", WorldStateAgent()),
    ]
    for label, agent in agents:
        assert agent.name, f"{label}: name is empty"
        print(f"  {agent.name}: OK")
    Guard()
    print("  guard wrapper: OK")
    print(f"Total: {len(agents)} agents + wrapper")


if __name__ == "__main__":
    demo()
