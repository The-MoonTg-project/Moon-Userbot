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
    "uplr [filepath]/[reply to path]*": "Upload a file from your local machine to Telegram, delete the file after uploading",
}
