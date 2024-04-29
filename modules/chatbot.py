import os
from utils.scripts import import_library, format_exc
from utils.config import cohere_key
from utils.db import db

cohere = import_library("cohere")

import cohere

co = cohere.Client(cohere_key)

from utils.misc import modules_help, prefix

from pyrogram import Client, filters, enums
from pyrogram.types import Message

chatai_users = db.getaiusers()
print(chatai_users)

@Client.on_message(filters.command("addai", prefix) & filters.me)
async def adduser(client: Client, message: Message):
    if len(message.command) > 1:
        user_id = message.text.split(maxsplit=1)[1]
        if user_id.isdigit():
            user_id = int(user_id)
            db.addaiuser(user_id)
            await message.edit_text(f"<b>User ID Added</b>")
        else:
            await message.edit_text(f"<b>User ID is invalid</b>")
            return
    else:
        await message.edit_text(f"<b>Usage: </b><code>{prefix}addai [user_id]</code>")
        return

@Client.on_message(filters.command("remai", prefix) & filters.me)
async def remuser(client: Client, message: Message):
    if len(message.command) > 1:
        user_id = message.text.split(maxsplit=1)[1]
        if user_id.isdigit():
            user_id = int(user_id)
            db.remaiuser(user_id)
            await message.edit_text(f"<b>User ID Removed</b>")
        else:
            await message.edit_text(f"<b>User ID is invalid</b>")
            return
    else:
        await message.edit_text(f"<b>Usage: </b><code>{prefix}remai [user_id]</code>")
        return

@Client.on_message(filters.user(users=chatai_users))
async def chatbot(client: Client, message: Message):
    user_id = message.chat.id

    if db.get("core.chatbot", f"addusers{user_id}") == user_id:
        pass
    else:
        return
    try:
        await message.reply_chat_action(enums.ChatAction.TYPING)

        chat_history = db.get_chat_history(user_id)

        prompt = message.text

        db.add_chat_history(user_id, {"role": "USER", "message": prompt})

        response = co.chat(
            chat_history=chat_history,
            model='command-r-plus',
            message=prompt,
            temperature=0.3,
            connectors=[{
                "id": "web-search",
                "options": {
                    "site": "wikipedia.com"
                }
            }],
            prompt_truncation="AUTO"
        )

        db.add_chat_history(user_id, {"role": "CHATBOT", "message": response.text})

        await message.reply_text(f"{response.text}", parse_mode=enums.ParseMode.MARKDOWN)

    except Exception as e:
        await message.reply_text(f"An error occurred: {format_exc(e)}")

@Client.on_message(filters.command("chatoff", prefix) & filters.me)
async def chatoff(client: Client, message: Message):
    db.remove("core.chatbot", "chatai_users")

    await message.reply_text("<b>ChatBot is off now</b>")


modules_help["chatbot"] = {
    "addai": "Add A user to AI ChatBot List",
    "remai": "Remove A user from AI ChatBot List",
    "chatoff": "Turn off AI ChatBot"
}