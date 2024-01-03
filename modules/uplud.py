import os

from pyrogram import Client, enums, filters
from pyrogram.types import Message
from utils.misc import modules_help, prefix
from utils.scripts import format_exc


@Client.on_message(filters.command("upl", prefix) & filters.me)
async def urldl(client: Client, message: Message):
   if len(message.command) > 1:
        link = message.text.split(maxsplit=1)[1]
   elif message.reply_to_message:
        link = message.reply_to_message.text
   else:
       await message.edit(
           f"<b>Usage: </b><code>{prefix}upl [filepath to upload]</code>",
           parse_mode=enums.ParseMode.HTML,
       )
       return

   # Ensure that the link is an absolute path to a file on your local machine
   if not os.path.isfile(link):
       await message.edit(
           f"<b>Error: </b><code>{link}</code> is not a valid file path.",
           parse_mode=enums.ParseMode.HTML,
       )
       return

   try:
       await message.edit("<b>Uploading Now...</b>", parse_mode=enums.ParseMode.HTML)
       await client.send_document(message.chat.id, link, parse_mode=enums.ParseMode.HTML)
       await message.delete()
   except Exception as e:
       await message.edit(format_exc(e), parse_mode=enums.ParseMode.HTML)

@Client.on_message(filters.command("uplr", prefix) & filters.me)
async def urldl(client: Client, message: Message):
   if len(message.command) > 1:
        link = message.text.split(maxsplit=1)[1]
   elif message.reply_to_message:
        link = message.reply_to_message.text
   else:
       await message.edit(
           f"<b>Usage: </b><code>{prefix}upl [filepath to upload]</code>",
           parse_mode=enums.ParseMode.HTML,
       )
       return

   # Ensure that the link is an absolute path to a file on your local machine
   if not os.path.isfile(link):
       await message.edit(
           f"<b>Error: </b><code>{link}</code> is not a valid file path.",
           parse_mode=enums.ParseMode.HTML,
       )
       return

   try:
       await message.edit("<b>Uploading Now...</b>", parse_mode=enums.ParseMode.HTML)
       await client.send_document(message.chat.id, link, parse_mode=enums.ParseMode.HTML)
       await message.delete()
   except Exception as e:
       await message.edit(format_exc(e), parse_mode=enums.ParseMode.HTML)
   finally:
       os.remove(link)

modules_help["uplud"] = {
   "upl": f"[filepath]/[reply to path]*"
   "uplr": f"[filepath]/[reply to path]* remove file after upload"
}
