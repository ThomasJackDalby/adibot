import os
import datetime
import discord
from data import DataBaseSession
import utils
import constants
import functools
from model import Member, Session
from typing import Optional, Union

from rich import print, traceback
traceback.install()

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

channel = client.get_channel(123456789)

GUILD = discord.Object(id=constants.DISCORD_GUILD_ID)

class AuthorisationError(Exception):
    def __init__(self, message, errors):            
        super().__init__(message)
        self.errors = errors

def enforce_admin(discord_name: str) -> None:
    """Throws an authorisation error is the user is not an admin"""
    with DataBaseSession() as db:
        member = db.get_member_by_discord_name(discord_name)
        if member is None: raise AuthorisationError(f"I can't do that if I don't know who you are ol' chap.")
        if not member.is_admin: raise AuthorisationError(f"Naughty naughty, that command's not for you now is it...")                 

def authorise():
    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(*args, **kwargs):
            if len(args) < 1: raise Exception("Not enough arguments provided to function, cannot authorise.")
            if not isinstance(args[0], discord.Interaction): raise Exception("Interaction not provided, cannot authorise.")
            interaction = args[0]
            try:
                enforce_admin(interaction.user.name)        
                return await func(*args)
            except AuthorisationError as e:
                await interaction.response.send_message(e.message)
        return wrapped
    return wrapper

async def get_guild_name() -> Optional[str]:
    guild = await get_guild()
    if guild is None: return None
    return guild.name

async def get_guild() -> Optional[discord.Guild]:
    guild = client.get_guild(constants.DISCORD_GUILD_ID)
    if guild is not None: return guild
    return await client.fetch_guild(constants.DISCORD_GUILD_ID)

# --- Commands ---

@tree.command(name='adi-stats', description='Get the stats of a member', guild=GUILD)
@authorise()
async def get_stats(discord_member: discord.Member):
    with DataBaseSession() as db:
        member = db.get_member_by_discord_name(member.name)

@tree.command(name='adi-add-member', description='Adds a member', guild=GUILD)
@authorise()
async def add_member(interaction: discord.Interaction, user: discord.Member, name: str):
    with DataBaseSession() as db:
        guild_name = await get_guild_name()
        discord_name = user.name
        db.add_member(name, discord_name)
        await interaction.response.send_message(f"Added {discord_name} [{name}] to {guild_name}")

@authorise()
@tree.command(name='adi-remove-member', description='Removes a member', guild=GUILD)
async def add_member(interaction: discord.Interaction, user: discord.Member, name: str):
    with DataBaseSession() as db:
        guild_name = await get_guild_name()
        discord_name = user.name
        db.add_member(name, discord_name)
        await interaction.response.send_message(f"Removed {discord_name} [{name}] from {guild_name}")

# --- Event Handlers ---

@client.event
async def on_ready():
    print(f'Logged on as {client.user}!')

    with DataBaseSession() as db:
        member = db.get_member_by_discord_name(constants.ADMIN_DISCORD_NAME)
        if member is None: db.add_member(constants.ADMIN_NAME, constants.ADMIN_DISCORD_NAME, is_admin=True)

    synced = await tree.sync(guild=GUILD)
    if len(synced) == 0: raise Exception("Unable to synchronise slash commands.")

@client.event
async def on_message(message):
    print(f'Message from {message.author}: {message.content}')

@client.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    if before.channel is None and after.channel is not None:
        print(f"{member.name} joined the '{after.channel.name}' channel!")
        await on_user_joins_channel(member)
    elif before.channel is not None and after.channel is None:
        print(f"This prick ({member.name}) left the '{before.channel.name}' channel.")
        await on_user_leaves_channel(member)

@client.event
async def on_presence_update(before: discord.Member, after: discord.Member):
    if before.activity is None and after.activity is not None:
        await on_user_starts_activity(after, after.activity)
    elif after.activity is None and before.activity is not None:
        await on_user_stops_activity(after, before.activity)

# -- Logic

async def on_user_joins_channel(discord_member: discord.Member) -> None:
    with DataBaseSession() as db:
        current_datetime = datetime.datetime.today()
        if not utils.is_valid_session_from_datetime(current_datetime): return False

        member = db.get_member_by_discord_name(discord_member.name)
        if member is None: return

        session = db.get_or_create_session(current_datetime.date())
        db.add_or_update_session_member(session.id, member.id, start=current_datetime)

async def on_user_leaves_channel(discord_member: Member) -> None:
    with DataBaseSession() as db:
        current_datetime = datetime.datetime.today()
        if not utils.is_valid_session_from_datetime(current_datetime): return False

        member = db.get_member_by_discord_name(discord_member.name)
        if member is None: return

        session = db.get_or_create_session(current_datetime.date())
        db.add_or_update_session_member(session.id, member.id, end=current_datetime)

async def on_user_starts_activity(discord_member: discord.Member, activity: discord.Activity):
    with DataBaseSession() as db:
        print(activity.type)
        print(type(activity.type))
        if not activity.type == discord.ActivityType.playing:
            print(f"FFS you can't play that! ({activity.name})")
            return 
        # print(type(discord_game))
        # if not isinstance(discord_game, discord.Game): return

        current_datetime = datetime.datetime.today()
        if not utils.is_valid_session_from_datetime(current_datetime): return

        member = db.get_member_by_discord_name(discord_member.name)
        if member is None: return

        session = db.get_or_create_session(current_datetime.date())
        game = db.get_or_create_game(activity.name)
        db.get_or_add_member_game(member.id, game.id)
        db.add_or_update_session_member(session.id, member.id, start=current_datetime)
        db.add_or_update_session_game(session.id, game.id, current_datetime)

async def on_user_stops_activity(discord_member: discord.Member, activity: discord.Activity):
    with DataBaseSession() as db:
        if not activity.playing:
            print(f"FFS you can't play that! ({activity.name})")
            return 
        # if not isinstance(discord_game, discord.Game): 
        #     print(f"[{discord_game.name}] is not a game.")
        #     return

        current_datetime = datetime.datetime.today()
        if not utils.is_valid_session_from_datetime(current_datetime): return

        member = db.get_member_by_discord_name(discord_member.name)
        if member is None: return

        session = db.get_or_create_session(current_datetime.date())
        game = db.get_or_create_game(activity.name)
        db.get_or_add_member_game(member.id, game.id)
        db.add_or_update_session_member(session.id, member.id, start=current_datetime)
        db.add_or_update_session_game(session.id, game.id, start=current_datetime)
    
client.run(constants.DISCORD_TOKEN)