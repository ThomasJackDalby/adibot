import os
import datetime
import discord
import data
import utils
import constants
from model import Member, Session
from discord import Member, VoiceState, Guild
from typing import Optional

from rich import print, traceback
traceback.install()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

GUILD = discord.Object(id=constants.DISCORD_GUILD_ID)

async def get_guild_name() -> Optional[str]:
    guild = await get_guild()
    if guild is None: return None
    return guild.name

async def get_guild() -> Optional[Guild]:
    guild = client.get_guild(constants.DISCORD_GUILD_ID)
    if guild is not None: return guild
    return await client.fetch_guild(constants.DISCORD_GUILD_ID)

@tree.command(name='add-member', description='Adds a member', guild=GUILD)
async def add_member(interaction: discord.Interaction, user: discord.Member, name: str):
    guild_name = await get_guild_name()
    discord_name = user.name
    data.add_member(name, discord_name)
    await interaction.response.send_message(f"Added {discord_name} [{name}] to {guild_name}")

@tree.command(name='remove-member', description='Removes a member', guild=GUILD)
async def add_member(interaction: discord.Interaction, user: discord.Member, name: str):
    guild_name = await get_guild_name()
    discord_name = user.name
    data.add_member(name, discord_name)
    await interaction.response.send_message(f"Removed {discord_name} [{name}] from {guild_name}")

def get_or_create_session(current_datetime: datetime.datetime) -> Session:
    """gets or creates a session for this Friday"""
    current_date = current_datetime.date()
    session = data.get_session_by_date(current_date)
    if session is None: session = data.add_session(current_date)
    return session

async def on_user_joins_channel(discord_member: discord.Member) -> None:
    guild_name = await get_guild_name()
    print(f"{discord_member.name} is in {guild_name}")

    member = data.get_member_by_discord_name(discord_member.name)
    if member is None: return

    current_datetime = datetime.datetime.today()
    if not utils.is_valid_session_from_datetime(current_datetime): return False
    session = get_or_create_session(current_datetime)

    session_member = data.get_session_member(member_id=member.id, session_id=session.id)
    if session_member is None:
        data.add_session_member(session.id, member.id, start=current_datetime, end=current_datetime)
    else:
        session_member.end = current_datetime
        data.update_session_member(session_member)  

async def on_user_leaves_channel(discord_member: Member) -> None:
    member = data.get_member_by_discord_name(discord_member.name)
    if member is None: return

    current_datetime = datetime.datetime.today()
    if not utils.is_valid_session_from_datetime(current_datetime): return False
    session = get_or_create_session(current_datetime)

    session_member = data.get_session_member(member_id=member.id, session_id=session.id)
    if session_member is None: 
        session_start_datetime = utils.get_current_or_last_session_start_date(current_datetime.date())
        data.add_session_member(session.id, member.id, start=session_start_datetime, end=current_datetime)
    else:
        session_member.end = current_datetime
        data.update_session_member(session_member)

@client.event
async def on_ready():
    print(f'Logged on as {client.user}!')
    try:
        synced = await tree.sync(guild=GUILD)
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(e)

@client.event
async def on_message(message):
    print(f'Message from {message.author}: {message.content}')

@client.event
async def on_voice_state_update(member: Member, before: VoiceState, after: VoiceState):
    if before.channel is None and after.channel is not None:
        print(f"{member.name} joined the '{after.channel.name}' channel!")
        await on_user_joins_channel(member)
    elif before.channel is not None and after.channel is None:
        print(f"This prick ({member.name}) left the '{before.channel.name}' channel.")
        await on_user_leaves_channel(member)

client.run(constants.DISCORD_TOKEN)