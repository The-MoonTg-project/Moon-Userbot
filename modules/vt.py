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
from pyrogram import Client, filters, enums
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import edit_or_reply, format_exc, time_formatter, humanbytes, edit_or_send_as_file, get_text, progress
from utils.config import vt_key as vak


@Client.on_message(filters.command("vt", prefix) & filters.me)
async def scan_my_file(client, message):
    ms_ = await edit_or_reply(message, "`Please Wait! Scanning This File`")
    if not message.reply_to_message:
      return await ms_.edit("`Please Reply To File To Scan For Viruses`", parse_mode=enums.ParseMode.MARKDOWN)
    if not message.reply_to_message.document:
      return await ms_.edit("`Please Reply To File To Scan For Viruses`", parse_mode=enums.ParseMode.MARKDOWN)
    if not vak:
      return await ms_.edit("`You Need To Set VIRUSTOTAL_API_KEY For Functing Of This Plugin.`", parse_mode=enums.ParseMode.MARKDOWN)
    if int(message.reply_to_message.document.file_size) > 25000000:
      return await ms_.edit("`File Too Large , Limit is 25 Mb`", parse_mode=enums.ParseMode.MARKDOWN)
    c_time = time.time()
    downloaded_file_name = await message.reply_to_message.download(
        progress=progress,
        progress_args=(ms_, c_time, '`Downloading This File!`'),
    )

    url = "https://www.virustotal.com/vtapi/v2/file/scan"
    params = {"apikey": vak}
    files = {"file": (downloaded_file_name, open(downloaded_file_name, "rb"))}
    response = requests.post(url, files=files, params=params)
    try:
       r_json = response.json()
       scanned_url = r_json["permalink"]
    except:
      return await ms_.edit(f"`[{response.status_code}] - Unable To Scan File.`")
    await ms_.edit(f"<b><u>Scanned {message.reply_to_message.document.file_name}</b></u>. <b>You Can Visit :</b> <a href="/{scanned_url}/">Here</a> <b>In 5-10 Min To See File Report</b>")
    os.remove(downloaded_file_name)