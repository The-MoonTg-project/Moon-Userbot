#  Moon-Userbot - telegram userbot
#  Copyright (C) 2020-present Moon Userbot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from pyrogram import Client, enums, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix

@Client.on_message(filters.command("id", prefix) & filters.me)
async def id(client: Client, message: Message):
        text = "\n".join(
            [
                f"Chat ID: `{message.chat.id}`",
                f"Chat DC ID: `{message.chat.dc_id}`\n",
                f"Message ID: `{message.id}`",
                (f"Your ID: `{message.from_user.id}`" if message.from_user else f"Channel/Group ID: `{message.sender_chat.id}`"),
                (f"Your DC ID: `{message.from_user.dc_id}`" if message.from_user else f"Channel/Group ID: `{message.sender_chat.id}`"),
            ]
        )

        if (rtm := message.reply_to_message):
            text += f"\n\nReplied Message ID: `{rtm.id}`"

            if (user := rtm.from_user):
                text = "\n".join(
                    [
                        text,
                        f"Replied User ID: `{user.id}`",
                        f"Replied User DC ID: `{user.dc_id}`"
                    ]
                )

            else:
                text = "\n".join(
                    [
                        text,
                        f"Replied Chat ID: `{rtm.sender_chat.id}`",
                        f"Replied Chat DC ID: `{rtm.sender_chat.dc_id}`"
                    ]
                )

            if rtm.forward_date and (ffc := rtm.forward_from_chat):
                text = "\n".join(
                    [
                        text,
                        f"\nForwarded Message ID: `{rtm.forward_from_message_id}`",
                        f"Forwarded from Chat ID: `{ffc.id}`",
                        f"Forwarded from Chat DC ID: `{ffc.dc_id}`",
                    ]
                )


        await message.edit("**__" + text + "__**", parse_mode=enums.ParseMode.MARKDOWN)

modules_help["id"] = {
    "id": "simply run or reply to message",
}
