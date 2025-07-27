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
from pyrogram.errors import YouBlockedUser
from pyrogram.types import Message

from utils.conv import Conversation
from utils.misc import modules_help, prefix
from utils.scripts import format_exc


@Client.on_message(filters.command("sgb", prefix) & filters.me)
async def sg(client: Client, message: Message):
    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.id
    else:
        await message.edit(f"<b>Usage: </b><code>{prefix}sgb [id]</code>")
        return
    try:
        await message.edit("<code>Processing please wait</code>")
        bot_username = "@SangMata_beta_bot"
        async with Conversation(client, bot_username, timeout=15) as conv:
            await conv.send_message(str(user_id))
            response = await conv.get_response(timeout=10)
            if "you have used up your quota" in response.text:
                await message.edit(response.text.splitlines()[0])
                return
            return await message.edit(response.text)
    except YouBlockedUser:
        await message.edit("<i>Please unblock @SangMata_beta_bot first.</i>")
    except TimeoutError:
        await message.edit("<i>No response from bot within the timeout period.</i>")
    except Exception as e:
        await message.edit(f"<i>Error: {format_exc(e)}</i>")


modules_help["sangmata"] = {"sgb": "reply to any user"}
