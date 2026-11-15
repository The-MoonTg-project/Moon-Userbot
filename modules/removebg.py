# Copyright (C) 2020-2021 by DevsExpo@Github, < https://github.com/DevsExpo >.
#
# This file is part of < https://github.com/DevsExpo/FridayUserBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/DevsExpo/blob/master/LICENSE >
#
# All rights reserved.
# Modifed by @moonuserbot

import base64
import io
import json
import os
from datetime import datetime
from functools import wraps
from io import BytesIO

import aiohttp
from PIL import Image
from pyrogram import Client, enums, filters
from pyrogram.types import Message

from utils import modules_help, prefix
from utils.config import leonardo_key
from utils.scripts import edit_or_reply, format_exc


async def convert_to_image(message, client) -> None | str:
    """Convert Most Media Formats To Raw Image"""
    if not message:
        return None
    if not message.reply_to_message:
        return None
    final_path = None
    if not (
        message.reply_to_message.video
        or message.reply_to_message.photo
        or message.reply_to_message.sticker
        or message.reply_to_message.media
        or message.reply_to_message.animation
        or message.reply_to_message.audio
        or message.reply_to_message.document
    ):
        return None
    if message.reply_to_message.photo:
        final_path = await message.reply_to_message.download()
    elif message.reply_to_message.sticker:
        if message.reply_to_message.sticker.mime_type == "image/webp":
            final_path = "webp_to_png_s_proton.png"
            path_s = await message.reply_to_message.download()
            im = Image.open(path_s)
            im.save(final_path, "PNG")
        else:
            path_s = await client.download_media(message.reply_to_message)
            final_path = "lottie_proton.png"
            cmd = (
                f"lottie_convert.py --frame 0 -if lottie -of png {path_s} {final_path}"
            )
            await exec(cmd)  # skipcq
    elif message.reply_to_message.audio:
        thumb = message.reply_to_message.audio.thumbs[0].file_id
        final_path = await client.download_media(thumb)
    elif message.reply_to_message.video or message.reply_to_message.animation:
        final_path = "fetched_thumb.png"
        vid_path = await client.download_media(message.reply_to_message)
        await exec(
            f"ffmpeg -i {vid_path} -filter:v scale=500:500 -an {final_path}"
        )  # skipcq
    elif message.reply_to_message.document:
        if message.reply_to_message.document.mime_type == "image/jpeg":
            final_path = await message.reply_to_message.download()
        elif message.reply_to_message.document.mime_type == "image/png":
            final_path = await message.reply_to_message.download()
        elif message.reply_to_message.document.mime_type == "image/webp":
            final_path = "webp_to_png_s_proton.png"
            path_s = await message.reply_to_message.download()
            im = Image.open(path_s)
            im.save(final_path, "PNG")
        else:
            return None
    return final_path


# remove.bg's API moved to Leonardo.Ai on December 1, 2026.
# https://docs.leonardo.ai/docs/migrate-from-the-removebg-api-to-leonardoai
async def leonardo_remove_bg(image_data):
    """Return (png_bytes, None) on success or (None, error_text) on failure."""
    payload = {
        "model": "remove-bg",
        "ephemeral": True,
        "parameters": {
            "size": "auto",
            "format": "png",
            "guidances": {
                "image_reference": [
                    {
                        "image": {
                            "type": "BASE64",
                            "data": base64.b64encode(image_data).decode(),
                        }
                    }
                ]
            },
        },
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            "https://cloud.leonardo.ai/api/rest/v2/generationssync",
            json=payload,
            headers={"Authorization": f"Bearer {leonardo_key}"},
        ) as response:
            error_text = await response.text()
        try:
            data = json.loads(error_text)
        except ValueError:
            data = None
        results = data.get("results") if isinstance(data, dict) else None
        # Errors come back as JSON, often with HTTP 200 and an errors[] list.
        if not results or not results[0].get("url"):
            return None, error_text
        async with session.get(results[0]["url"]) as result:
            if result.status != 200:
                return None, f"Downloading the result failed: HTTP {result.status}"
            return await result.read(), None


async def remove_background(photo_data):
    with open(photo_data, "rb") as image_file:
        image_data = image_file.read()
    result, error_text = await leonardo_remove_bg(image_data)
    if result:
        return BytesIO(result)
    print("Error:", error_text)
    return None


def _check_rmbg(func):
    @wraps(func)
    async def check_rmbg(client: Client, message: Message):
        if not leonardo_key:
            await edit_or_reply(
                message,
                "<code>Set LEONARDO_API_KEY to use this module. remove.bg moved its API to Leonardo.Ai, so old RMBG_KEY keys won't work.</code>",
            )
        else:
            await func(client, message)

    return check_rmbg


@Client.on_message(filters.command("rmbg", prefix) & filters.me)
@_check_rmbg
async def rmbg(client: Client, message: Message):
    pablo = await edit_or_reply(message, "<code>Processing...</code>")
    if not message.reply_to_message:
        await pablo.edit("<code>Reply To A Image Please!</code>")
        return
    cool = await convert_to_image(message, client)
    if not cool:
        await pablo.edit("<code>Reply to a valid media first.</code>")
        return
    start = datetime.now()
    await pablo.edit("sending to Leonardo.Ai")
    with open(cool, "rb") as fh:
        r_content, error_text = await leonardo_remove_bg(fh.read())
    if os.path.exists(cool):
        os.remove(cool)
    if r_content:
        with io.BytesIO(r_content) as remove_bg_image:
            remove_bg_image.name = "BG_rem.png"
            await client.send_document(
                message.chat.id, remove_bg_image, reply_to_message_id=message.id
            )
        end = datetime.now()
        ms = (end - start).seconds
        await pablo.edit(
            f"<code>Removed image's Background in {ms} seconds, powered by </code> <b>@moonuserbot</b>"
        )
        if os.path.exists("BG_rem.png"):
            os.remove("BG_rem.png")
    else:
        await pablo.edit(
            "Leonardo.Ai API returned Errors. Please report to @moonub_chat"
            + f"\n`{error_text}"
        )


@Client.on_message(filters.command("rebg", prefix) & filters.me)
async def rembg(client: Client, message: Message):
    await message.edit("<code>Processing...</code>")
    chat_id = message.chat.id
    try:
        try:
            photo_data = await message.download()
        except ValueError:
            try:
                photo_data = await message.reply_to_message.download()
            except ValueError:
                await message.edit("<b>File not found</b>")
                return
        background_removed_data = await remove_background(photo_data)

        if background_removed_data:
            await message.delete()
            await client.send_photo(
                chat_id, photo=background_removed_data, caption="Background removed!"
            )
        else:
            await message.edit_text(
                "`Is your LEONARDO_API_KEY valid, or did you not add it?`\n **Check logs for details**",
                parse_mode=enums.ParseMode.MARKDOWN,
            )
    except Exception as e:
        await message.reply_text(f"An error occurred: {format_exc(e)}")
    finally:
        if os.path.exists(photo_data):
            os.remove(photo_data)


modules_help["removebg"] = {
    "rebg [reply to image]*": "remove background from image without transparency",
    "rmbg [reply to image]*": "remove background from image with transparency",
}
