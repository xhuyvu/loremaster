"""Discord bot — wires guard → orchestrator + slash commands for setup."""

import json
import os

import discord
from discord import app_commands
from dotenv import load_dotenv
from google.adk import Runner
from google.genai import types
from agents.guard import Guard
from agents.orchestrator import OrchestratorAgent
from agents.session_service import FileSessionService
from mcp_servers.campaign_state_server.server import (
    add_pc,
    get_campaign,
    init_campaign,
)

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

guard = Guard()
orchestrator = OrchestratorAgent()
_session_service = FileSessionService()
_runner = Runner(
    agent=orchestrator,
    session_service=_session_service,
    app_name="loremaster",
)


@tree.command(name="campaign", description="Manage campaign settings")
@app_commands.describe(
    action="init to start a new campaign, status to view current",
    name="Campaign name (required for init)",
    setting="Campaign setting/world (required for init)",
    starting_location="Starting location (required for init)",
)
async def campaign(
    interaction: discord.Interaction,
    action: str,
    name: str = None,
    setting: str = None,
    starting_location: str = None,
):
    if action == "init":
        if not all([name, setting, starting_location]):
            await interaction.response.send_message(
                "Usage: /campaign init name:<name> setting:<setting> starting_location:<location>"
            )
            return
        result = init_campaign(name, setting, starting_location)
        await interaction.response.send_message(result)
    elif action == "status":
        raw = get_campaign()
        if raw:
            c = json.loads(raw)
            await interaction.response.send_message(
                f"**{c['name']}** — {c['setting']}\nStarting location: {c['starting_location']}"
            )
        else:
            await interaction.response.send_message("No campaign set. Use /campaign init to start one.")
    else:
        await interaction.response.send_message("Action must be `init` or `status`.")


@tree.command(name="pc", description="Manage player characters")
@app_commands.describe(
    action="add to add a PC to the party",
    name="Character name (required for add)",
    race="Character race (required for add)",
    char_class="Character class (required for add)",
    level="Character level (default: 1)",
)
async def pc(
    interaction: discord.Interaction,
    action: str,
    name: str = None,
    race: str = None,
    char_class: str = None,
    level: int = 1,
):
    if action == "add":
        if not all([name, race, char_class]):
            await interaction.response.send_message(
                "Usage: /pc add name:<name> race:<race> char_class:<class> level:<level>"
            )
            return
        result = add_pc(name, race, char_class, level)
        await interaction.response.send_message(result)
    else:
        await interaction.response.send_message("Action must be `add`.")

# ponytail: global runner + in-memory sessions. Per-channel sessions would use
# DB-backed session service; per-user runners if throughput requires it.
guard = Guard()
orchestrator = OrchestratorAgent()
_session_service = InMemorySessionService()
_runner = Runner(
    agent=orchestrator,
    session_service=_session_service,
    app_name="loremaster",
)


@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user} (ID: {client.user.id})")


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    is_safe, reason = await guard.injection_filter(message.content)
    if not is_safe:
        await message.channel.send(
            f"{message.author.mention} Message blocked: {reason}"
        )
        return

    responses = []
    async for event in _runner.run_async(
        user_id=str(message.author.id),
        session_id=str(message.channel.id),
        new_message=types.Content(role="user", parts=[types.Part(text=message.content)]),
    ):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    responses.append(part.text)

    reply = "\n".join(responses) if responses else "Hmm, I'm not sure how to respond."
    await message.channel.send(f"{message.author.mention} {reply}")


def demo():
    """Self-check: verify pipeline imports and client config (does not log in)."""
    assert client.user is None
    assert guard is not None
    assert orchestrator is not None
    assert _runner is not None
    token = os.environ.get("DISCORD_BOT_TOKEN")
    print(f"OK — Discord client ready. token={'set' if token else 'NOT SET'}")


if __name__ == "__main__":
    demo()
