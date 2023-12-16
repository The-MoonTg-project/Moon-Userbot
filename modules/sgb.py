import asyncio

from pyrogram import Client, enums, filters
from pyrogram.types import Message
from pyrogram.errors import RPCError


from utils.misc import modules_help, prefix
from utils.scripts import edit_or_reply


@Client.on_message(filters.command("sgb", prefix) & filters.me)
async def sg(client: Client, message: Message):
    lol = await edit_or_reply(message, "`Processing please wait`", parse_mode=enums.ParseMode.MARKDOWN)
    if len(message.command) > 1:
        reply = message.text.split(maxsplit=1)[1]
    elif message.reply_to_message:
        reply = message.reply_to_message.text
    else:
        await message.edit(f"<b>Usage: </b><code>{prefix}sgb [id]</code>", parse_mode=enums.ParseMode.HTML)
        return
    chat = message.chat.id
    try:
        await client.send_message("@SangMata_beta_bot","/start", parse_mode=enums.ParseMode.MARKDOWN)
    except RPCError:
        await lol.edit("**Please unblock @SangMata_beta_bot and try again**", parse_mode=enums.ParseMode.MARKDOWN)
        return
    id = "@SangMata_beta_bot"
    await client.send_message(id, reply, parse_mode=enums.ParseMode.MARKDOWN)
    await asyncio.sleep(2)
    async for opt in client.get_chat_history("@SangMata_beta_bot", limit=1):
        hmm = opt.text
        if hmm.startswith("Forward"):
            await lol.edit("**Can you kindly disable your privacy settings for good**", parse_mode=enums.ParseMode.MARKDOWN)
            return
            
        else:
            await lol.delete()
            await opt.copy(chat)

modules_help["sangmata"] = {
    "sgb": "reply to any user or id"
}