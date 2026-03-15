
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

from requests import get
from utils.misc import modules_help, prefix


@Client.on_message(filters.command(["lrc", "lyrics"], prefix) & filters.me)
async def search_lyrics(_, message: Message):
    if len(message.command) < 2:
        return await message.edit("<b>Specify the song name in message text</b>")

    song_name = message.text.split(maxsplit=1)[1]
    if " - " in song_name:
        track, artist = song_name.split(" - ", 1)
    else:
        track, artist = song_name, None

    API_URL = "https://lrclib.net/api/search"

    try:
        if not artist:
            response = get(API_URL, params={"track_name": track})
        else:
            response = get(API_URL, params={"artist_name": artist, "track_name": track})

        response.raise_for_status()
        data = response.json()

        if not isinstance(data, list) or not data:
            return await message.edit("<b>No lyrics found for this song.</b>")

        result = None
        for item in data:
            if item.get("plainLyrics"):
                result = item
                break

        if not result:
            return await message.edit("<b>No lyrics found for this song.</b>")

        text = (
            f"<b>🆔 ID:</b> <code>{result.get('id', 'N/A')}</code>\n"
            f"<b>🎯 Name:</b> {result.get('trackName') or result.get('name') or 'N/A'}\n"
            f"<b>🎤 Artist:</b> {result.get('artistName') or 'N/A'}\n"
            f"<b>🖼 Album:</b> {result.get('albumName') or 'N/A'}\n\n"
            f"{result.get('plainLyrics')}\n\n"
            f"<i>source: {song_name}</i>"
        )

        # Telegram messages are capped around 4096 chars; keep a safe margin.
        if len(text) > 4090:
            text = text[:4090] + "\n\n<b>...lyrics truncated...</b>"

        return await message.edit(text)
    except Exception as e:
        print(f"Error fetching lyrics: {e}")
        return await message.edit("<b>An error occurred while fetching lyrics.</b>")


modules_help["lyrics"] = {
    "lrc": "Search for Lyrics of a song. Usage: <code>.lrc song name [optional - artist]</code>",
    "lyrics": "Search for Lyrics of a song. Usage: <code>.lrc song name [optional - artist]</code>",
}
