import json
import time
import uuid
from pathlib import Path

from hata.ext import asyncio
from hata import (
    AutoModerationActionExecutionEvent,
    Client,
    ClientUserBase,
    ClientWrapper,
    Guild,
    GuildProfile,
    Message,
)
import aiosqlite

from ..constants import GUILD_ID

ALL = ClientWrapper()


DATABASE = Path("persist") / "voxelbot.db"


# ensure that the tables are setup
async def setup(_):
    if not DATABASE.parent.exists():
        DATABASE.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS logging_messages (id TEXT PRIMARY KEY, timestamp INTEGER, channel_id INTEGER, user_id INTEGER, username TEXT, action TEXT, content TEXT, json TEXT)"
        )
        await db.execute("CREATE TABLE IF NOT EXISTS logging_members (id TEXT PRIMARY KEY, timestamp INTEGER, user_id INTEGER, username TEXT, action TEXT, json TEXT)")
        await db.execute("CREATE TABLE IF NOT EXISTS logging_automod (id TEXT PRIMARY KEY, timestamp INTEGER, user_id INTEGER, username TEXT, action TEXT, json TEXT)")
        await db.commit()


# message logging
async def log_message(action: str, message: Message):
    if message.author.bot:
        return
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(
            "INSERT INTO logging_messages (id, timestamp, channel_id, user_id, username, action, content, json) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                str(uuid.uuid4()),
                time.time(),
                message.channel.id,
                message.author.id,
                message.author.full_name,
                action,
                message.content,
                json.dumps(message.to_data(include_internals=True)),
            ),
        )
        await db.commit()


@ALL.events
async def message_create(client: Client, message: Message):
    await log_message("create", message)


@ALL.events
async def message_update(client: Client, message: Message, _):
    await log_message("update", message)


@ALL.events
async def message_delete(client: Client, message: Message):
    await log_message("delete", message)


# member logging
async def log_member(action: str, user: ClientUserBase, _profile: GuildProfile | None = None):
    profile: GuildProfile | None = user.get_guild_profile_for(GUILD_ID) if _profile is None else _profile
    if profile is None:
        return
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(
            "INSERT INTO logging_members (id, timestamp, user_id, username, action, json) VALUES (?, ?, ?, ?, ?, ?)",
            (
                str(uuid.uuid4()),
                time.time(),
                user.id,
                user.full_name,
                action,
                json.dumps(profile.to_data(include_internals=True)),
            ),
        )
        await db.commit()


@ALL.events
async def guild_user_add(client: Client, guild: Guild, user: ClientUserBase):
    await log_member("add", user)


@ALL.events
async def guild_user_update(client: Client, guild: Guild, user: ClientUserBase, _):
    await log_member("update", user)


@ALL.events
async def guild_user_delete(client: Client, guild: Guild, user: ClientUserBase, profile: GuildProfile):
    await log_member("delete", user, profile)


# automod logging
async def log_automod(action: str, user: ClientUserBase, payload):
    async with aiosqlite.connect(DATABASE) as db:
        await db.execute(
            "INSERT INTO logging_automod (id, timestamp, user_id, username, action, json) VALUES (?, ?, ?, ?, ?, ?)",
            (
                str(uuid.uuid4()),
                time.time(),
                user.id,
                user.full_name,
                action,
                json.dumps(payload.to_data()),
            ),
        )
        await db.commit()


@ALL.events
async def auto_moderation_action_execution(client: Client, event: AutoModerationActionExecutionEvent):
    await log_automod("action", event.user, event)
