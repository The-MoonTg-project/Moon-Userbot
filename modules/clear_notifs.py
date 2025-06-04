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

from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.raw import functions, types
from pyrogram.types import Message

from utils.misc import modules_help, prefix


@Client.on_message(filters.command(["clear_@"], prefix) & filters.me)
async def solo_mention_clear(client: Client, message: Message):
    await message.delete()
    peer = await client.resolve_peer(message.chat.id)
    request = functions.messages.ReadMentions(peer=peer)
    await client.invoke(request)


@Client.on_message(filters.command(["clear_all_@"], prefix) & filters.me)
async def global_mention_clear(client: Client, message: Message):
    counter: int = 0
    await message.edit_text(
        f"<b>Clearing all mentions...</b>\n\n<b>Cleared:</b> <code>{counter}</code> chats"
    )
    async for dialog in client.get_dialogs():
        peer = await client.resolve_peer(dialog.chat.id)
        request = functions.messages.ReadMentions(peer=peer)
        await client.invoke(request)
        counter += 1
        await message.edit_text(
            f"<b>Clearing all mentions...</b>\n\n<b>Cleared:</b> <code>{counter}</code> chats"
        )
    await message.delete()


@Client.on_message(filters.command(["clear_reacts"], prefix) & filters.me)
async def solo_reaction_clear(client: Client, message: Message):
    await message.delete()
    peer = await client.resolve_peer(message.chat.id)
    request = functions.messages.ReadReactions(peer=peer)
    await client.invoke(request)


@Client.on_message(filters.command(["clear_all_reacts"], prefix) & filters.me)
async def global_reaction_clear(client: Client, message: Message):
    counter: int = 0
    await message.edit_text(
        f"<b>Clearing all reactions...</b>\n\n<b>Cleared:</b> <code>{counter}</code> chats"
    )
    async for dialog in client.get_dialogs():
        peer = await client.resolve_peer(dialog.chat.id)
        request = functions.messages.ReadReactions(peer=peer)
        await client.invoke(request)
        counter += 1
        await message.edit_text(
            f"<b>Clearing all reactions...</b>\n\n<b>Cleared:</b> <code>{counter}</code> chats"
        )
    await message.delete()


modules_help["clear_notifs"] = {
    "clear_@": "clear all mentions in this chat",
    "clear_all_@": "clear all mentions in all chats",
    "clear_reacts": "clear all reactions in this chat",
    "clear_all_reacts": "clear all reactions in all chats (except private chats)",
}
