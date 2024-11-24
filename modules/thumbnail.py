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
