from pyrogram import Client, enums, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.config import cohere_key
from utils.db import db
from utils.scripts import format_exc, import_library, restart

cohere = import_library("cohere")

co = cohere.Client(cohere_key)

chatai_users = db.getaiusers()


@Client.on_message(filters.command("addai", prefix) & filters.me)
async def adduser(_, message: Message):
    if len(message.command) > 1:
        user_id = message.text.split(maxsplit=1)[1]
        if user_id.isdigit():
            user_id = int(user_id)
            db.addaiuser(user_id)
            await message.edit_text("<b>User ID Added</b>")
            restart()
        else:
            await message.edit_text("<b>User ID is invalid.</b>")
            return
    else:
        await message.edit_text(f"<b>Usage: </b><code>{prefix}addai [user_id]</code>")
        return


@Client.on_message(filters.command("remai", prefix) & filters.me)
async def remuser(_, message: Message):
    if len(message.command) > 1:
        user_id = message.text.split(maxsplit=1)[1]
        if user_id.isdigit():
            user_id = int(user_id)
            db.remaiuser(user_id)
            await message.edit_text("<b>User ID Removed</b>")
            restart()
        else:
            await message.edit_text("<b>User ID is invalid.</b>")
            return
    else:
        await message.edit_text(f"<b>Usage: </b><code>{prefix}remai [user_id]</code>")
        return


@Client.on_message(filters.user(users=chatai_users) & filters.text)
async def chatbot(_, message: Message):
    user_id = message.chat.id

    if user_id in chatai_users:
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
            model="command-r-plus",
            message=prompt,
            temperature=0.3,
            connectors=[{"id": "web-search", "options": {"site": "wikipedia.com"}}],
            prompt_truncation="AUTO",
        )

        db.add_chat_history(user_id, {"role": "CHATBOT", "message": response.text})

        await message.reply_text(
            f"{response.text}", parse_mode=enums.ParseMode.MARKDOWN
        )

    except Exception as e:
        await message.reply_text(f"An error occurred: {format_exc(e)}")


@Client.on_message(filters.command("chatoff", prefix) & filters.me)
async def chatoff(_, message: Message):
    db.remove("core.chatbot", "chatai_users")
    await message.reply_text("<b>ChatBot is off now</b>")
    restart()


@Client.on_message(filters.command("listai", prefix) & filters.me)
async def listai(_, message: Message):
    await message.edit_text(
        f"<b>User ID's Currently in AI ChatBot List:</b>\n <code>{chatai_users}</code>"
    )


modules_help["chatbot"] = {
    "addai [user_id]*": "Add A user to AI ChatBot List",
    "remai [user_id]*": "Remove A user from AI ChatBot List",
    "listai": "List A user from AI ChatBot List",
    "chatoff": "Turn off AI ChatBot",
}
