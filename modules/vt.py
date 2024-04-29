# Copyright (C) 2020-2021 by DevsExpo@Github, < https://github.com/DevsExpo >.
#
# This file is part of < https://github.com/DevsExpo/FridayUserBot > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/DevsExpo/blob/master/LICENSE >
#
# All rights reserved.

import os
import time

import requests
from pyrogram import Client, enums, filters
from pyrogram.types import Message

from utils.config import vt_key as vak
from utils.misc import modules_help, prefix
from utils.scripts import edit_or_reply, format_exc, progress


@Client.on_message(filters.command("vt", prefix) & filters.me)
async def scan_my_file(client: Client, message: Message):
    ms_ = await edit_or_reply(message, "`Please Wait! Scanning This File`")
    if not message.reply_to_message:
        return await ms_.edit(
            "`Please Reply To File To Scan For Viruses`",
            parse_mode=enums.ParseMode.MARKDOWN,
        )
    if not message.reply_to_message.document:
        return await ms_.edit(
            "`Please Reply To File To Scan For Viruses`",
            parse_mode=enums.ParseMode.MARKDOWN,
        )
    if vak is None:
        return await ms_.edit(
            "`You Need To Set VIRUSTOTAL_API_KEY For Functing Of This Plugin.`",
            parse_mode=enums.ParseMode.MARKDOWN,
        )
    if int(message.reply_to_message.document.file_size) > 32000000:
        return await ms_.edit(
            f"**File Too Large, Use `{prefix}vtl` instead**",
            parse_mode=enums.ParseMode.MARKDOWN,
        )
    c_time = time.time()
    downloaded_file_name = await message.reply_to_message.download(
        progress=progress,
        progress_args=(ms_, c_time, "`Downloading This File!`"),
    )

    url = "https://www.virustotal.com/vtapi/v2/file/scan"
    params = {"apikey": vak}
    files = {"file": (downloaded_file_name, open(downloaded_file_name, "rb"))}
    response = requests.post(url, files=files, params=params, timeout=10)
    try:
        r_json = response.json()
        md5 = r_json["md5"]
    except Exception as e:
        return await ms_.edit(format_exc(e))
    await ms_.edit(
        f'<b><u>Scanned {message.reply_to_message.document.file_name}</b></u>. <b>You Can Visit :</b> <a href="https://www.virustotal.com/gui/file/{md5}">Here</a> <b>In 5-10 Min To See File Report</b>'
    )
    if os.path.exists(downloaded_file_name):
        os.remove(downloaded_file_name)


@Client.on_message(filters.command("vtl", prefix) & filters.me)
async def scan_my_large_file(client: Client, message: Message):
    ms_ = await edit_or_reply(message, "`Please Wait! Scanning This File`")
    if not message.reply_to_message:
        return await ms_.edit(
            "`Please Reply To File To Scan For Viruses`",
            parse_mode=enums.ParseMode.MARKDOWN,
        )
    if not message.reply_to_message.document:
        return await ms_.edit(
            "`Please Reply To File To Scan For Viruses`",
            parse_mode=enums.ParseMode.MARKDOWN,
        )
    if vak is None:
        return await ms_.edit(
            "`You Need To Set VIRUSTOTAL_API_KEY For Functing Of This Plugin.`",
            parse_mode=enums.ParseMode.MARKDOWN,
        )
    if int(message.reply_to_message.document.file_size) > 650000000:
        return await ms_.edit(
            "**File Too Large, exceeded Max capacity of 650MB**",
            parse_mode=enums.ParseMode.MARKDOWN,
        )
    c_time = time.time()
    downloaded_file_name = await message.reply_to_message.download(
        progress=progress,
        progress_args=(ms_, c_time, "`Downloading This File!`"),
    )

    url1 = "https://www.virustotal.com/api/v3/files/upload_url"

    headers = {"accept": "application/json", "x-apikey": vak}

    rponse = requests.get(url1, headers=headers, timeout=10)
    try:
        r_json = rponse.json()
        upl_data = r_json["data"]
    except Exception as e:
        return await ms_.edit(format_exc(e))

    url = upl_data

    files = {"file": (downloaded_file_name, open(downloaded_file_name, "rb"))}
    headers = {"accept": "application/json", "x-apikey": vak}
    response = requests.post(url, files=files, headers=headers, timeout=10)

    r_json = response.json()
    analysis_url = r_json["data"]["links"]["self"]

    url = analysis_url

    headers = {"accept": "application/json", "x-apikey": vak}

    response_result = requests.get(url, headers=headers, timeout=10)

    try:
        r_json = response_result.json()
        md5 = r_json["meta"]["file_info"]["md5"]
    except Exception as e:
        return await ms_.edit(format_exc(e))
    await ms_.edit(
        f'<b><u>Scanned {message.reply_to_message.document.file_name}</b></u>. <b>You Can Visit :</b> <a href="https://www.virustotal.com/gui/file/{md5}">Here</a> <b>In 5-10 Min To See File Report</b>'
    )
    if os.path.exists(downloaded_file_name):
        os.remove(downloaded_file_name)


modules_help["virustotal"] = {
    "vt [reply to file]*": "Scan for viruses on Virus Total (for lower file size <32MB)",
    "vtl [reply to file]*": "Scan for viruses on Virus Total (for lower file size >=32MB)",
}
