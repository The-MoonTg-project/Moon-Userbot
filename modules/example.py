#  Moon-Userbot - telegram userbot
#  Copyright (C) 2020-present Moon Userbot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the#  Moon-Userbot - telegram userbot
#  Copyright (C) 2020-present Moon Userbot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# This file contains example functions for the Moon Userbot. It includes two functions:
# example_edit and example_send. These functions are used to demonstrate the basic structure
# and functionality of a module in the Moon Userbot.
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from pyrogram import Client, enums, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix

# if your module has packages from PyPi

# from utils.scripts import import_library
# example_1 = import_library("example_1")
# example_2 = import_library("example_2")

# import_library() will automatically install required library
# if it isn't installed


# This function listens for the "example_edit" command and edits the message to display
# "This is an example module". If an error occurs, it edits the message to display the error details.
@Client.on_message(filters.command("example_edit", prefix) & filters.me)
async def example_edit(client: Client, message: Message):
    try:
        # Edit the message to display "This is an example module"
        await message.edit("<code>This is an example module</code>")
    except Exception as e:
        # If an error occurs, edit the message to display the error details
        await message.edit(
            f"<code>[{e.error_code}: {enums.MessageType.TEXT}] - {e.error_details}</code>"
        )


# This function listens for the "example_send" command and sends a new message saying
# "This is an example module". If an error occurs, it edits the original message to display the error details.
@Client.on_message(filters.command("example_send", prefix) & filters.me)
async def example_send(client: Client, message: Message):
    try:
        # Send a new message saying "This is an example module"
        await client.send_message(message.chat.id, "<b>This is an example module</b>")
    except Exception as e:
        # If an error occurs, edit the original message to display the error details
        await message.edit(
            f"<code>[{e.error_code}: {enums.MessageType.TEXT}] - {e.error_details}</code>"
        )


# This adds instructions for your module
modules_help["example"] = {
    "example_send": "example send",
    "example_edit": "example edit",
}

# modules_help["example"] = { "example_send [text]": "example send" }
#                  |            |              |        |
#                  |            |              |        └─ command description
#           module_name         command_name   └─ optional command arguments
#        (only snake_case)   (only snake_case too)
