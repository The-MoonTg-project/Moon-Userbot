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
import urllib3
from pyrogram import Client, filters, enums
from pyrogram.types import Message
import requests
from utils.misc import modules_help, prefix
from utils.scripts import format_exc

import io
import requests

from utils.config import apiflash_key



def generate_screenshot(url):
    api_url = f'https://api.apiflash.com/v1/urltoimage?access_key={apiflash_key}&url={url}&format=png'
    response = requests.get(api_url)
    if response.status_code == 200:
        return io.BytesIO(response.content)
    else:
        return None


http = urllib3.PoolManager()

@Client.on_message(filters.command("short", prefix) & filters.me)
async def short(_, message: Message):
  if len(message.command) > 1:
      link = message.text.split(maxsplit=1)[1]
  elif message.reply_to_message:
      link = message.reply_to_message.text
  else:
      await message.edit(f"<b>Usage: </b><code>{prefix}short [url to short]</code>", parse_mode=enums.ParseMode.HTML)
      return

  r = http.request('GET', 'https://clck.ru/--?url='+link)

  await message.edit(r.data.decode().replace("https://", "<b>Shortened Url:</b>"), disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)



@Client.on_message(filters.command("urldl", prefix) & filters.me)
async def urldl(client: Client, message: Message):
    if len(message.command) > 1:
        link = message.text.split(maxsplit=1)[1]
    elif message.reply_to_message:
        link = message.reply_to_message.text
    else:
        await message.edit(
            f"<b>Usage: </b><code>{prefix}urldl [url to download]</code>",
            parse_mode=enums.ParseMode.HTML
        )
        return

    await message.edit("<b>Downloading...</b>", parse_mode=enums.ParseMode.HTML)
    file_name = "downloads/" + link.split("/")[-1]

    try:
        resp = requests.get(link)
        resp.raise_for_status()

        with open(file_name, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        await message.edit("<b>Uploading...</b>", parse_mode=enums.ParseMode.HTML)
        await client.send_document(message.chat.id, file_name, parse_mode=enums.ParseMode.HTML)
        await message.delete()
    except Exception as e:
        await message.edit(format_exc(e), parse_mode=enums.ParseMode.HTML)
    finally:
        os.remove(file_name)


@Client.on_message(filters.command("upload", prefix) & filters.me)
async def upload_cmd(_, message: Message):
    max_size = 512 * 1024 * 1024
    max_size_mb = 100

    min_file_age = 31
    max_file_age = 180

    await message.edit("<b>Downloading...</b>", parse_mode=enums.ParseMode.HTML)

    try:
        file_name = await message.download()
    except ValueError:
        try:
            file_name = await message.reply_to_message.download()
        except ValueError:
            await message.edit("<b>File to upload not found</b>", parse_mode=enums.ParseMode.HTML)
            return

    if os.path.getsize(file_name) > max_size:
        await message.edit(f"<b>Files longer than {max_size_mb}MB isn't supported</b>", parse_mode=enums.ParseMode.HTML)
        os.remove(file_name)
        return

    await message.edit("<b>Uploading...</b>", parse_mode=enums.ParseMode.HTML)
    with open(file_name, "rb") as f:
        response = requests.post(
            "https://x0.at",
            files={"file": f},
        )

    if response.ok:
        file_size_mb = os.path.getsize(file_name) / 1024 / 1024
        file_age = int(
            min_file_age
            + (max_file_age - min_file_age) *
            ((1 - (file_size_mb / max_size_mb)) ** 2)
        )
        url = response.text.replace("https://", "")
        await message.edit(
            f"<b>Your URL: {url}\nYour file will remain live for {file_age} days</b>",
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML
        )
    else:
        await message.edit(f"<b>API returned an error!\n" f"{response.text}\n Not allowed</b>", parse_mode=enums.ParseMode.HTML)
        print(response.text)

    os.remove(file_name)



@Client.on_message(filters.command(["ws", "webshot"], prefix) & filters.me)
async def webshot(client: Client, message: Message):
    if len(message.command) > 1:
        url = message.text.split(maxsplit=1)[1]
        if not url.startswith("https://"):
            await message.edit_text("Invalid URL. Please make sure the URL starts with 'https://'")
            return
    elif message.reply_to_message:
        url = message.reply_to_message.text
        if not url.startswith("https://"):
            await message.edit_text("Invalid URL. Please make sure the URL starts with 'https://'")
            return
    else:
        await message.edit_text(f"<b>Usage: </b><code>{prefix}webshot/{prefix}ws [url/reply to url]</code>", parse_mode=enums.ParseMode.HTML)
        return

    chat_id = message.chat.id

    try:
        screenshot_data = generate_screenshot(url)
        if screenshot_data:
            await message.delete()
            await client.send_photo(chat_id, screenshot_data, caption=f"Screenshot of {url}")
        else:
            await message.reply_text("Failed to generate screenshot.")
    except Exception as e:
        await message.reply_text(f"An error occurred: {format_exc(e)}")

modules_help["url"] = {
    "short [url]*": "short url",
    "urldl [url]*": "download url content",
    "upload [file|reply]*": "upload file to internet",
    "webshot [link]*": "Screenshot of web page",
    "ws [reply to link]*": "Screenshot of web page",
}
