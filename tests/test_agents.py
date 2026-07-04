"""Tests for agent modules."""

from agents import (
    GuardAgent,
    Guard,
    OrchestratorAgent,
    RulesAdjudicatorAgent,
    CombatEngineAgent,
    NpcPersonaAgent,
    WorldStateAgent,
)


def test_all_agents_instantiate():
    agents = [
        GuardAgent(),
        OrchestratorAgent(),
        RulesAdjudicatorAgent(),
        CombatEngineAgent(),
        NpcPersonaAgent(),
        WorldStateAgent(),
    ]
    for a in agents:
        assert a.name


def test_guard_wrapper():
    g = Guard()
    assert g.agent.name == "input_guard"


def test_world_state_tools():
    a = WorldStateAgent()
    tool_names = {t.__name__ for t in a.tools}
    assert "init_campaign" in tool_names
    assert "get_campaign" in tool_names
    assert "add_pc" in tool_names
    assert "get_party" in tool_names
    assert "get_state" in tool_names
    assert "set_state" in tool_names


def test_combat_engine_tools():
    a = CombatEngineAgent()
    tool_names = {t.__name__ for t in a.tools}
    assert "roll_dice" in tool_names
    assert "get_combat_state" in tool_names
    assert "apply_damage" in tool_names
    assert "set_combat_state" in tool_names
    assert "end_combat" in tool_names
