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


from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix


@Client.on_message(filters.command(["ping", "p"], prefix) & filters.me)
async def ping(client: Client, message: Message):
    latency = await client.ping()
    await message.edit(f"<b>Pong! {latency}ms</b>")


modules_help["ping"] = {
    "ping": "Check ping to Telegram servers",
}
