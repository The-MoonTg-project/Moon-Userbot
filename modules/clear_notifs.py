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

from pyrogram import Client, enums, filters
from pyrogram.errors import FloodWait
from pyrogram.raw import functions, types
from pyrogram.types import Message

from utils.misc import modules_help, prefix


@Client.on_message(filters.command(["clear_@"], prefix) & filters.me)
async def solo_mention_clear(client: Client, message: Message):
    await message.delete()
    peer = await client.resolve_peer(message.chat.id)
    request = functions.messages.ReadMentions(peer=peer)
    await client.send(request)


@Client.on_message(filters.command(["clear_all_@"], prefix) & filters.me)
async def global_mention_clear(client: Client, message: Message):
    request = functions.messages.GetAllChats(except_ids=[])
    try:
        result = await client.send(request)
    except FloodWait as e:
        await message.edit(
            f"<code>FloodWait received. Wait {e.x} seconds before trying again</code>",
            parse_mode=enums.ParseMode.HTML,
        )
        return
    await message.delete()
    for chat in result.chats:
        if type(chat) is types.Chat:
            peer_id = -chat.id
        elif type(chat) is types.Channel:
            peer_id = int(f"-100{chat.id}")
        peer = await client.resolve_peer(peer_id)
        request = functions.messages.ReadMentions(peer=peer)
        await client.send(request)


@Client.on_message(filters.command(["clear_reacts"], prefix) & filters.me)
async def solo_reaction_clear(client: Client, message: Message):
    await message.delete()
    peer = await client.resolve_peer(message.chat.id)
    request = functions.messages.ReadReactions(peer=peer)
    await client.send(request)


@Client.on_message(filters.command(["clear_all_reacts"], prefix) & filters.me)
async def global_reaction_clear(client: Client, message: Message):
    request = functions.messages.GetAllChats(except_ids=[])
    try:
        result = await client.send(request)
    except FloodWait as e:
        await message.edit(
            f"<code>FloodWait received. Wait {e.x} seconds before trying again</code>",
            parse_mode=enums.ParseMode.HTML,
        )
        return
    await message.delete()
    for chat in result.chats:
        if type(chat) is types.Chat:
            peer_id = -chat.id
        elif type(chat) is types.Channel:
            peer_id = int(f"-100{chat.id}")
        peer = await client.resolve_peer(peer_id)
        request = functions.messages.ReadReactions(peer=peer)
        await client.send(request)


modules_help["clear_notifs"] = {
    "clear_@": "clear all mentions in this chat",
    "clear_all_@": "clear all mentions in all chats",
    "clear_reacts": "clear all reactions in this chat",
    "clear_all_reacts": "clear all reactions in all chats (except private chats)",
}
