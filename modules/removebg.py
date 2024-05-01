# Copyright (C) 2020-2021 by DevsExpo@Github, < https://github.com/DevsExpo >.
#
# This file is part of < https://github.com/DevsExpo/FridayUserBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/DevsExpo/blob/master/LICENSE >
#
# All rights reserved.
# Modifed by @moonuserbot

import io
import os
from datetime import datetime
from functools import wraps
from io import BytesIO

import requests
from PIL import Image
from pyrogram import Client, enums, filters
from pyrogram.types import Message

from utils.config import rmbg_key
from utils.misc import modules_help, prefix
from utils.scripts import edit_or_reply, format_exc


async def convert_to_image(message, client) -> [None, str]:
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
            await exec(cmd)
    elif message.reply_to_message.audio:
        thumb = message.reply_to_message.audio.thumbs[0].file_id
        final_path = await client.download_media(thumb)
    elif message.reply_to_message.video or message.reply_to_message.animation:
        final_path = "fetched_thumb.png"
        vid_path = await client.download_media(message.reply_to_message)
        await exec(f"ffmpeg -i {vid_path} -filter:v scale=500:500 -an {final_path}")
    return final_path


def remove_background(photo_data):
    response = requests.post(
        "https://api.remove.bg/v1.0/removebg",
        files={"image_file": open(photo_data, "rb")},
        data={"size": "auto"},
        headers={"X-Api-Key": rmbg_key},
    )
    if response.status_code == 200:
        return BytesIO(response.content)
    print("Error:", response.status_code, response.text)
    return None


def _check_rmbg(func):
    @wraps(func)
    async def check_rmbg(client: Client, message: Message):
        if not rmbg_key:
            await edit_or_reply(
                message,
                "<code>Is Your RMBG Api 'rmbg_key' Valid Or You Didn't Add It??</code>"
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
    await pablo.edit("sending to ReMove.BG")
    input_file_name = cool
    files = {
        "image_file": (input_file_name, open(input_file_name, "rb")),
    }
    r = requests.post(
        "https://api.remove.bg/v1.0/removebg",
        headers={"X-Api-Key": rmbg_key},
        files=files,
        allow_redirects=True,
        stream=True,
    )
    if os.path.exists(cool):
        os.remove(cool)
    output_file_name = r
    contentType = output_file_name.headers.get("content-type")
    if "image" in contentType:
        with io.BytesIO(output_file_name.content) as remove_bg_image:
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
            "ReMove.BG API returned Errors. Please report to @moonub_chat"
            + f"\n`{output_file_name.content.decode('UTF-8')}")


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
                await message.edit(
                    "<b>File not found</b>"
                )
                return
        background_removed_data = remove_background(photo_data)

        if background_removed_data:
            await message.delete()
            await client.send_photo(
                chat_id, photo=background_removed_data, caption="Background removed!"
            )
        else:
            await message.edit_text(
                "`Is Your RMBG Api 'rmbg_key' Valid Or You Didn't Add It??`\n **Check logs for details**",
                parse_mode=enums.ParseMode.MARKDOWN,
            )
    except Exception as e:
        await message.reply_text(f"An error occurred: {format_exc(e)}")
    finally:
        if os.path.exists(photo_data):
            os.remove(photo_data)


modules_help["removebg"] = {
    "rebg [reply to image]*": "reemove background from image without transparency",
    "rmbg [reply to image]*": "remove background from image with transparency",
}
