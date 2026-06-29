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
    assert "set_npc" in tools
    assert "get_npc" in tools
    assert "list_npcs" in tools
    assert "delete_npc" in tools


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


class TestNpcCrud:
    def test_set_and_get_npc(self):
        from mcp_servers.campaign_state_server.server import (
            _DATA_FILE,
            get_npc,
            set_npc,
        )
        import json

        _DATA_FILE.unlink(missing_ok=True)
        result = set_npc("Elminster", "Wise and cryptic", "Knows the Weave", "STR 10")
        assert "saved" in result
        raw = get_npc("Elminster")
        profile = json.loads(raw)
        assert profile["personality"] == "Wise and cryptic"
        assert profile["knowledge"] == "Knows the Weave"
        assert profile["stats"] == "STR 10"
        _DATA_FILE.unlink(missing_ok=True)

    def test_get_npc_not_found(self):
        from mcp_servers.campaign_state_server.server import (
            _DATA_FILE,
            get_npc,
        )

        _DATA_FILE.unlink(missing_ok=True)
        assert get_npc("Ghost") == '""'
        _DATA_FILE.unlink(missing_ok=True)

    def test_update_npc(self):
        from mcp_servers.campaign_state_server.server import (
            _DATA_FILE,
            get_npc,
            set_npc,
        )
        import json

        _DATA_FILE.unlink(missing_ok=True)
        set_npc("Elminster", "Old")
        set_npc("Elminster", "Ancient and wise")
        profile = json.loads(get_npc("Elminster"))
        assert profile["personality"] == "Ancient and wise"
        _DATA_FILE.unlink(missing_ok=True)

    def test_list_npcs(self):
        from mcp_servers.campaign_state_server.server import (
            _DATA_FILE,
            list_npcs,
            set_npc,
        )
        import json

        _DATA_FILE.unlink(missing_ok=True)
        assert json.loads(list_npcs()) == []
        set_npc("Elminster", "Wise")
        set_npc("Durnan", "Gruff")
        names = json.loads(list_npcs())
        assert "Elminster" in names
        assert "Durnan" in names
        _DATA_FILE.unlink(missing_ok=True)

    def test_delete_npc(self):
        from mcp_servers.campaign_state_server.server import (
            _DATA_FILE,
            delete_npc,
            get_npc,
            set_npc,
        )

        _DATA_FILE.unlink(missing_ok=True)
        set_npc("Elminster", "Wise")
        assert "deleted" in delete_npc("Elminster")
        assert get_npc("Elminster") == '""'
        assert "not found" in delete_npc("Ghost")
        _DATA_FILE.unlink(missing_ok=True)
