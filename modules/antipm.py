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
from pyrogram.raw import functions
from pyrogram.types import Message

from utils.config import pm_limit
from utils.db import db
from utils.misc import modules_help, prefix

anti_pm_enabled = filters.create(
    lambda _, __, ___: db.get("core.antipm", "status", False)
)

in_contact_list = filters.create(lambda _, __, message: message.from_user.is_contact)

is_support = filters.create(lambda _, __, message: message.chat.is_support)


message_counts = {}


@Client.on_message(
    filters.private
    & ~filters.me
    & ~filters.bot
    & ~in_contact_list
    & ~is_support
    & anti_pm_enabled
)
async def anti_pm_handler(client: Client, message: Message):
    m_n = 0
    warns = db.get("core.antipm", "warns", m_n)
    user_id = message.from_user.id
    id = message.chat.id
    b_f = await client.get_me()
    u_n = b_f.first_name
    user = await client.get_users(id)
    u_f = user.first_name
    user_info = await client.resolve_peer(message.chat.id)
    default_text = f"""<b>Hello, {u_f}!
This is the Assistant Of {u_n}.</b>
<i>My Boss is away or busy as of now, You can wait for him to respond.
Do not spam further messages else I may have to block you!</i>

<b>This is an automated message by the assistant.</b>
<b><u>Currently You Have <code>{warns}</code> Warnings.</u></b>
"""
    if db.get("core.antipm", "spamrep", False):
        await client.invoke(functions.messages.ReportSpam(peer=user_info))
    if db.get("core.antipm", "block", False):
        await client.block_user(user_info)

    if db.get("core.antipm", f"disallowusers{id}") == user_id != db.get(
        "core.antipm", f"allowusers{id}"
    ) or db.get("core.antipm", f"disallowusers{id}") != user_id != db.get(
        "core.antipm", f"allowusers{id}"
    ):
        await client.send_message(message.chat.id, f"{default_text}")

        if user_id in message_counts:
            message_counts[user_id] += 1
            m_n = db.get("core.antipm", "warns")
            m_n_n = m_n + 1
            db.set("core.antipm", "warns", m_n_n)
        else:
            message_counts[user_id] = 1
            m_n_n = 1
            db.set("core.antipm", "warns", m_n_n)

        if message_counts[user_id] > pm_limit:
            await client.send_message(
                message.chat.id,
                "<b>Ehm...! That was your Last warn, Bye Bye see you L0L</b>",
            )
            await client.block_user(user_id)
            del message_counts[user_id]
            db.set("core.antipm", "warns", 0)


@Client.on_message(filters.command(["antipm", "anti_pm"], prefix) & filters.me)
async def anti_pm(_, message: Message):
    if len(message.command) == 1:
        if db.get("core.antipm", "status", False):
            await message.edit(
                "<b>Anti-PM status: enabled\n"
                f"Disable with: </b><code>{prefix}antipm disable</code>"
            )
        else:
            await message.edit(
                "<b>Anti-PM status: disabled\n"
                f"Enable with: </b><code>{prefix}antipm enable</code>"
            )
    elif message.command[1] in ["enable", "on", "1", "yes", "true"]:
        db.set("core.antipm", "status", True)
        await message.edit("<b>Anti-PM enabled!</b>")
    elif message.command[1] in ["disable", "off", "0", "no", "false"]:
        db.set("core.antipm", "status", False)
        await message.edit("<b>Anti-PM disabled!</b>")
    else:
        await message.edit(f"<b>Usage: {prefix}antipm [enable|disable]</b>")


@Client.on_message(filters.command(["antipm_report"], prefix) & filters.me)
async def antipm_report(_, message: Message):
    if len(message.command) == 1:
        if db.get("core.antipm", "spamrep", False):
            await message.edit(
                "<b>Spam-reporting enabled.\n"
                f"Disable with: </b><code>{prefix}antipm_report disable</code>"
            )
        else:
            await message.edit(
                "<b>Spam-reporting disabled.\n"
                f"Enable with: </b><code>{prefix}antipm_report enable</code>"
            )
    elif message.command[1] in ["enable", "on", "1", "yes", "true"]:
        db.set("core.antipm", "spamrep", True)
        await message.edit("<b>Spam-reporting enabled!</b>")
    elif message.command[1] in ["disable", "off", "0", "no", "false"]:
        db.set("core.antipm", "spamrep", False)
        await message.edit("<b>Spam-reporting disabled!</b>")
    else:
        await message.edit(f"<b>Usage: {prefix}antipm_report [enable|disable]</b>")


@Client.on_message(filters.command(["antipm_block"], prefix) & filters.me)
async def antipm_block(_, message: Message):
    if len(message.command) == 1:
        if db.get("core.antipm", "block", False):
            await message.edit(
                "<b>Blocking users enabled.\n"
                f"Disable with: </b><code>{prefix}antipm_block disable</code>"
            )
        else:
            await message.edit(
                "<b>Blocking users disabled.\n"
                f"Enable with: </b><code>{prefix}antipm_block enable</code>"
            )
    elif message.command[1] in ["enable", "on", "1", "yes", "true"]:
        db.set("core.antipm", "block", True)
        await message.edit("<b>Blocking users enabled!</b>")
    elif message.command[1] in ["disable", "off", "0", "no", "false"]:
        db.set("core.antipm", "block", False)
        await message.edit("<b>Blocking users disabled!</b>")
    else:
        await message.edit(f"<b>Usage: {prefix}antipm_block [enable|disable]</b>")


@Client.on_message(filters.command(["a"], prefix) & filters.me)
async def add_contact(client: Client, message: Message):
    id = message.chat.id

    db.set("core.antipm", f"allowusers{id}", id)
    db.set("core.antipm", "warns", 0)
    await message.edit("User Approved!")


@Client.on_message(filters.command(["d"], prefix) & filters.me)
async def del_contact(client: Client, message: Message):
    id = message.chat.id

    db.set("core.antipm", f"disallowusers{id}", id)
    db.remove("core.antipm", f"allowusers{id}")
    await message.edit("User DisApproved!")


modules_help["antipm"] = {
    "antipm [enable|disable]*": "Enable Pm permit",
    "antipm_report [enable|disable]*": "Enable spam reporting",
    "antipm_block [enable|disable]*": "Enable user blocking",
    "a": "Approve User",
    "d": "DisApprove User",
}


