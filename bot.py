import os
import logging
from rich.logging import RichHandler
import functools
import datetime
import discord
import data
from data import DataBaseSession
import utils
import constants
import logging
from constants import DISCORD_GUILD_ID, ADMIN_NAME, ADMIN_DISCORD_NAME, DISCORD_TOKEN

from model import Member, Session
from typing import Optional, Union

logger = logging.getLogger("adibot")

intents = discord.Intents.default()
intents.message_content = True
intents.presences = True
intents.members = True
client: discord.Client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

ActivityTypes = Union[discord.Activity, discord.Game, discord.CustomActivity, discord.Streaming, discord.Spotify]
GUILD = discord.Object(id=DISCORD_GUILD_ID)

class AuthorisationError(Exception):
    def __init__(self, message: str):            
        super().__init__(message)
        self.message = message

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

async def get_guild_name() -> str | None:
    guild = await get_guild()
    if guild is None: return None
    return guild.name

async def get_guild() -> discord.Guild | None:
    guild = client.get_guild(DISCORD_GUILD_ID)
    if guild is not None: return guild
    return await client.fetch_guild(DISCORD_GUILD_ID)

# --- Commands ---

# @tree.command(name='adi-stats', description='Get the stats of a member', guild=GUILD)
# @authorise()
# async def get_stats(discord_member: discord.Member):
#     with DataBaseSession() as db:
#         member = db.get_member_by_discord_name(discord_member.name)

# @tree.command(name='adi-add-member', description='Adds a member', guild=GUILD)
# @authorise()
# async def add_member(interaction: discord.Interaction, user: discord.Member, name: str):
#     with DataBaseSession() as db:
#         guild_name = await get_guild_name()
#         discord_name = user.name
#         db.add_member(name, discord_name)
#         await interaction.response.send_message(f"Added {discord_name} [{name}] to {guild_name}")

# @authorise()
# @tree.command(name='adi-remove-member', description='Removes a member', guild=GUILD)
# async def remove_member(interaction: discord.Interaction, user: discord.Member, name: str):
#     with DataBaseSession() as db:
#         guild_name = await get_guild_name()
#         discord_name = user.name
#         db.add_member(name, discord_name)
#         await interaction.response.send_message(f"Removed {discord_name} [{name}] from {guild_name}")

# --- Event Handlers ---

@client.event
async def on_ready():
    logger.debug(f'Logged on as {client.user}!')

    with DataBaseSession() as db:
        member = db.get_member_by_discord_name(ADMIN_DISCORD_NAME)
        if member is None: db.add_member(ADMIN_NAME, ADMIN_DISCORD_NAME, is_admin=True)

    # TODO: Uncomment when slash commands re-added.
    # synced = await tree.sync(guild=GUILD)
    # if len(synced) == 0: raise Exception("Unable to synchronise slash commands.")

@client.event
async def on_message(message):
    print(f'Message from {message.author}: {message.content}')

@client.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    if before.channel is None and after.channel is not None:
        logger.debug(f"'{member.name}' joined the '{after.channel.name}' channel.")
        await on_user_joins_channel(member)
    elif before.channel is not None and after.channel is None:
        logger.debug(f"'{member.name}' left the '{before.channel.name}' channel.")
        await on_user_leaves_channel(member)

@client.event
async def on_presence_update(before: discord.Member, after: discord.Member):
    if before.activity is None and after.activity is not None:
        await on_user_starts_activity(after, after.activity)
    elif after.activity is None and before.activity is not None:
        await on_user_stops_activity(after, before.activity)

# -- Logic --

async def on_user_joins_channel(discord_member: discord.Member) -> None:
    await add_or_update_session_member(discord_member)

async def on_user_leaves_channel(discord_member: discord.Member) -> None:
    await add_or_update_session_member(discord_member, True)

async def add_or_update_session_member(
    discord_member: discord.Member,
    is_end: bool = False):

    current_datetime = datetime.datetime.today()
    if not utils.is_valid_session_from_datetime(current_datetime): 
        logger.debug(f"The current date [{current_datetime}] is not a valid session.")
        return

    with DataBaseSession() as db:
        member = db.get_member_by_discord_name(discord_member.name)
        if member is None: 
            logger.debug(f"[{discord_member.name}] is not a member of adibot.")
            return

        session = db.get_or_create_session_with_date(current_datetime.date())
        session_member = db.add_or_update_session_member(session.id, member.id, datetime=current_datetime, is_end=is_end)

        # TODO: If we're ending the voice chat, end the session_member and any pending session_member_games

async def on_user_starts_activity(discord_member: discord.Member, activity: ActivityTypes):
    logger.debug(f"{discord_member.name} has started activity [{activity.name}].")
    await add_or_update_session_member_game(discord_member, activity)

async def on_user_stops_activity(discord_member: discord.Member, activity: ActivityTypes):
    logger.debug(f"{discord_member.name} has stopped activity [{activity.name}].")
    await add_or_update_session_member_game(discord_member, activity, True)
    
async def add_or_update_session_member_game(
        discord_member: discord.Member,
        discord_activity: ActivityTypes,
        is_end: bool = False):
    
    with DataBaseSession() as db:
        
        current_datetime = datetime.datetime.today()
        if not utils.is_valid_session_from_datetime(current_datetime): 
            logger.debug(f"The current date [{current_datetime}] is not a valid session.")
            return
        
        if not isinstance(discord_activity, discord.Game | discord.Activity):
            logger.debug(f"[{discord_activity.name}] is not a game (it's a [{type(discord_activity)}])")
            return
        discord_game: discord.Game | discord.Activity = discord_activity

        member = db.get_member_by_discord_name(discord_member.name)
        if member is None: 
            logger.debug(f"[{discord_member.name}] is not a member of adibot.")
            return

        game_name = discord_game.name
        if game_name is None:
            logger.warning("Cannot register game as discord_game.name is None.")
            return
        
        game = db.get_or_create_game(game_name)
        session = db.get_or_create_session_with_date(current_datetime.date())
        session_member = db.get_pending_session_member_for_session_and_member(session.id, member.id)
        
        if session_member is None: 
            logger.warning("Cannot add a session_member_game record as no pending session_member.")
            return
        db.add_or_update_session_member_game(session_member.id, game.id, datetime=current_datetime, is_end=is_end)

async def main():
    try:
        await client.login(DISCORD_TOKEN)
        await client.connect()
    except Exception as e:
        await client.close()

if __name__ == "__main__":
    client.run(DISCORD_TOKEN)