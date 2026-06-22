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
