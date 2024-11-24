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

import asyncio

from pyrogram import Client, enums, filters
from pyrogram.types import Message
from pyrogram.errors import RPCError

from utils.misc import modules_help, prefix
from utils.scripts import edit_or_reply


@Client.on_message(filters.command("sgb", prefix) & filters.me)
async def sg(client: Client, message: Message):
    lol = await edit_or_reply(message, "<code>Processing please wait</code>")
    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.id
    else:
        await message.edit(f"<b>Usage: </b><code>{prefix}sgb [id]</code>")
        return
    try:
        await client.send_message(
            "@SangMata_beta_bot", "/start", parse_mode=enums.ParseMode.MARKDOWN
        )
    except RPCError:
        await lol.edit(
            "**Please unblock @SangMata_beta_bot and try again**",
            parse_mode=enums.ParseMode.MARKDOWN,
        )
        return
    id = "@SangMata_beta_bot"
    chat = message.chat.id
    await client.send_message(id, user_id, parse_mode=enums.ParseMode.MARKDOWN)
    await asyncio.sleep(2)
    async for opt in client.get_chat_history("@SangMata_beta_bot", limit=1):
        hmm = opt.text
        if hmm.startswith("Forward"):
            await lol.edit(
                "**Unknown error occurred**", parse_mode=enums.ParseMode.MARKDOWN
            )
            return
        await lol.delete()
        await opt.copy(chat)


modules_help["sangmata"] = {"sgb": "reply to any user"}
