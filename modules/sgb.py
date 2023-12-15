import asyncio

from pyrogram import Client, enums, filters
from pyrogram.types import Message
from pyrogram.errors import RPCError

from utils.misc import modules_help, prefix

async def edit_or_reply(message, text, parse_mode=enums.ParseMode.MARKDOWN):
    """Edit Message If Its From Self, Else Reply To Message, (Only Works For Sudo's)"""
    if not message:
        return await message.edit(text, parse_mode=parse_mode)
    if not message.from_user:
        return await message.edit(text, parse_mode=parse_mode)
    return await message.edit(text, parse_mode=parse_mode)


@Client.on_message(filters.command("sgb", prefix) & filters.me)
async def sg(client: Client, message: Message):
    lol = await edit_or_reply(message, "`Processing please wait`", parse_mode=enums.ParseMode.MARKDOWN)
    if not message.reply_to_message:
        await lol.edit("`reply to any message`", parse_mode=enums.ParseMode.MARKDOWN)
    reply = message.reply_to_message
    if not reply.text:
        await lol.edit("`reply to any text message`", parse_mode=enums.ParseMode.MARKDOWN)
    chat = message.chat.id
    try:
        await client.send_message("@SangMata_beta_bot","/start", parse_mode=enums.ParseMode.MARKDOWN)
    except RPCError:
        await lol.edit("**Please unblock @SangMata_beta_bot and try again**", parse_mode=enums.ParseMode.MARKDOWN)
        return
    
    await reply.forward("@SangMata_beta_bot")
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
    "sgm": "reply to any user or id"
}