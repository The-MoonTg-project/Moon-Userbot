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
import time
import requests
import urllib3
import mimetypes

from pyrogram import Client, filters, enums
from pyrogram.types import Message
from pyrogram.errors import MessageNotModified

from utils.misc import modules_help, prefix
from utils.scripts import format_exc, progress

from io import BytesIO

from utils.config import apiflash_key



def generate_screenshot(url):
    api_url = f'https://api.apiflash.com/v1/urltoimage?access_key={apiflash_key}&url={url}&format=png'
    response = requests.get(api_url)
    if response.status_code == 200:
        return BytesIO(response.content)
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
        message_id = None
        link = message.text.split(maxsplit=1)[1]
    elif message.reply_to_message:
        message_id = message.reply_to_message.id
        link = message.reply_to_message.text
    else:
        await message.edit(
            f"<b>Usage: </b><code>{prefix}urldl [url to download]</code>",
            parse_mode=enums.ParseMode.HTML
        )
        return

    await message.edit("<b>Downloading...</b>", parse_mode=enums.ParseMode.HTML)

    ext = '.' + link.split('.')[-1]

    resp = requests.get(link, stream=True)
    resp.raise_for_status()

    content_type = resp.headers.get('Content-Type').split(';')[0]
    extension = mimetypes.guess_extension(content_type)

    try:
        os.makedirs('downloads')
        if ext == extension:
            file_name = "downloads/" + link.split("/")[-1]
        else:
            file_name = "downloads/" + link.split("/")[-1] + extension
    except FileNotFoundError:
        if ext == extension:
            file_name = "downloads/" + link.split("/")[-1]
        else:
            file_name = "downloads/" + link.split("/")[-1] + extension
    except FileExistsError:
        if ext == extension:
            file_name = "downloads/" + link.split("/")[-1]
        else:
            file_name = "downloads/" + link.split("/")[-1] + extension


    try:
        # Get the total file size
        total_size = int(resp.headers.get('content-length', 0))
        print(total_size)

        with open(file_name, "wb") as f:
            downloaded = 0
            chunk_count = 0
            update_frequency = 800
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                chunk_count += 10
                progress_dl = (downloaded / total_size) * 100
                print(progress_dl)
                if chunk_count % update_frequency == 0:
                    try:
                        await message.edit_text(f"<b>Downloading...</b>\n<b>Progress:</b> {progress_dl:.2f}%")
                    except MessageNotModified:
                        continue

        ms_ = await message.edit("<b>Uploading...</b>")
        c_time = time.time()
        await client.send_document(message.chat.id, file_name, progress=progress, progress_args=(ms_, c_time, '`Uploading...`'), reply_to_message_id=message_id, parse_mode=enums.ParseMode.MARKDOWN)
        await message.delete()
    except ZeroDivisionError:
        await message.edit_text("<b>File to download not found</b>")
    except Exception as e:
        await message.edit_text(format_exc(e))
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)

@Client.on_message(filters.command("upload", prefix) & filters.me)
async def upload_cmd(_, message: Message):
    max_size = 512 * 1024 * 1024
    max_size_mb = 100

    min_file_age = 31
    max_file_age = 180

    ms_ = await message.edit("`Downloading...`", parse_mode=enums.ParseMode.MARKDOWN)
    c_time = time.time()

    try:
        file_name = await message.download(
            progress=progress,
            progress_args=(ms_, c_time, '`Downloading...`')
            )
    except ValueError:
        try:
            file_name = await message.reply_to_message.download(
                progress=progress,
                progress_args=(ms_, c_time, '`Downloading...`')
                )
        except ValueError:
            await message.edit("<b>File to upload not found</b>", parse_mode=enums.ParseMode.HTML)
            return

    if os.path.getsize(file_name) > max_size:
        await message.edit(f"<b>Files longer than {max_size_mb}MB isn't supported</b>", parse_mode=enums.ParseMode.HTML)
        if os.path.exists(file_name):
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
    if os.path.exists(file_name):
        os.remove(file_name)



@Client.on_message(filters.command(["ws", "webshot"], prefix) & filters.me)
async def webshot(client: Client, message: Message):
    if len(message.command) > 1:
        url = message.text.split(maxsplit=1)[1]
        if not url.startswith("https://"):
            url = "https://" + message.text.split(maxsplit=1)[1]
    elif message.reply_to_message:
        url = message.reply_to_message.text
        if not url.startswith("https://"):
            url = "https://" + message.text.split(maxsplit=1)[1]
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
            await message.reply_text("<code>Failed to generate screenshot...\nMake sure url is correct</code>")
    except Exception as e:
        await message.reply_text(f"An error occurred: {format_exc(e)}")

modules_help["url"] = {
    "short [url]*": "short url",
    "urldl [url]*": "download url content",
    "upload [file|reply]*": "upload file to internet",
    "webshot [link]*": "Screenshot of web page",
    "ws [reply to link]*": "Screenshot of web page",
}
