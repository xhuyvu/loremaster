"""Tests for MCP server modules."""

import re

import pytest


@pytest.mark.asyncio
async def test_dice_server_demo():
    from mcp_servers.dice_server.server import mcp

    tools = [t.name for t in await mcp.list_tools()]
    assert "roll_dice" in tools


class TestRollDice:
    def test_basic_roll(self):
        from mcp_servers.dice_server.server import roll_dice

        result = roll_dice(2, 6)
        m = re.match(r"Rolled 2d6: \[(\d+), (\d+)\] \(total: (\d+)\)", result)
        assert m, f"unexpected format: {result}"
        v1, v2, total = int(m[1]), int(m[2]), int(m[3])
        assert 1 <= v1 <= 6
        assert 1 <= v2 <= 6
        assert v1 + v2 == total

    def test_range(self):
        from mcp_servers.dice_server.server import roll_dice

        for _ in range(20):
            result = roll_dice(1, 20)
            v = int(result.split("[")[1].split("]")[0])
            assert 1 <= v <= 20

    def test_invalid_count(self):
        from mcp_servers.dice_server.server import roll_dice

        with pytest.raises(ValueError):
            roll_dice(0, 6)

    def test_invalid_sides(self):
        from mcp_servers.dice_server.server import roll_dice

        with pytest.raises(ValueError):
            roll_dice(1, 1)

    def test_excessive_count(self):
        from mcp_servers.dice_server.server import roll_dice

        with pytest.raises(ValueError):
            roll_dice(101, 6)


@pytest.mark.asyncio
async def test_srd_server_demo():
    from mcp_servers.srd_server.server import mcp

    tools = [t.name for t in await mcp.list_tools()]
    assert "query_srd" in tools


@pytest.mark.asyncio
async def test_campaign_state_server_demo():
    from mcp_servers.campaign_state_server.server import mcp

    tools = [t.name for t in await mcp.list_tools()]
    assert "get_state" in tools
    assert "set_state" in tools
    assert "init_campaign" in tools
    assert "get_campaign" in tools
    assert "add_pc" in tools
    assert "get_party" in tools
    assert "get_combat_state" in tools
    assert "apply_damage" in tools
    assert "set_combat_state" in tools
    assert "end_combat" in tools


class TestCampaignState:
    def test_set_and_get(self):
        from mcp_servers.campaign_state_server.server import (
            _DATA_FILE,
            get_state,
            set_state,
        )

        _DATA_FILE.unlink(missing_ok=True)
        set_state("hp", "42")
        assert get_state("hp") == "42"
        _DATA_FILE.unlink(missing_ok=True)

    def test_missing_key(self):
        from mcp_servers.campaign_state_server.server import (
            _DATA_FILE,
            get_state,
        )

        _DATA_FILE.unlink(missing_ok=True)
        assert get_state("nonexistent") == ""
        _DATA_FILE.unlink(missing_ok=True)

    def test_overwrite(self):
        from mcp_servers.campaign_state_server.server import (
            _DATA_FILE,
            get_state,
            set_state,
        )

        _DATA_FILE.unlink(missing_ok=True)
        set_state("gold", "100")
        set_state("gold", "200")
        assert get_state("gold") == "200"
        _DATA_FILE.unlink(missing_ok=True)

    def test_persistence(self):
        from mcp_servers.campaign_state_server.server import (
            _DATA_FILE,
            get_state,
            set_state,
        )

        _DATA_FILE.unlink(missing_ok=True)
        set_state("quest", "save the village")
        v1 = get_state("quest")
        v2 = get_state("quest")
        assert v1 == v2 == "save the village"
        _DATA_FILE.unlink(missing_ok=True)


class TestCampaignInit:
    def test_init_and_get(self):
        from mcp_servers.campaign_state_server.server import (
            _DATA_FILE,
            get_campaign,
            init_campaign,
        )
        import json

        _DATA_FILE.unlink(missing_ok=True)
        result = init_campaign("Test", "A test world", "Start Town")
        assert "initialized" in result
        raw = get_campaign()
        c = json.loads(raw)
        assert c["name"] == "Test"
        assert c["setting"] == "A test world"
        assert c["starting_location"] == "Start Town"
        _DATA_FILE.unlink(missing_ok=True)

    def test_get_campaign_not_set(self):
        from mcp_servers.campaign_state_server.server import (
            _DATA_FILE,
            get_campaign,
        )

        _DATA_FILE.unlink(missing_ok=True)
        assert get_campaign() == '""'
        _DATA_FILE.unlink(missing_ok=True)

    def test_add_pc_and_get_party(self):
        from mcp_servers.campaign_state_server.server import (
            _DATA_FILE,
            add_pc,
            get_party,
        )
        import json

        _DATA_FILE.unlink(missing_ok=True)
        add_pc("Alice", "Elf", "Wizard", 2)
        add_pc("Bob", "Dwarf", "Fighter", 1)
        raw = get_party()
        party = json.loads(raw)
        assert len(party) == 2
        assert party[0]["name"] == "Alice"
        assert party[0]["level"] == 2
        assert party[1]["name"] == "Bob"
        _DATA_FILE.unlink(missing_ok=True)

    def test_get_party_empty(self):
        from mcp_servers.campaign_state_server.server import (
            _DATA_FILE,
            get_party,
        )

        _DATA_FILE.unlink(missing_ok=True)
        assert get_party() == "[]"
        _DATA_FILE.unlink(missing_ok=True)


class TestCombatState:
    def test_get_empty(self):
        from mcp_servers.campaign_state_server.server import (
            _DATA_FILE,
            get_combat_state,
        )
        import json

        _DATA_FILE.unlink(missing_ok=True)
        assert json.loads(get_combat_state()) == {}

    def test_set_and_get(self):
        from mcp_servers.campaign_state_server.server import (
            _DATA_FILE,
            get_combat_state,
            set_combat_state,
        )
        import json

        _DATA_FILE.unlink(missing_ok=True)
        state = json.dumps({"round": 1, "current_turn_index": 0, "combatants": []})
        set_combat_state(state)
        result = json.loads(get_combat_state())
        assert result["round"] == 1
        assert result["combatants"] == []

    def test_apply_damage(self):
        from mcp_servers.campaign_state_server.server import (
            _DATA_FILE,
            apply_damage,
            set_combat_state,
        )
        import json

        _DATA_FILE.unlink(missing_ok=True)
        state = {
            "round": 1,
            "current_turn_index": 0,
            "combatants": [
                {"name": "Goblin", "initiative": 15, "hp": 7, "max_hp": 7, "ac": 15, "conditions": [], "is_player": False},
            ],
        }
        set_combat_state(json.dumps(state))

        result = apply_damage("Goblin", 5)
        assert "takes 5 damage" in result
        assert "(HP: 2/7)" in result

    def test_apply_damage_floor_at_zero(self):
        from mcp_servers.campaign_state_server.server import (
            _DATA_FILE,
            apply_damage,
            get_combat_state,
            set_combat_state,
        )
        import json

        _DATA_FILE.unlink(missing_ok=True)
        state = {
            "round": 1,
            "current_turn_index": 0,
            "combatants": [
                {"name": "Goblin", "initiative": 15, "hp": 7, "max_hp": 7, "ac": 15, "conditions": [], "is_player": False},
            ],
        }
        set_combat_state(json.dumps(state))

        apply_damage("Goblin", 10)
        combat = json.loads(get_combat_state())
        assert combat["combatants"][0]["hp"] == 0

    def test_healing(self):
        from mcp_servers.campaign_state_server.server import (
            _DATA_FILE,
            apply_damage,
            get_combat_state,
            set_combat_state,
        )
        import json

        _DATA_FILE.unlink(missing_ok=True)
        state = {
            "round": 1,
            "current_turn_index": 0,
            "combatants": [
                {"name": "Alice", "initiative": 12, "hp": 10, "max_hp": 20, "ac": 14, "conditions": [], "is_player": True},
            ],
        }
        set_combat_state(json.dumps(state))

        result = apply_damage("Alice", -5)
        assert "heals" in result
        combat = json.loads(get_combat_state())
        assert combat["combatants"][0]["hp"] == 15

    def test_healing_capped_at_max_hp(self):
        from mcp_servers.campaign_state_server.server import (
            _DATA_FILE,
            apply_damage,
            get_combat_state,
            set_combat_state,
        )
        import json

        _DATA_FILE.unlink(missing_ok=True)
        state = {
            "round": 1,
            "current_turn_index": 0,
            "combatants": [
                {"name": "Alice", "initiative": 12, "hp": 18, "max_hp": 20, "ac": 14, "conditions": [], "is_player": True},
            ],
        }
        set_combat_state(json.dumps(state))

        apply_damage("Alice", -10)
        combat = json.loads(get_combat_state())
        assert combat["combatants"][0]["hp"] == 20

    def test_apply_damage_unknown_target(self):
        from mcp_servers.campaign_state_server.server import (
            _DATA_FILE,
            apply_damage,
        )

        _DATA_FILE.unlink(missing_ok=True)
        result = apply_damage("Nobody", 5)
        assert "not found" in result

    def test_end_combat(self):
        from mcp_servers.campaign_state_server.server import (
            _DATA_FILE,
            end_combat,
            get_combat_state,
            set_combat_state,
        )
        import json

        _DATA_FILE.unlink(missing_ok=True)
        state = json.dumps({"round": 1, "current_turn_index": 0, "combatants": []})
        set_combat_state(state)
        end_combat()
        assert json.loads(get_combat_state()) == {}

    def test_cycle(self):
        from mcp_servers.campaign_state_server.server import (
            _DATA_FILE,
            apply_damage,
            end_combat,
            get_combat_state,
            set_combat_state,
        )
        import json

        _DATA_FILE.unlink(missing_ok=True)
        state = {
            "round": 1,
            "current_turn_index": 0,
            "combatants": [
                {"name": "Goblin", "initiative": 15, "hp": 7, "max_hp": 7, "ac": 15, "conditions": [], "is_player": False},
            ],
        }
        set_combat_state(json.dumps(state))
        apply_damage("Goblin", 7)
        combat = json.loads(get_combat_state())
        assert combat["combatants"][0]["hp"] == 0
        end_combat()
        assert json.loads(get_combat_state()) == {}
