from pyrogram import Client, filters, types
from pyrogram import enums as enums

@Client.on_message(filters.command("sqoute", prefix) & filters.me)
async def sqoute(client: Client, message: types.Message):
    if len(message.command) < 2:
        return await message.edit("<b>No arguments provided</b>", parse_mode=enums.ParseMode.HTML)
    text = message.text.split(maxsplit=1)[1]
    await message.delete()
    await client.send_message(message.chat.id, text, parse_mode=enums.ParseMode.HTML)
