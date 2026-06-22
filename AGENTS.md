# AGENTS.md — Loremaster

## Setup

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install
pip install -r requirements.txt
```

## Commands

```bash
# Always activate venv first
source .venv/bin/activate

# Start MCP servers (each in its own terminal)
python mcp_servers/dice_server/run.py
python mcp_servers/srd_server/run.py
python mcp_servers/campaign_state_server/run.py

# Start bot
python bot/discord_client.py

# Lint
ruff check .

# Test
python -m pytest
```

## Architecture

```
┌──────────┐     ┌──────────────┐
│ Players  │────▶│ Input Guard  │
│(Discord) │     │ (injection   │
└──────────┘     │  filter)     │
                 └──────┬───────┘
                        ▼
               ┌────────────────┐
               │  Orchestrator  │
               │  (routes       │
               │   intent)      │
               └──┬──┬──┬──┬───┘
                  │  │  │  │
         ┌────────┘  │  │  └────────┐
         ▼           ▼  ▼           ▼
┌─────────────┐ ┌──────────┐ ┌──────────┐
│    Rules    │ │  Combat  │ │  World   │
│ Adjudicator │ │  Engine  │ │  State   │
│  (SRD MCP)  │ │(Dice MCP)│ │(State DB)│
└─────────────┘ └──────────┘ └──────────┘
```

| Agent | Role |
|---|---|
| Input Guard | Sanitizes input before any agent sees it. Discriminator model, not regex. |
| DM Orchestrator | Player-facing voice. Interprets intent, delegates, composes narration. |
| Rules Adjudicator | Answers rules questions via SRD MCP. Never guesses. |
| Combat Engine | Initiative, HP, conditions. Dice rolls via MCP (verifiable). |
| NPC Persona | In-character dialogue. Separate from narrator voice. |
| World-State | Long-term memory: quest log, inventory, alive/dead. |

**Trust paths:** Player input → Guard → Orchestrator → sub-agents.
State mutation only through World-State MCP. Narration output back to player.

## Conventions

- Agents are ADK `LlmAgent` or `Agent` subclasses.
- MCP servers use stdio transport.
- All player input passes through `guard.injection_filter` before any agent.
- Campaign state goes through `world_state` agent / MCP — no raw DB access outside it.
- No raw LLM calls outside `agents/`.
- Mark intentional simplifications with `ponytail:` comments.

## Constraints

- Secrets from `os.environ` only. Never logged.
- Guard uses a discriminator model, not a keyword list.
- One `demo()` / `__main__` self-check per non-trivial module. Skip trivial one-liners.

## Git conventions

- Branch naming: `<type>/<short-description>` (e.g. `feat/dice-server`, `fix/initiative-roll`)
- Commit message format: `<type>(<optional scope>): <short summary>`
  - Types: `feat`, `fix`, `chore`, `docs`, `refactor`, `test`
  - Scope: module/area (e.g. `mcp`, `agents`, `bot`, `project`)
  - Summary: lowercase, no period, imperative mood
  - Body (optional): blank line then wrapped at 100 chars
- Small, focused commits. Stop before each commit for review.
