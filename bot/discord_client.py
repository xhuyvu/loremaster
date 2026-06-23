"""Discord bot client — wires guard → orchestrator → sub-agent pipeline."""

import os

import discord
from dotenv import load_dotenv
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents.guard import Guard
from agents.orchestrator import OrchestratorAgent

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

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
