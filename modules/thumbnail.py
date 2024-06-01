import os
from PIL import Image

from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import prefix, modules_help


@Client.on_message(filters.command("setthumb", prefix) & filters.me)
async def setthumb(_, message: Message):
    THUMB_PATH = "downloads/thumb"
    if message.reply_to_message:
        if not os.path.exists(THUMB_PATH):
            os.makedirs(THUMB_PATH)
        new_thumb = await message.reply_to_message.download()
        with Image.open(new_thumb) as img:
            if img.format in ["PNG", "JPG", "JPEG"]:
                new_path = os.path.join(THUMB_PATH, "thumb.jpg")
                os.rename(new_thumb, new_path)
                await message.edit_text("Thumbnail set successfully!")
    else:
        await message.edit_text("Kindly reply to a PHOTO Entity!")
        return


modules_help["thumb"] = {"setthumb [reply_to_photo]*": "set your own custom thumbnail"}
