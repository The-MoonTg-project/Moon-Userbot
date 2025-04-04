#  Moon-Userbot - telegram userbot
#  Copyright (C) 2020-present Moon Userbot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

import io
import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix
from utils.scripts import format_exc, progress


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

    if not os.path.isfile(link):
        await message.edit(
            f"<b>Error: </b><code>{link}</code> is not a valid file path."
        )
        return

    try:
        await message.edit("<b>Uploading Now...</b>")
        await client.send_document(
            message.chat.id,
            link,
            progress=progress,
            progress_args=(message, time.time(), "<b>Uploading Now...</b>", link),
        )
        await message.delete()
    except Exception as e:
        await message.edit(format_exc(e))


@Client.on_message(filters.command("dlf", prefix) & filters.me)
async def dlf(client: Client, message: Message):
    if message.reply_to_message:
        await client.download_media(
            message.reply_to_message,
            progress=progress,
            progress_args=(message, time.time(), "<b>Uploading Now...</b>"),
        )
        await message.edit("<b>Downloaded Successfully!</b>")
    else:
        await message.edit(f"<b>Usage: </b><code>{prefix}dlf [reply to a file]</code>")


@Client.on_message(filters.command("moonlogs", prefix) & filters.me)
async def mupl(client: Client, message: Message):
    link = "moonlogs.txt"
    if os.path.exists(link):
        try:
            await message.edit("<b>Uploading Now...</b>")
            with open(link, "rb") as f:
                data = f.read()
            bio = io.BytesIO(data)
            bio.name = "moonlogs.txt"
            await client.send_document(
                message.chat.id,
                bio,
                progress=progress,
                progress_args=(message, time.time(), "<b>Uploading Now...</b>")
            )
            await message.delete()
        except Exception as e:
            await client.send_message(message.chat.id, format_exc(e))
    else:
        await message.edit("<b>Error: </b><code>LOGS</code> file doesn't exist.")


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

    if not os.path.isfile(link):
        await message.edit(
            f"<b>Error: </b><code>{link}</code> is not a valid file path."
        )
        return

    try:
        await message.edit("<b>Uploading Now...</b>")
        await client.send_document(
            message.chat.id,
            link,
            progress=progress,
            progress_args=(message, time.time(), "<b>Uploading Now...</b>", link),
        )
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
    "moonlogs": "Upload the moonlogs.txt file to Telegram",
}
