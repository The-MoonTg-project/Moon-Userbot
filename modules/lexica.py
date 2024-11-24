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
import re
import time
from bs4 import BeautifulSoup
import requests

from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import format_exc, format_module_help, progress
from utils.lexicapi import ImageGeneration, UpscaleImages, ImageModels


@Client.on_message(filters.command("upscale", prefix) & filters.me)
async def upscale(client: Client, message: Message):
    """Upscale Image Using Lexica API"""

    await message.edit("<code>Processing...</code>")
    try:
        photo_data = await message.download()
    except ValueError:
        try:
            photo_data = await message.reply_to_message.download()
        except ValueError:
            await message.edit("<b>File not found</b>")
            return
    try:
        with open(photo_data, "rb") as image_file:
            image = image_file.read()
        upscaled_image = await UpscaleImages(image)
        if message.reply_to_message:
            message_id = message.reply_to_message.id
            await message.delete()
        else:
            message_id = message.id
        await client.send_document(
            message.chat.id,
            upscaled_image,
            caption="Upscaled!",
            reply_to_message_id=message_id,
        )
        os.remove(upscaled_image)
        os.remove(photo_data)
    except Exception as e:
        await message.edit(format_exc(e))


@Client.on_message(filters.command("lgen", prefix) & filters.me)
async def lgen(client: Client, message: Message):
    try:
        await message.edit_text("<code>Processing...</code>")

        models = ImageModels()
        models_ids = models.values()

        if len(message.command) > 2:
            model_id = int(message.text.split()[1])
            if model_id not in models_ids:
                return await message.edit_text(format_module_help("lgen"))
            message_id = None
            prompt = " ".join(message.text.split()[2:])
        elif message.reply_to_message and len(message.command) > 1:
            model_id = int(message.text.split()[1])
            if model_id not in models_ids:
                return await message.edit_text(
                    f"<b>Usage: </b><code>{prefix}lgen [model_id]* [prompt/reply to prompt]*</code>\n <b>Available Models and IDs:</b> <blockquote>{models}</blockquote>"
                )
            message_id = message.reply_to_message.id
            prompt = message.reply_to_message.text
        else:
            return await message.edit_text(
                f"<b>Usage: </b><code>{prefix}lgen [model_id]* [prompt/reply to prompt]*</code>\n <b>Available Models and IDs:</b> <blockquote>{models}</blockquote>"
            )

        for key, val in models.items():
            if val == model_id:
                model_name = key

        img = await ImageGeneration(model_id, prompt)
        if img is None or img == 1 or img == 2:
            return await message.edit_text("Something went wrong!")
        if img == 69:
            return await message.edit_text("NSFW is not allowed")
        img_url = img[0]
        with open("generated_image.png", "wb") as f:
            f.write(requests.get(img_url, timeout=5).content)

        await message.delete()
        await client.send_document(
            message.chat.id,
            "generated_image.png",
            caption=f"<b>Prompt: </b><code>{prompt}</code>\n<b>Model: </b><code>{model_name}</code>",
            reply_to_message_id=message_id,
        )
        os.remove("generated_image.png")
    except Exception as e:
        await message.edit(format_exc(e))


@Client.on_message(filters.command("linsta", prefix) & filters.me)
async def linsta(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.edit_text(
            f"<b>Usage: </b><code>{prefix}linsta [link]*</code>"
        )
    link = message.text.split(maxsplit=1)[1]
    url = f"https://social-dl.vercel.app/api/download?url={link}&platform=Instagram"
    await message.edit_text("<code>Processing...</code>")
    try:
        response = requests.post(url)
        if response.status_code == 200:
            if response.json().get("code") == 2:
                if response.json().get("message") == "success":
                    download_url = response.json().get("content")[0].get("url")
                    soup = BeautifulSoup(requests.get(link).text, "html.parser")
                    title = soup.find("meta", property="og:title")
                    if title:
                        title_text = title["content"]
                    title_text = re.sub(r"#\w+", "", title_text)
                    title_text = title_text.replace("\n", "")
                    title_text = re.sub(" +", " ", title_text)
                    if ".mp4" in download_url:
                        ext = ".mp4"
                    elif ".jpg" in download_url:
                        ext = ".jpg"
                    elif ".png" in download_url:
                        ext = ".png"
                    elif ".webp" in download_url:
                        ext = ".webp"
                    elif ".gif" in download_url:
                        ext = ".gif"
                    with open(f"video_insta{ext}", "wb") as f:
                        f.write(requests.get(download_url).content)
                    await message.edit_text(
                        "Video downloaded successfully... Uploading"
                    )
                    await client.send_video(
                        message.chat.id,
                        f"video_insta{ext}",
                        caption=f"<b>Title: </b><code>{title_text}</code>",
                        progress=progress,
                        progress_args=(
                            message,
                            time.time(),
                            "Video downloaded successfully... Uploading",
                        ),
                    )
                    if os.path.exists(f"video_insta{ext}"):
                        os.remove(f"video_insta{ext}")
                    await message.delete()
                else:
                    await message.edit_text("Error: Failed to retrieve download URL")
            else:
                await message.edit_text("Error: Invalid response format")
        else:
            await message.edit_text("Error: Failed to send request")
    except Exception as e:
        await message.edit_text(format_exc(e))


modules_help["lexica"] = {
    "lgen [model_id]* [prompt/reply to prompt]*": "Generate Image with Lexica API",
    "upscale [cap/reply to image]*": "Upscale Image through Lexica API",
    "linsta [link]*": "Download Instagram Media",
}
