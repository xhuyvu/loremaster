"""Discord bot client — placeholder wiring."""

import os

import discord
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"Logged in as {client.user} (ID: {client.user.id})")


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return

    # ponytail: guard → orchestrator → sub-agent chain will replace this
    await message.channel.send(
        f"{message.author.mention} Loremaster is online. "
        f"(Stub handler — message routing not yet wired.)"
    )


def demo():
    """Self-check: verify client config (does not log in)."""
    assert client.user is None
    token = os.environ.get("DISCORD_BOT_TOKEN")
    print(f"OK — Discord client ready. token={'set' if token else 'NOT SET'}")


if __name__ == "__main__":
    demo()
