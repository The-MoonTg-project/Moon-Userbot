#  Moon-Userbot - telegram userbot
#  Copyright (C) 2020-present Moon Userbot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import re
from datetime import datetime, timedelta
from typing import Dict, Union

from pyrogram import Client
from pyrogram.errors import (
    ChatAdminRequired,
    PeerIdInvalid,
    RPCError,
    UserAdminInvalid,
    UsernameInvalid,
)
from pyrogram.raw import functions, types
from pyrogram.types import (
    ChatPermissions,
    ChatPrivileges,
    InputMediaAudio,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
    Message,
)
from pyrogram.utils import (
    MAX_CHANNEL_ID,
    MAX_USER_ID,
    MIN_CHANNEL_ID,
    MIN_CHAT_ID,
    get_channel_id,
)

from utils.db import db
from utils.misc import prefix
from utils.scripts import format_exc, text


async def check_username_or_id(data: Union[str, int]) -> str:
    data = str(data)
    if (
        not data.isdigit()
        and data[0] == "-"
        and not data[1:].isdigit()
        or not data.isdigit()
        and data[0] != "-"
    ):
        return "channel"
    peer_id = int(data)
    if peer_id < 0:
        if MIN_CHAT_ID <= peer_id:
            return "chat"

        if MIN_CHANNEL_ID <= peer_id < MAX_CHANNEL_ID:
            return "channel"
    elif 0 < peer_id <= MAX_USER_ID:
        return "user"

    raise ValueError(f"Peer id invalid: {peer_id}")


async def get_user_and_name(message):
    if message.reply_to_message.from_user:
        return (
            message.reply_to_message.from_user.id,
            message.reply_to_message.from_user.first_name,
        )
    if message.reply_to_message.sender_chat:
        return (
            message.reply_to_message.sender_chat.id,
            message.reply_to_message.sender_chat.title,
        )


class BanHandler:
    def __init__(self, client: Client, message: Message):
        self.client = client
        self.message = message
        self.cause = text(message)
        self.channel = None
        self.user_id = None
        self.name = None

    async def handle_ban(self):
        if self.message.reply_to_message:
            await self.handle_reply_ban()
        elif not self.message.reply_to_message:
            await self.handle_non_reply_ban()
        else:
            await self.message.edit("<b>Unsupported</b>")

    async def handle_reply_ban(self):
        if self.message.chat.type not in ["private", "channel"]:
            user_for_ban, self.name = await get_user_and_name(self.message)
            await self.ban_user(user_for_ban)

    async def handle_non_reply_ban(self):
        if (
            self.message.chat.type not in ["private", "channel"]
            and len(self.cause.split()) > 1
        ):
            user_to_ban = await self.get_user_to_ban()
            if user_to_ban:
                self.name = (
                    user_to_ban.first_name
                    if getattr(user_to_ban, "first_name", None)
                    else user_to_ban.title
                )
                await self.ban_user(user_to_ban.id)

    async def get_user_to_ban(self):
        user_type = await check_username_or_id(self.cause.split(" ")[1])
        if user_type == "channel":
            return await self.client.get_chat(self.cause.split(" ")[1])
        if user_type == "user":
            return await self.client.get_users(self.cause.split(" ")[1])
        await self.message.edit("<b>Invalid user type</b>")
        return None

    async def ban_user(self, user_id):
        try:
            await self.client.ban_chat_member(self.message.chat.id, user_id)
            self.channel = await self.client.resolve_peer(self.message.chat.id)
            self.user_id = await self.client.resolve_peer(user_id)
            await self.handle_additional_actions()
            await self.edit_message()
        except UserAdminInvalid:
            await self.message.edit("<b>No rights</b>")
        except ChatAdminRequired:
            await self.message.edit("<b>No rights</b>")
        except Exception as e:
            await self.message.edit(format_exc(e))

    async def handle_additional_actions(self):
        if "report_spam" in self.cause.lower().split():
            await self.client.invoke(
                functions.channels.ReportSpam(
                    channel=self.channel,
                    participant=self.user_id,
                    id=[self.message.reply_to_message.id],
                )
            )
        if "delete_history" in self.cause.lower().split():
            await self.client.invoke(
                functions.channels.DeleteParticipantHistory(
                    channel=self.channel, participant=self.user_id
                )
            )

    async def edit_message(self):
        text_c = "".join(
            f" {_}"
            for _ in self.cause.split()
            if _.lower() not in ["delete_history", "report_spam"]
        )
        await self.message.edit(
            f"<b>{self.name}</b> <code>banned!</code>"
            + f"\n{'<b>Cause:</b> <i>' + text_c.split(maxsplit=1)[1] + '</i>' if len(text_c.split()) > 1 else ''}"
        )


class UnbanHandler:
    def __init__(self, client: Client, message: Message):
        self.client = client
        self.message = message
        self.cause = text(message)
        self.channel = None
        self.user_id = None
        self.name = None

    async def handle_unban(self):
        if self.message.reply_to_message:
            await self.handle_reply_unban()
        elif not self.message.reply_to_message:
            await self.handle_non_reply_unban()
        else:
            await self.message.edit("<b>Unsupported</b>")

    async def handle_reply_unban(self):
        if self.message.chat.type not in ["private", "channel"]:
            user_for_unban, self.name = await get_user_and_name(self.message)
            await self.unban_user(user_for_unban)

    async def handle_non_reply_unban(self):
        if (
            self.message.chat.type not in ["private", "channel"]
            and len(self.cause.split()) > 1
        ):
            user_to_unban = await self.get_user_to_unban()
            if user_to_unban:
                self.name = (
                    user_to_unban.first_name
                    if getattr(user_to_unban, "first_name", None)
                    else user_to_unban.title
                )
                await self.unban_user(user_to_unban.id)

    async def get_user_to_unban(self):
        user_type = await check_username_or_id(self.cause.split(" ")[1])
        if user_type == "channel":
            return await self.client.get_chat(self.cause.split(" ")[1])
        if user_type == "user":
            return await self.client.get_users(self.cause.split(" ")[1])
        await self.message.edit("<b>Invalid user type</b>")
        return None

    async def unban_user(self, user_id):
        try:
            await self.client.unban_chat_member(self.message.chat.id, user_id)
            self.channel = await self.client.resolve_peer(self.message.chat.id)
            self.user_id = await self.client.resolve_peer(user_id)
            await self.edit_message()
        except UserAdminInvalid:
            await self.message.edit("<b>No rights</b>")
        except ChatAdminRequired:
            await self.message.edit("<b>No rights</b>")
        except Exception as e:
            await self.message.edit(format_exc(e))

    async def edit_message(self):
        text_c = "".join(
            f" {_}"
            for _ in self.cause.split()
            if _.lower() not in ["delete_history", "report_spam"]
        )
        await self.message.edit(
            f"<b>{self.name}</b> <code>unbanned!</code>"
            + f"\n{'<b>Cause:</b> <i>' + text_c.split(maxsplit=1)[1] + '</i>' if len(text_c.split()) > 1 else ''}"
        )


class KickHandler:
    def __init__(self, client: Client, message: Message):
        self.client = client
        self.message = message
        self.cause = text(message)
        self.channel = None
        self.user_id = None
        self.name = None

    async def handle_kick(self):
        if self.message.reply_to_message:
            await self.handle_reply_kick()
        elif not self.message.reply_to_message:
            await self.handle_non_reply_kick()
        else:
            await self.message.edit("<b>Unsupported</b>")

    async def handle_reply_kick(self):
        if self.message.chat.type not in ["private", "channel"]:
            if self.message.reply_to_message.from_user:
                await self.kick_user(self.message.reply_to_message.from_user.id)
            else:
                await self.message.edit("<b>Reply on user msg</b>")

    async def handle_non_reply_kick(self):
        if self.message.chat.type not in ["private", "channel"]:
            if len(self.cause.split()) > 1:
                user_to_kick = await self.get_user_to_kick()
                if user_to_kick:
                    self.name = (
                        user_to_kick.first_name
                        if getattr(user_to_kick, "first_name", None)
                        else user_to_kick.title
                    )
                    await self.kick_user(user_to_kick.id)
            else:
                await self.message.edit("<b>user_id or username</b>")

    async def get_user_to_kick(self):
        user_type = await check_username_or_id(self.cause.split(" ")[1])
        if user_type == "channel":
            return await self.client.get_chat(self.cause.split(" ")[1])
        if user_type == "user":
            return await self.client.get_users(self.cause.split(" ")[1])
        await self.message.edit("<b>Invalid user type</b>")
        return None

    async def kick_user(self, user_id):
        try:
            await self.client.ban_chat_member(
                self.message.chat.id,
                user_id,
                datetime.now() + timedelta(minutes=1),
            )
            self.channel = await self.client.resolve_peer(self.message.chat.id)
            self.user_id = await self.client.resolve_peer(user_id)
            await self.handle_additional_actions()
            await self.client.unban_chat_member(
                self.message.chat.id,
                user_id,
                datetime.now() + timedelta(minutes=1),
            )
            await self.edit_message()
        except UserAdminInvalid:
            await self.message.edit("<b>No rights</b>")
        except ChatAdminRequired:
            await self.message.edit("<b>No rights</b>")
        except Exception as e:
            await self.message.edit(format_exc(e))

    async def handle_additional_actions(self):
        if "report_spam" in self.cause.lower().split():
            await self.client.invoke(
                functions.channels.ReportSpam(
                    channel=self.channel,
                    participant=self.user_id,
                    id=[self.message.reply_to_message.id],
                )
            )
        if "delete_history" in self.cause.lower().split():
            await self.client.invoke(
                functions.channels.DeleteParticipantHistory(
                    channel=self.channel, participant=self.user_id
                )
            )

    async def edit_message(self):
        text_c = "".join(
            f" {_}"
            for _ in self.cause.split()
            if _.lower() not in ["delete_history", "report_spam"]
        )
        await self.message.edit(
            f"<b>{self.name}</b> <code>kicked!</code>"
            + f"\n{'<b>Cause:</b> <i>' + text_c.split(maxsplit=1)[1] + '</i>' if len(text_c.split()) > 1 else ''}"
        )


class KickDeletedAccountsHandler:
    def __init__(self, client: Client, message: Message):
        self.client = client
        self.message = message
        self.chat_id = message.chat.id
        self.kicked_count = 0

    async def kick_deleted_accounts(self):
        await self.message.edit("<b>Kicking deleted accounts...</b>")
        try:
            async for member in self.client.get_chat_members(self.chat_id):
                if member.user.is_deleted:
                    await self.kick_member(member.user.id)
                    self.kicked_count += 1
        except Exception as e:
            return await self.message.edit(format_exc(e))
        await self.message.edit(
            f"<b>Successfully kicked {self.kicked_count} deleted account(s)</b>",
        )

    async def kick_member(self, user_id):
        try:
            await self.client.ban_chat_member(
                self.chat_id, user_id, datetime.now() + timedelta(seconds=31)
            )
        except Exception as e:
            await self.message.edit(f"Failed to kick user {user_id}: {format_exc(e)}")


class TimeMuteHandler:
    def __init__(self, client: Client, message: Message):
        self.client = client
        self.message = message
        self.cause = text(message)
        self.chat_id = message.chat.id
        self.tmuted_users = db.get("core.ats", f"c{self.chat_id}", [])

    async def handle_tmute(self):
        if self.message.reply_to_message:
            await self.handle_reply_tmute()
        elif not self.message.reply_to_message:
            await self.handle_non_reply_tmute()
        else:
            await self.message.edit("<b>Unsupported</b>")

    async def handle_reply_tmute(self):
        if self.message.chat.type not in ["private", "channel"]:
            user_for_tmute, name = await get_user_and_name(self.message)
            if user_for_tmute in self.tmuted_users:
                await self.message.edit(f"<b>{name}</b> <code>already in tmute</code>")
            else:
                self.tmuted_users.append(user_for_tmute)
                db.set("core.ats", f"c{self.chat_id}", self.tmuted_users)
                await self.message.edit(
                    f"<b>{name}</b> <code>in tmute</code>"
                    + f"\n{'<b>Cause:</b> <i>' + self.cause.split(maxsplit=1)[1] + '</i>' if len(self.cause.split()) > 1 else ''}",
                )

    async def handle_non_reply_tmute(self):
        if self.message.chat.type not in ["private", "channel"]:
            if len(self.cause.split()) > 1:
                user_to_tmute = await self.get_user_to_tmute()
                if user_to_tmute:
                    name = (
                        user_to_tmute.first_name
                        if getattr(user_to_tmute, "first_name", None)
                        else user_to_tmute.title
                    )
                    if user_to_tmute.id not in self.tmuted_users:
                        self.tmuted_users.append(user_to_tmute.id)
                        db.set("core.ats", f"c{self.chat_id}", self.tmuted_users)
                        await self.message.edit(
                            f"<b>{name}</b> <code>in tmute</code>"
                            + f"\n{'<b>Cause:</b> <i>' + self.cause.split(maxsplit=2)[2] + '</i>' if len(self.cause.split()) > 2 else ''}",
                        )
                    else:
                        await self.message.edit(
                            f"<b>{name}</b> <code>already in tmute</code>",
                        )
            else:
                await self.message.edit("<b>user_id or username</b>")

    async def get_user_to_tmute(self):
        user_type = await check_username_or_id(self.cause.split(" ")[1])
        if user_type == "channel":
            return await self.client.get_chat(self.cause.split(" ")[1])
        if user_type == "user":
            return await self.client.get_users(self.cause.split(" ")[1])
        await self.message.edit("<b>Invalid user type</b>")
        return None


class TimeUnmuteHandler:
    def __init__(self, client: Client, message: Message):
        self.client = client
        self.message = message
        self.cause = text(message)
        self.chat_id = message.chat.id
        self.tmuted_users = db.get("core.ats", f"c{self.chat_id}", [])

    async def handle_tunmute(self):
        if self.message.reply_to_message:
            await self.handle_reply_tunmute()
        elif not self.message.reply_to_message:
            await self.handle_non_reply_tunmute()
        else:
            await self.message.edit("<b>Unsupported</b>")

    async def handle_reply_tunmute(self):
        if self.message.chat.type not in ["private", "channel"]:
            user_for_tunmute, name = await get_user_and_name(self.message)
            if user_for_tunmute not in self.tmuted_users:
                await self.message.edit(f"<b>{name}</b> <code>not in tmute</code>")
            else:
                self.tmuted_users.remove(user_for_tunmute)
                db.set("core.ats", f"c{self.chat_id}", self.tmuted_users)
                await self.message.edit(
                    f"<b>{name}</b> <code>tunmuted</code>"
                    + f"\n{'<b>Cause:</b> <i>' + self.cause.split(maxsplit=1)[1] + '</i>' if len(self.cause.split()) > 1 else ''}",
                )

    async def handle_non_reply_tunmute(self):
        if self.message.chat.type not in ["private", "channel"]:
            if len(self.cause.split()) > 1:
                user_to_tunmute = await self.get_user_to_tunmute()
                if user_to_tunmute:
                    name = (
                        user_to_tunmute.first_name
                        if getattr(user_to_tunmute, "first_name", None)
                        else user_to_tunmute.title
                    )
                    if user_to_tunmute.id not in self.tmuted_users:
                        await self.message.edit(
                            f"<b>{name}</b> <code>not in tmute</code>",
                        )
                    else:
                        self.tmuted_users.remove(user_to_tunmute.id)
                        db.set("core.ats", f"c{self.chat_id}", self.tmuted_users)
                        await self.message.edit(
                            f"<b>{name}</b> <code>tunmuted</code>"
                            + f"\n{'<b>Cause:</b> <i>' + self.cause.split(maxsplit=2)[2] + '</i>' if len(self.cause.split()) > 2 else ''}",
                        )
            else:
                await self.message.edit("<b>user_id or username</b>")

    async def get_user_to_tunmute(self):
        user_type = await check_username_or_id(self.cause.split(" ")[1])
        if user_type == "channel":
            return await self.client.get_chat(self.cause.split(" ")[1])
        if user_type == "user":
            return await self.client.get_users(self.cause.split(" ")[1])
        await self.message.edit("<b>Invalid user type</b>")
        return None


class TimeMuteUsersHandler:
    def __init__(self, client: Client, message: Message):
        self.client = client
        self.message = message
        self.chat_id = message.chat.id
        self.tmuted_users = db.get("core.ats", f"c{self.chat_id}", [])

    async def list_tmuted_users(self):
        if self.message.chat.type not in ["private", "channel"]:
            text = f"<b>All users</b> <code>{self.message.chat.title}</code> <b>who are now in tmute</b>\n\n"
            count = 0
            for user in self.tmuted_users:
                try:
                    name = await self.get_user_name(user)
                    if name:
                        count += 1
                        text += f"{count}. <b>{name}</b>\n"
                except PeerIdInvalid:
                    pass
            if count == 0:
                await self.message.edit("<b>No users in tmute</b>")
            else:
                text += f"\n<b>Total users in tmute</b> {count}"
                await self.message.edit(text)
        else:
            await self.message.edit("<b>Unsupported</b>")

    async def get_user_name(self, user_id):
        try:
            _name_ = await self.client.get_chat(user_id)
            if await check_username_or_id(_name_.id) == "channel":
                channel = await self.client.invoke(
                    functions.channels.GetChannels(
                        id=[
                            types.InputChannel(
                                channel_id=get_channel_id(_name_.id),
                                access_hash=0,
                            )
                        ]
                    )
                )
                return channel.chats[0].title
            if await check_username_or_id(_name_.id) == "user":
                user = await self.client.get_users(_name_.id)
                return user.first_name
        except PeerIdInvalid:
            return None


class UnmuteHandler:
    def __init__(self, client: Client, message: Message):
        self.client = client
        self.message = message
        self.cause = text(message)
        self.chat_id = message.chat.id
        self.permissions = message.chat.permissions

    async def handle_unmute(self):
        if self.message.reply_to_message:
            await self.handle_reply_unmute()
        elif not self.message.reply_to_message:
            await self.handle_non_reply_unmute()
        else:
            await self.message.edit("<b>Unsupported</b>")

    async def handle_reply_unmute(self):
        if self.message.chat.type not in ["private", "channel"]:
            user_for_unmute = self.message.reply_to_message.from_user
            if user_for_unmute:
                try:
                    await self.unmute_user(user_for_unmute.id)
                    await self.message.edit(
                        f"<b>{user_for_unmute.first_name}</b> <code>unmuted</code>"
                        + f"\n{'<b>Cause:</b> <i>' + self.cause.split(' ', maxsplit=1)[1] + '</i>' if len(self.cause.split()) > 1 else ''}"
                    )
                except UserAdminInvalid:
                    await self.message.edit("<b>No rights</b>")
                except ChatAdminRequired:
                    await self.message.edit("<b>No rights</b>")
                except Exception as e:
                    await self.message.edit(format_exc(e))
            else:
                await self.message.edit("<b>Reply on user msg</b>")

    async def handle_non_reply_unmute(self):
        if self.message.chat.type not in ["private", "channel"]:
            if len(self.cause.split()) > 1:
                user_to_unmute = await self.get_user_to_unmute()
                if user_to_unmute:
                    try:
                        await self.unmute_user(user_to_unmute.id)
                        await self.message.edit(
                            f"<b>{user_to_unmute.first_name}</b> <code>unmuted!</code>"
                            + f"\n{'<b>Cause:</b> <i>' + self.cause.split(' ', maxsplit=2)[2] + '</i>' if len(self.cause.split()) > 2 else ''}"
                        )
                    except UserAdminInvalid:
                        await self.message.edit("<b>No rights</b>")
                    except ChatAdminRequired:
                        await self.message.edit("<b>No rights</b>")
                    except Exception as e:
                        await self.message.edit(format_exc(e))
                else:
                    await self.message.edit("<b>User is not found</b>")
            else:
                await self.message.edit("<b>user_id or username</b>")

    async def get_user_to_unmute(self):
        user_type = await check_username_or_id(self.cause.split(" ")[1])
        if user_type == "channel":
            return await self.client.get_chat(self.cause.split(" ")[1])
        if user_type == "user":
            return await self.client.get_users(self.cause.split(" ")[1])
        await self.message.edit("<b>Invalid user type</b>")
        return None

    async def unmute_user(self, user_id):
        try:
            await self.client.restrict_chat_member(
                self.chat_id,
                user_id,
                self.permissions,
                datetime.now() + timedelta(seconds=30),
            )
        except Exception as e:
            await self.message.edit(format_exc(e))


class MuteHandler:
    def __init__(self, client: Client, message: Message):
        self.client = client
        self.message = message
        self.cause = text(message)
        self.chat_id = message.chat.id

    async def handle_mute(self):
        if self.message.reply_to_message:
            await self.handle_reply_mute()
        elif not self.message.reply_to_message:
            await self.handle_non_reply_mute()
        else:
            await self.message.edit("<b>Unsupported</b>")

    async def handle_reply_mute(self):
        if self.message.chat.type not in ["private", "channel"]:
            user_for_mute = self.message.reply_to_message.from_user
            if user_for_mute:
                mute_seconds = self.calculate_mute_seconds()
                try:
                    await self.mute_user(user_for_mute.id, mute_seconds)
                    await self.message.edit(
                        self.construct_mute_message(user_for_mute, mute_seconds)
                    )
                except UserAdminInvalid:
                    await self.message.edit("<b>No rights</b>")
                except ChatAdminRequired:
                    await self.message.edit("<b>No rights</b>")
                except Exception as e:
                    await self.message.edit(format_exc(e))
            else:
                await self.message.edit("<b>Reply on user msg</b>")

    async def handle_non_reply_mute(self):
        if self.message.chat.type not in ["private", "channel"]:
            if len(self.cause.split()) > 1:
                user_to_mute = await self.get_user_to_mute()
                if user_to_mute:
                    mute_seconds = self.calculate_mute_seconds()
                    try:
                        await self.mute_user(user_to_mute.id, mute_seconds)
                        await self.message.edit(
                            self.construct_mute_message(user_to_mute, mute_seconds)
                        )
                    except UserAdminInvalid:
                        await self.message.edit("<b>No rights</b>")
                    except ChatAdminRequired:
                        await self.message.edit("<b>No rights</b>")
                    except Exception as e:
                        await self.message.edit(format_exc(e))
                else:
                    await self.message.edit("<b>User is not found</b>")
            else:
                await self.message.edit("<b>user_id or username</b>")

    async def get_user_to_mute(self):
        user_type = await check_username_or_id(self.cause.split(" ")[1])
        if user_type == "channel":
            return await self.client.get_chat(self.cause.split(" ")[1])
        if user_type == "user":
            return await self.client.get_users(self.cause.split(" ")[1])
        await self.message.edit("<b>Invalid user type</b>")
        return None

    def calculate_mute_seconds(self):
        mute_seconds: int = 0
        for character in "mhdw":
            match = re.search(rf"(\d+|(\d+\.\d+)){character}", self.message.text)
            if match:
                value = float(match.string[match.start() : match.end() - 1])
                if character == "m":
                    mute_seconds += int(value * 60)
                if character == "h":
                    mute_seconds += int(value * 3600)
                if character == "d":
                    mute_seconds += int(value * 86400)
                if character == "w":
                    mute_seconds += int(value * 604800)
        return mute_seconds

    async def mute_user(self, user_id, mute_seconds):
        try:
            if mute_seconds > 30:
                await self.client.restrict_chat_member(
                    self.chat_id,
                    user_id,
                    ChatPermissions(),
                    datetime.now() + timedelta(seconds=mute_seconds),
                )
            else:
                await self.client.restrict_chat_member(
                    self.chat_id,
                    user_id,
                    ChatPermissions(),
                )
        except Exception as e:
            await self.message.edit(format_exc(e))

    def construct_mute_message(self, user, mute_seconds):
        mute_time: Dict[str, int] = {
            "days": mute_seconds // 86400,
            "hours": mute_seconds % 86400 // 3600,
            "minutes": mute_seconds % 86400 % 3600 // 60,
        }
        message_text = (
            f"<b>{user.first_name}</b> <code> was muted for"
            f" {((str(mute_time['days']) + ' day') if mute_time['days'] > 0 else '') + ('s' if mute_time['days'] > 1 else '')}"
            f" {((str(mute_time['hours']) + ' hour') if mute_time['hours'] > 0 else '') + ('s' if mute_time['hours'] > 1 else '')}"
            f" {((str(mute_time['minutes']) + ' minute') if mute_time['minutes'] > 0 else '') + ('s' if mute_time['minutes'] > 1 else '')}</code>"
            + f"\n{'<b>Cause:</b> <i>' + self.cause.split(' ', maxsplit=2)[2] + '</i>' if len(self.cause.split()) > 2 else ''}"
        )
        while " " in message_text:
            message_text = message_text.replace(" ", " ")
        return message_text


class DemoteHandler:
    def __init__(self, client: Client, message: Message):
        self.client = client
        self.message = message
        self.cause = text(message)
        self.chat_id = message.chat.id
        self.common_privileges_demote = {
            "is_anonymous": False,
            "can_manage_chat": False,
            "can_change_info": False,
            "can_post_messages": False,
            "can_edit_messages": False,
            "can_delete_messages": False,
            "can_manage_video_chats": False,
            "can_restrict_members": False,
            "can_invite_users": False,
            "can_pin_messages": False,
            "can_promote_members": False,
        }

    async def handle_demote(self):
        if self.message.reply_to_message:
            await self.handle_reply_demote()
        elif not self.message.reply_to_message:
            await self.handle_non_reply_demote()
        else:
            await self.message.edit("<b>Unsupported</b>")

    async def handle_reply_demote(self):
        if self.message.chat.type not in ["private", "channel"]:
            user_for_demote = self.message.reply_to_message.from_user
            if user_for_demote:
                try:
                    await self.demote_user(user_for_demote.id)
                    await self.message.edit(
                        self.construct_demote_message(user_for_demote)
                    )
                except UserAdminInvalid:
                    await self.message.edit("<b>No rights</b>")
                except ChatAdminRequired:
                    await self.message.edit("<b>No rights</b>")
                except Exception as e:
                    await self.message.edit(format_exc(e))
            else:
                await self.message.edit("<b>Reply on user msg</b>")

    async def handle_non_reply_demote(self):
        if self.message.chat.type not in ["private", "channel"]:
            if len(self.cause.split()) > 1:
                user_to_demote = await self.get_user_to_demote()
                if user_to_demote:
                    try:
                        await self.demote_user(user_to_demote.id)
                        await self.message.edit(
                            self.construct_demote_message(user_to_demote)
                        )
                    except UserAdminInvalid:
                        await self.message.edit("<b>No rights</b>")
                    except ChatAdminRequired:
                        await self.message.edit("<b>No rights</b>")
                    except Exception as e:
                        await self.message.edit(format_exc(e))
                else:
                    await self.message.edit("<b>User is not found</b>")
            else:
                await self.message.edit("<b>user_id or username not provided!</b>")

    async def get_user_to_demote(self):
        user_type = await check_username_or_id(self.cause.split(" ")[1])
        if user_type == "channel":
            return await self.client.get_chat(self.cause.split(" ")[1])
        if user_type == "user":
            return await self.client.get_users(self.cause.split(" ")[1])
        await self.message.edit("<b>Invalid user type</b>")
        return None

    async def demote_user(self, user_id):
        try:
            await self.client.promote_chat_member(
                self.chat_id,
                user_id,
                privileges=ChatPrivileges(**self.common_privileges_demote),
            )
        except Exception as e:
            await self.message.edit(format_exc(e))

    def construct_demote_message(self, user):
        return (
            f"<b>{user.first_name}</b> <code>demoted!</code>"
            + f"\n{'<b>Cause:</b> <i>' + self.cause.split(' ', maxsplit=2)[2] + '</i>' if len(self.cause.split()) > 2 else ''}"
        )


class PromoteHandler:
    def __init__(self, client: Client, message: Message):
        self.client = client
        self.message = message
        self.cause = text(message)
        self.chat_id = message.chat.id
        self.common_privileges_promote = {
            "can_delete_messages": True,
            "can_restrict_members": True,
            "can_invite_users": True,
            "can_pin_messages": True,
        }

    async def handle_promote(self):
        if self.message.reply_to_message:
            await self.handle_reply_promote()
        elif not self.message.reply_to_message:
            await self.handle_non_reply_promote()
        else:
            await self.message.edit("<b>Unsupported</b>")

    async def handle_reply_promote(self):
        if self.message.chat.type not in ["private", "channel"]:
            user_for_promote = self.message.reply_to_message.from_user
            if user_for_promote:
                try:
                    await self.promote_user(user_for_promote.id)
                    await self.message.edit(
                        self.construct_promote_message(user_for_promote)
                    )
                except UserAdminInvalid:
                    await self.message.edit("<b>No rights</b>")
                except ChatAdminRequired:
                    await self.message.edit("<b>No rights</b>")
                except Exception as e:
                    await self.message.edit(format_exc(e))
            else:
                await self.message.edit("<b>Reply on user msg</b>")

    async def handle_non_reply_promote(self):
        if self.message.chat.type not in ["private", "channel"]:
            if len(self.cause.split()) > 1:
                user_to_promote = await self.get_user_to_promote()
                if user_to_promote:
                    try:
                        await self.promote_user(user_to_promote.id)
                        await self.message.edit(
                            self.construct_promote_message(user_to_promote)
                        )
                    except UserAdminInvalid:
                        await self.message.edit("<b>No rights</b>")
                    except ChatAdminRequired:
                        await self.message.edit("<b>No rights</b>")
                    except Exception as e:
                        await self.message.edit(format_exc(e))
                else:
                    await self.message.edit("<b>User is not found</b>")
            else:
                await self.message.edit("<b>user_id or username not provided!</b>")

    async def get_user_to_promote(self):
        user_type = await check_username_or_id(self.cause.split(" ")[1])
        if user_type == "channel":
            return await self.client.get_chat(self.cause.split(" ")[1])
        if user_type == "user":
            return await self.client.get_users(self.cause.split(" ")[1])
        await self.message.edit("<b>Invalid user type</b>")
        return None

    async def promote_user(self, user_id):
        try:
            await self.client.promote_chat_member(
                self.chat_id,
                user_id,
                privileges=ChatPrivileges(**self.common_privileges_promote),
            )
            if len(self.cause.split()) > 1 and self.message.chat.type == "group":
                await self.client.set_administrator_title(
                    self.chat_id,
                    user_id,
                    self.cause.split(maxsplit=1)[1],
                )
        except Exception as e:
            await self.message.edit(format_exc(e))

    def construct_promote_message(self, user):
        return (
            f"<b>{user.first_name}</b> <code>promoted!</code>"
            + f"\n{'<b>Prefix:</b> <i>' + self.cause.split(' ', maxsplit=1)[1] + '</i>' if len(self.cause.split()) > 1 else ''}"
        )


class AntiChannelsHandler:
    def __init__(self, client: Client, message: Message):
        self.client = client
        self.message = message
        self.chat_id = message.chat.id
        self.prefix = prefix

    async def handle_anti_channels(self):
        if self.message.chat.type != "group":
            await self.message.edit("<b>Not supported in non-group chats</b>")
            return

        command = self.message.command
        if len(command) == 1:
            await self.toggle_anti_channels_status()
        elif command[1] in ["enable", "on", "1", "yes", "true"]:
            await self.enable_anti_channels()
        elif command[1] in ["disable", "off", "0", "no", "false"]:
            await self.disable_anti_channels()
        else:
            await self.message.edit(
                f"<b>Usage: {self.prefix}antich [enable|disable]</b>"
            )

    async def toggle_anti_channels_status(self):
        current_status = db.get("core.ats", f"antich{self.chat_id}", False)
        new_status = not current_status
        db.set("core.ats", f"antich{self.chat_id}", new_status)
        if new_status:
            await self.message.edit("<b>Blocking channels in this chat enabled.</b>")
        else:
            await self.message.edit("<b>Blocking channels in this chat disabled.</b>")

    async def enable_anti_channels(self):
        db.set("core.ats", f"antich{self.chat_id}", True)
        group = await self.client.get_chat(self.chat_id)
        if group.linked_chat:
            db.set("core.ats", f"linked{self.chat_id}", group.linked_chat.id)
        else:
            db.set("core.ats", f"linked{self.chat_id}", 0)
        await self.message.edit("<b>Blocking channels in this chat enabled.</b>")

    async def disable_anti_channels(self):
        db.set("core.ats", f"antich{self.chat_id}", False)
        await self.message.edit("<b>Blocking channels in this chat disabled.</b>")


class DeleteHistoryHandler:
    def __init__(self, client: Client, message: Message):
        self.client = client
        self.message = message
        self.cause = text(message)
        self.chat_id = message.chat.id
        self.prefix = prefix

    async def handle_delete_history(self):
        if self.message.chat.type not in ["private", "channel"]:
            if self.message.reply_to_message:
                await self.handle_reply_delete_history()
            elif not self.message.reply_to_message:
                await self.handle_non_reply_delete_history()
            else:
                await self.message.edit("<b>Unsupported</b>")

    async def handle_reply_delete_history(self):
        if self.message.reply_to_message.from_user:
            try:
                user_for_delete, name = await get_user_and_name(self.message)
                await self.delete_user_history(user_for_delete, name)
            except UserAdminInvalid:
                await self.message.edit("<b>No rights</b>")
            except ChatAdminRequired:
                await self.message.edit("<b>No rights</b>")
            except Exception as e:
                await self.message.edit(format_exc(e))
        else:
            await self.message.edit("<b>Reply on user msg</b>")

    async def handle_non_reply_delete_history(self):
        if len(self.cause.split()) > 1:
            try:
                user_to_delete = await self.get_user_to_delete()
                if user_to_delete:
                    name = (
                        user_to_delete.first_name
                        if getattr(user_to_delete, "first_name", None)
                        else user_to_delete.title
                    )
                    await self.delete_user_history(user_to_delete.id, name)
                else:
                    await self.message.edit("<b>User is not found</b>")
            except PeerIdInvalid:
                await self.message.edit("<b>User is not found</b>")
            except UsernameInvalid:
                await self.message.edit("<b>User is not found</b>")
            except IndexError:
                await self.message.edit("<b>User is not found</b>")
        else:
            await self.message.edit("<b>user_id or username</b>")

    async def get_user_to_delete(self):
        user_type = await check_username_or_id(self.cause.split(" ")[1])
        if user_type == "channel":
            return await self.client.get_chat(self.cause.split(" ")[1])
        if user_type == "user":
            return await self.client.get_users(self.cause.split(" ")[1])
        await self.message.edit("<b>Invalid user type</b>")
        return None

    async def delete_user_history(self, user_id, name):
        try:
            channel = await self.client.resolve_peer(self.chat_id)
            user_id = await self.client.resolve_peer(user_id)
            await self.client.invoke(
                functions.channels.DeleteParticipantHistory(
                    channel=channel, participant=user_id
                )
            )
            await self.message.edit(
                f"<code>History from <b>{name}</b> was deleted!</code>"
                + f"\n{'<b>Cause:</b> <i>' + self.cause.split(' ', maxsplit=1)[1] + '</i>' if len(self.cause.split()) > 1 else ''}"
            )
        except UserAdminInvalid:
            await self.message.edit("<b>No rights</b>")
        except ChatAdminRequired:
            await self.message.edit("<b>No rights</b>")
        except Exception as e:
            await self.message.edit(format_exc(e))


class AntiRaidHandler:
    def __init__(self, client: Client, message: Message):
        self.client = client
        self.message = message
        self.chat_id = message.chat.id
        self.prefix = prefix

    async def handle_antiraid(self):
        command = self.message.command
        if len(command) > 1:
            if command[1] == "on":
                await self.enable_antiraid()
            elif command[1] == "off":
                await self.disable_antiraid()
        else:
            await self.toggle_antiraid()

    async def enable_antiraid(self):
        db.set("core.ats", f"antiraid{self.chat_id}", True)
        group = await self.client.get_chat(self.chat_id)
        if group.linked_chat:
            db.set("core.ats", f"linked{self.chat_id}", group.linked_chat.id)
        else:
            db.set("core.ats", f"linked{self.chat_id}", 0)
        await self.message.edit(
            "<b>Anti-raid mode enabled!\n"
            f"Disable with: </b><code>{self.prefix}antiraid off</code>"
        )

    async def disable_antiraid(self):
        db.set("core.ats", f"antiraid{self.chat_id}", False)
        await self.message.edit("<b>Anti-raid mode disabled</b>")

    async def toggle_antiraid(self):
        current_status = db.get("core.ats", f"antiraid{self.chat_id}", False)
        new_status = not current_status
        db.set("core.ats", f"antiraid{self.chat_id}", new_status)
        if new_status:
            group = await self.client.get_chat(self.chat_id)
            if group.linked_chat:
                db.set("core.ats", f"linked{self.chat_id}", group.linked_chat.id)
            else:
                db.set("core.ats", f"linked{self.chat_id}", 0)
            await self.message.edit(
                "<b>Anti-raid mode enabled!\n"
                f"Disable with: </b><code>{self.prefix}antiraid off</code>"
            )
        else:
            await self.message.edit("<b>Anti-raid mode disabled</b>")


class NoteSendHandler:
    def __init__(self, client: Client, message: Message):
        self.client = client
        self.message = message
        self.chat_id = message.chat.id
        self.prefix = prefix

    async def handle_note_send(self):
        if len(self.message.text.split()) >= 2:
            await self.message.edit("<b>Loading...</b>")

            note_name = self.message.text.split(maxsplit=1)[1]
            find_note = db.get("core.notes", f"note{note_name}", False)
            if find_note:
                try:
                    await self.send_note(find_note)
                except RPCError:
                    await self.message.edit(
                        "<b>Sorry, but this note is unavailable.\n\n"
                        f"You can delete this note with "
                        f"<code>{self.prefix}clear {note_name}</code></b>"
                    )
            else:
                await self.message.edit("<b>There is no such note</b>")
        else:
            await self.message.edit(
                f"<b>Example: <code>{self.prefix}note note_name</code></b>",
            )

    async def send_note(self, find_note):
        if find_note.get("MEDIA_GROUP"):
            await self.message.delete()
            await self.send_media_group(find_note)
        else:
            await self.message.delete()
            await self.copy_message(find_note)

    async def send_media_group(self, find_note):
        messages_grouped = await self.client.get_media_group(
            int(find_note["CHAT_ID"]), int(find_note["MESSAGE_ID"])
        )
        media_grouped_list = self.prepare_media_group(messages_grouped)
        if self.message.reply_to_message:
            await self.client.send_media_group(
                self.message.chat.id,
                media_grouped_list,
                reply_to_message_id=self.message.reply_to_message.id,
            )
        else:
            await self.client.send_media_group(self.message.chat.id, media_grouped_list)

    async def copy_message(self, find_note):
        if self.message.reply_to_message:
            await self.client.copy_message(
                self.message.chat.id,
                int(find_note["CHAT_ID"]),
                int(find_note["MESSAGE_ID"]),
                reply_to_message_id=self.message.reply_to_message.id,
            )
        else:
            await self.client.copy_message(
                self.message.chat.id,
                int(find_note["CHAT_ID"]),
                int(find_note["MESSAGE_ID"]),
            )

    def prepare_media_group(self, messages_grouped):
        media_grouped_list = []
        for _ in messages_grouped:
            if _.photo:
                media_grouped_list.append(self.prepare_photo(_))
            elif _.video:
                media_grouped_list.append(self.prepare_video(_))
            elif _.audio:
                media_grouped_list.append(self.prepare_audio(_))
            elif _.document:
                media_grouped_list.append(self.prepare_document(_))
        return media_grouped_list

    @staticmethod
    def prepare_photo(message):
        if message.caption:
            return InputMediaPhoto(message.photo.file_id, message.caption.markdown)
        return InputMediaPhoto(message.photo.file_id)

    @staticmethod
    def prepare_video(message):
        if message.caption:
            if message.video.thumbs:
                return InputMediaVideo(
                    message.video.file_id,
                    message.video.thumbs[0].file_id,
                    message.caption.markdown,
                )
            return InputMediaVideo(message.video.file_id, message.caption.markdown)
        if message.video.thumbs:
            return InputMediaVideo(
                message.video.file_id, message.video.thumbs[0].file_id
            )
        return InputMediaVideo(message.video.file_id)

    @staticmethod
    def prepare_audio(message):
        if message.caption:
            return InputMediaAudio(message.audio.file_id, message.caption.markdown)
        return InputMediaAudio(message.audio.file_id)

    @staticmethod
    def prepare_document(message):
        if message.caption:
            if message.document.thumbs:
                return InputMediaDocument(
                    message.document.file_id,
                    message.document.thumbs[0].file_id,
                    message.caption.markdown,
                )
            return InputMediaDocument(
                message.document.file_id, message.caption.markdown
            )
        if message.document.thumbs:
            return InputMediaDocument(
                message.document.file_id, message.document.thumbs[0].file_id
            )
        return InputMediaDocument(message.document.file_id)
