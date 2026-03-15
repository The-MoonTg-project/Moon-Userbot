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

import html
from time import perf_counter

import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import MessageTooLong

from utils.config import CF_ACCOUNT_ID, CF_API_KEY
from utils.misc import modules_help, prefix


def _parse_cf_response(data) -> str:
    if not (isinstance(data, dict) and data.get("success")):
        errors = data.get("errors") if isinstance(data, dict) else None
        raise ValueError(str(errors) if errors else str(data))
    result = data.get("result") or {}
    return (
        result.get("response")
        or result.get("text")
        or result.get("output_text")
        or "No response returned."
    )


async def _call_cf_api(prompt: str) -> tuple:
    url = (
        f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}"
        "/ai/run/@cf/meta/llama-3.1-8b-instruct"
    )
    headers = {"Authorization": f"Bearer {CF_API_KEY}"}
    timeout = aiohttp.ClientTimeout(total=60)
    start = perf_counter()
    async with aiohttp.ClientSession(timeout=timeout) as session, \
            session.post(url, headers=headers, json={"prompt": prompt}) as response:
        data = await response.json(content_type=None)
    return _parse_cf_response(data), perf_counter() - start


@Client.on_message(filters.command(["ask", "ai"], prefix) & filters.me)
async def ask_ai(_, message: Message):
    if len(message.command) < 2:
        return await message.edit("<b>Specify the question in message text</b>")
    prompt = message.text.split(maxsplit=1)[1]

    if not CF_ACCOUNT_ID or not CF_API_KEY:
        return await message.edit(
            "<b>Missing Cloudflare credentials.</b>\n"
            "<b>Set:</b> <code>CF_ACCOUNT_ID</code> and <code>CF_API_KEY</code>"
        )

    text = f"<b>Prompt:</b> <code>{html.escape(prompt)}</code>\n\n"
    await message.edit(text + "<b>Running...</b>")

    try:
        answer, elapsed = await _call_cf_api(prompt)
        text += f"<b>Response:</b>\n<code>{html.escape(answer)}</code>\n\n"
        text += f"<b>Completed in {round(elapsed, 5)} seconds</b>"
    except aiohttp.ClientError as exc:
        text += f"<b>Request failed:</b> <code>{html.escape(str(exc))}</code>"
    except ValueError as exc:
        text += f"<b>API error:</b> <code>{html.escape(str(exc))}</code>"
    except Exception as exc:
        text += f"<b>Unexpected error:</b> <code>{html.escape(str(exc))}</code>"

    if len(text) > 3900:
        text = text[:3900] + "\n\n<b>...output truncated...</b>"

    try:
        await message.edit(text)
    except MessageTooLong:
        await message.edit(text[:3900])


modules_help["ai"] = {
    "ai": "Ask a question to AI and get an answer",
    "ask": "Ask a question to AI and get an answer",
}
