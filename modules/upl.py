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

import os

from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import format_exc


@Client.on_message(filters.command("upl", prefix) & filters.me)
async def upl(client: Client, message: Message):
    if len(message.command) > 1:
        link = message.text.split(maxsplit=1)[1]
    elif message.reply_to_message:
        link = message.reply_to_message.text
    else:
        await message.edit(
            f"<b>Usage: </b><code>{prefix}upl [filepath to upload]</code>"
        )
        return

    # Ensure that the link is an absolute path to a file on your local machine
    if not os.path.isfile(link):
        await message.edit(
            f"<b>Error: </b><code>{link}</code> is not a valid file path."
        )
        return

    try:
        await message.edit("<b>Uploading Now...</b>")
        await client.send_document(message.chat.id, link)
        await message.delete()
    except Exception as e:
        await message.edit(format_exc(e))


@Client.on_message(filters.command("dlf", prefix) & filters.me)
async def dlf(client: Client, message: Message):
    if message.reply_to_message:
        await client.download_media(message.reply_to_message)
        await message.edit("<b>Downloaded Successfully!</b>")
    else:
        await message.edit(
            f"<b>Usage: </b><code>{prefix}dlf [reply to a file]</code>"
        )


@Client.on_message(filters.command("moonlogs", prefix) & filters.me)
async def mupl(client: Client, message: Message):
    link = "moonlogs.txt"
    try:
        if os.path.exists(link):
            await message.edit("<b>Uploading Now...</b>")
            await client.send_document(message.chat.id, link)
            await message.delete()
        return await message.edit(
            "<b>Error: </b><code>LOGS</code> file doesn't exist."
        )
    except Exception as e:
        await message.edit(format_exc(e))


@Client.on_message(filters.command("uplr", prefix) & filters.me)
async def uplr(client: Client, message: Message):
    if len(message.command) > 1:
        link = message.text.split(maxsplit=1)[1]
    elif message.reply_to_message:
        link = message.reply_to_message.text
    else:
        await message.edit(
            f"<b>Usage: </b><code>{prefix}upl [filepath to upload]</code>"
        )
        return

    # Ensure that the link is an absolute path to a file on your local machine
    if not os.path.isfile(link):
        await message.edit(
            f"<b>Error: </b><code>{link}</code> is not a valid file path."
        )
        return

    try:
        await message.edit("<b>Uploading Now...</b>")
        await client.send_document(message.chat.id, link)
        await message.delete()
    except Exception as e:
        await message.edit(format_exc(e))
    finally:
        if os.path.exists(link):
            os.remove(link)


modules_help["uplud"] = {
    "upl [filepath]/[reply to path]*": "Upload a file from your local machine to Telegram",
    "dlf": "Download a file from Telegram to your local machine",
    "uplr [filepath]/[reply to path]*": "Upload a file from your local machine to Telegram, delete the file after uploading",
    "moonlogs": "Upload the moonlogs.txt file to Telegram"
}
