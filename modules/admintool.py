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

from contextlib import suppress

from pyrogram import Client, ContinuePropagation, filters
from pyrogram.enums import ChatType
from pyrogram.errors import (
    ChatAdminRequired,
    RPCError,
    UserAdminInvalid,
)
from pyrogram.raw import functions
from pyrogram.types import ChatPermissions, Message

from utils.db import db
from utils.handlers import (
    AntiChannelsHandler,
    AntiRaidHandler,
    BanHandler,
    DeleteHistoryHandler,
    DemoteHandler,
    KickDeletedAccountsHandler,
    KickHandler,
    MuteHandler,
    PromoteHandler,
    TimeMuteHandler,
    TimeMuteUsersHandler,
    TimeUnmuteHandler,
    UnbanHandler,
    UnmuteHandler,
)
from utils.misc import modules_help, prefix
from utils.scripts import format_exc, with_reply

db_cache: dict = db.get_collection("core.ats")


def update_cache():
    db_cache.clear()
    db_cache.update(db.get_collection("core.ats"))


def format_welcome_text(raw_text: str, user, chat) -> str:
    first = user.first_name or ""
    last = user.last_name or ""
    fullname = f"{first} {last}".strip()
    username = f"@{user.username}" if user.username else ""
    mention = user.mention(first)
    chatname = chat.title
    uid = user.id

    text = (
        raw_text.replace("{first}", first)
        .replace("{last}", last)
        .replace("{fullname}", fullname)
        .replace("{mention}", mention)
        .replace("{id}", str(uid))
        .replace("{chat_title}", chatname)
    )

    if "{username}" in text:
        text = text.replace("{username}", username or mention)

    return text


@Client.on_message(filters.group | filters.channel & ~filters.me)
async def admintool_handler(_, message: Message):
    if message.sender_chat and (
        message.sender_chat.type == "supergroup"
        or message.sender_chat.id == db_cache.get(f"linked{message.chat.id}", 0)
    ):
        raise ContinuePropagation

    if message.sender_chat and db_cache.get(f"antich{message.chat.id}", False):
        with suppress(RPCError):
            await message.delete()
            await message.chat.ban_member(message.sender_chat.id)

    tmuted_users = db_cache.get(f"c{message.chat.id}", [])
    if (
        message.from_user
        and message.from_user.id in tmuted_users
        or message.sender_chat
        and message.sender_chat.id in tmuted_users
    ):
        with suppress(RPCError):
            await message.delete()

    if db_cache.get(f"antiraid{message.chat.id}", False):
        with suppress(RPCError):
            await message.delete()
            if message.from_user:
                await message.chat.ban_member(message.from_user.id)
            elif message.sender_chat:
                await message.chat.ban_member(message.sender_chat.id)

    if message.new_chat_members and db_cache.get(
        f"welcome_enabled{message.chat.id}", False
    ):
        await message.reply(
            format_welcome_text(
                db_cache.get(f"welcome_text{message.chat.id}"),
                message.new_chat_members[0],
                message.chat,
            ),
            disable_web_page_preview=True,
        )

    raise ContinuePropagation


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


@Client.on_message(filters.command(["ban"], prefix) & filters.me)
async def ban_command(client: Client, message: Message):
    handler = BanHandler(client, message)
    await handler.handle_ban()


@Client.on_message(filters.command(["unban"], prefix) & filters.me)
async def unban_command(client: Client, message: Message):
    handler = UnbanHandler(client, message)
    await handler.handle_unban()


@Client.on_message(filters.command(["kick"], prefix) & filters.me)
async def kick_command(client: Client, message: Message):
    handler = KickHandler(client, message)
    await handler.handle_kick()


@Client.on_message(filters.command(["kickdel"], prefix) & filters.me)
async def kickdel_cmd(client: Client, message: Message):
    handler = KickDeletedAccountsHandler(client, message)
    await handler.kick_deleted_accounts()


@Client.on_message(filters.command(["tmute"], prefix) & filters.me)
async def tmute_command(client: Client, message: Message):
    handler = TimeMuteHandler(client, message)
    await handler.handle_tmute()
    update_cache()


@Client.on_message(filters.command(["tunmute"], prefix) & filters.me)
async def tunmute_command(client: Client, message: Message):
    handler = TimeUnmuteHandler(client, message)
    await handler.handle_tunmute()
    update_cache()


@Client.on_message(filters.command(["tmute_users"], prefix) & filters.me)
async def tunmute_users_command(client: Client, message: Message):
    handler = TimeMuteUsersHandler(client, message)
    await handler.list_tmuted_users()


@Client.on_message(filters.command(["unmute"], prefix) & filters.me)
async def unmute_command(client: Client, message: Message):
    handler = UnmuteHandler(client, message)
    await handler.handle_unmute()


@Client.on_message(filters.command(["mute"], prefix) & filters.me)
async def mute_command(client: Client, message: Message):
    handler = MuteHandler(client, message)
    await handler.handle_mute()


@Client.on_message(filters.command(["demote"], prefix) & filters.me)
async def demote_command(client: Client, message: Message):
    handler = DemoteHandler(client, message)
    await handler.handle_demote()


@Client.on_message(filters.command(["promote"], prefix) & filters.me)
async def promote_command(client: Client, message: Message):
    handler = PromoteHandler(client, message)
    await handler.handle_promote()


@Client.on_message(filters.command(["antich"], prefix))
async def anti_channels(client: Client, message: Message):
    handler = AntiChannelsHandler(client, message)
    await handler.handle_anti_channels()
    update_cache()


@Client.on_message(filters.command(["delete_history", "dh"], prefix))
async def delete_history(client: Client, message: Message):
    handler = DeleteHistoryHandler(client, message)
    await handler.handle_delete_history()


@Client.on_message(filters.command(["report_spam", "rs"], prefix))
@with_reply
async def report_spam(client: Client, message: Message):
    try:
        channel = await client.resolve_peer(message.chat.id)

        user_id, name = await get_user_and_name(message)
        peer = await client.resolve_peer(user_id)
        await client.invoke(
            functions.channels.ReportSpam(
                channel=channel,
                participant=peer,
                id=[message.reply_to_message.id],
            )
        )
    except Exception as e:
        await message.edit(format_exc(e))
    else:
        await message.edit(f"<b>Message</a> from {name} was reported</b>")


@Client.on_message(filters.command("pin", prefix) & filters.me)
@with_reply
async def pin(_, message: Message):
    try:
        await message.reply_to_message.pin()
        await message.edit("<b>Pinned!</b>")
    except Exception as e:
        await message.edit(format_exc(e))


@Client.on_message(filters.command("unpin", prefix) & filters.me)
@with_reply
async def unpin(_, message: Message):
    try:
        await message.reply_to_message.unpin()
        await message.edit("<b>Unpinned!</b>")
    except Exception as e:
        await message.edit(format_exc(e))


@Client.on_message(filters.command("ro", prefix) & filters.me)
async def ro(client: Client, message: Message):
    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await message.edit("<b>Invalid chat type</b>")
        return

    try:
        perms = message.chat.permissions
        perms_list = [
            perms.can_send_messages,
            perms.can_send_media_messages,
            perms.can_send_polls,
            perms.can_add_web_page_previews,
            perms.can_change_info,
            perms.can_invite_users,
            perms.can_pin_messages,
        ]
        db.set("core.ats", f"ro{message.chat.id}", perms_list)

        try:
            await client.set_chat_permissions(message.chat.id, ChatPermissions())
        except (UserAdminInvalid, ChatAdminRequired):
            await message.edit("<b>No rights</b>")
        else:
            await message.edit(
                "<b>Read-only mode activated!\n"
                f"Turn off with:</b><code>{prefix}unro</code>"
            )
    except Exception as e:
        await message.edit(format_exc(e))


@Client.on_message(filters.command("unro", prefix) & filters.me)
async def unro(client: Client, message: Message):
    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await message.edit("<b>Invalid chat type</b>")
        return

    try:
        perms_list = db.get(
            "core.ats",
            f"ro{message.chat.id}",
            [True, True, False, False, False, False, False],
        )

        common_perms = {
            "can_send_messages": perms_list[0],
            "can_send_media_messages": perms_list[1],
            "can_send_polls": perms_list[2],
            "can_add_web_page_previews": perms_list[3],
            "can_change_info": perms_list[4],
            "can_invite_users": perms_list[5],
            "can_pin_messages": perms_list[6],
        }

        perms = ChatPermissions(**common_perms)

        try:
            await client.set_chat_permissions(message.chat.id, perms)
        except (UserAdminInvalid, ChatAdminRequired):
            await message.edit("<b>No rights</b>")
        else:
            await message.edit("<b>Read-only mode disabled!</b>")
    except Exception as e:
        await message.edit(format_exc(e))


@Client.on_message(filters.command("antiraid", prefix) & filters.me)
async def antiraid(client: Client, message: Message):
    handler = AntiRaidHandler(client, message)
    await handler.handle_antiraid()
    update_cache()


@Client.on_message(filters.command(["welcome", "wc"], prefix) & filters.me)
async def welcome(_, message: Message):
    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return await message.edit("<b>Unsupported chat type</b>")

    if len(message.command) > 1:
        text = message.text.split(maxsplit=1)[1]
        db.set("core.ats", f"welcome_enabled{message.chat.id}", True)
        db.set("core.ats", f"welcome_text{message.chat.id}", text)

        await message.edit(
            f"<b>Welcome enabled in this chat\nText:</b> <code>{text}</code>"
        )
    else:
        db.set("core.ats", f"welcome_enabled{message.chat.id}", False)
        await message.edit("<b>Welcome disabled in this chat</b>")

    update_cache()


modules_help["admintool"] = {
    "ban [reply]/[username/id]* [reason] [report_spam] [delete_history]": "ban user in chat",
    "unban [reply]/[username/id]* [reason]": "unban user in chat",
    "kick [reply]/[userid]* [reason] [report_spam] [delete_history]": "kick user out of chat",
    "mute [reply]/[userid]* [reason] [1m]/[1h]/[1d]/[1w]": "mute user in chat",
    "unmute [reply]/[userid]* [reason]": "unmute user in chat",
    "promote [reply]/[userid]* [prefix]": "promote user in chat",
    "demote [reply]/[userid]* [reason]": "demote user in chat",
    "tmute [reply]/[username/id]* [reason]": "delete all new messages from user in chat",
    "tunmute [reply]/[username/id]* [reason]": "stop deleting all messages from user in chat",
    "tmute_users": "list of tmuted (.tmute) users",
    "antich [enable/disable]": "turn on/off blocking channels in this chat",
    "delete_history [reply]/[username/id]* [reason]": "delete history from member in chat",
    "report_spam [reply]*": "report spam message in chat",
    "pin [reply]*": "Pin replied message",
    "unpin [reply]*": "Unpin replied message",
    "ro": "enable read-only mode",
    "unro": "disable read-only mode",
    "antiraid [on|off]": "when enabled, anyone who writes message will be blocked. Useful in raids. "
    "Running without arguments equals to toggling state",
    "welcome [text]*": "enable auto-welcome to new users in groups. "
    "Running without text equals to disable"
    "\nSupported formats: <code>{first}</code>, <code>{last}</code>, <code>{username}</code>, <code>{mention}</code>, <code>{id}</code>, <code>{chat_title}</code>, <code>{chat_id}</code>",
    "kickdel": "Kick all deleted accounts",
}
