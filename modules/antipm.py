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

USER_WARNINGS = {}


@Client.on_message(
    filters.private
    & ~filters.me
    & ~filters.bot
    & ~in_contact_list
    & ~is_support
    & anti_pm_enabled
)
async def anti_pm_handler(client: Client, message: Message):
    user_id = message.from_user.id
    ids = message.chat.id
    b_f = await client.get_me()
    u_n = b_f.first_name
    user = await client.get_users(ids)
    u_f = user.first_name
    default_text = db.get("core.antipm", "antipm_msg", None)
    if default_text is None:
        default_text = f"""<b>Hello, {u_f}!
This is the Assistant Of {u_n}.</b>
<i>My Boss is away or busy as of now, You can wait for him to respond.
Do not spam further messages else I may have to block you!</i>

<b>This is an automated message by the assistant.</b>
<b><u>Currently You Have <code>{USER_WARNINGS.get(user_id, 0)}</code> Warnings.</u></b>
    """
    else:
        default_text = default_text.format(
            user=u_f, my_name=u_n, warns=USER_WARNINGS.get(user_id, 0)
        )

    if db.get("core.antipm", "spamrep", False):
        user_info = await client.resolve_peer(ids)
        await client.invoke(functions.messages.ReportSpam(peer=user_info))

    if db.get("core.antipm", "block", False):
        await client.block_user(user_id)

    if db.get("core.antipm", f"disallowusers{ids}") == user_id != db.get(
        "core.antipm", f"allowusers{ids}"
    ) or db.get("core.antipm", f"disallowusers{ids}") != user_id != db.get(
        "core.antipm", f"allowusers{ids}"
    ):
        default_pic = db.get("core.antipm", "antipm_pic", None)
        if default_pic:
            await client.send_photo(message.chat.id, default_pic, caption=default_text)
        else:
            await client.send_message(message.chat.id, default_text)

        if user_id in USER_WARNINGS:
            USER_WARNINGS[user_id] += 1
        else:
            USER_WARNINGS[user_id] = 1

        if USER_WARNINGS[user_id] > pm_limit:
            await client.send_message(
                message.chat.id,
                "<b>Ehm...! That was your Last warn, Bye Bye see you L0L</b>",
            )
            await client.block_user(user_id)
            del USER_WARNINGS[user_id]


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
async def add_contact(_, message: Message):
    ids = message.chat.id

    db.set("core.antipm", f"allowusers{ids}", ids)
    if ids in USER_WARNINGS:
        del USER_WARNINGS[ids]
    await message.edit("User Approved!")


@Client.on_message(filters.command(["d"], prefix) & filters.me)
async def del_contact(_, message: Message):
    ids = message.chat.id

    db.set("core.antipm", f"disallowusers{ids}", ids)
    db.remove("core.antipm", f"allowusers{ids}")
    await message.edit("User DisApproved!")


@Client.on_message(filters.command(["setantipmmsg", "sam"], prefix) & filters.me)
async def set_antipm_msg(_, message: Message):
    if not message.reply_to_message:
        db.set("core.antipm", "antipm_msg", None)
        await message.edit("antipm message set to default.")
        return

    msg = message.reply_to_message
    afk_msg = msg.text or msg.caption

    if not afk_msg:
        return await message.edit(
            "Reply to a text or caption message to set it as your antipm message."
        )

    if len(afk_msg) > 200:
        return await message.edit(
            "antipm message is too long. It should be less than 200 characters."
        )

    if "{user}" not in afk_msg:
        return await message.edit(
            "antipm message must contain <code>{user}</code> to mention the user."
        )
    if "{my_name}" not in afk_msg:
        return await message.edit(
            "antipm message must contain <code>{my_name}</code> to mention your name."
        )
    if "{warns}" not in afk_msg:
        return await message.edit(
            "antipm message must contain <code>{warns}</code> to mention the warns count."
        )

    old_afk_msg = db.get("core.antipm", "antipm_msg", None)
    if old_afk_msg:
        db.remove("core.antipm", "antipm_msg")
    db.set("core.antipm", "antipm_msg", afk_msg)
    await message.edit(f"antipm message set to:\n\n{afk_msg}")


@Client.on_message(filters.command(["setantipmpic", "sap"], prefix) & filters.me)
async def set_antipm_pic(_, message: Message):
    if not message.reply_to_message or not message.reply_to_message.photo:
        db.set("core.antipm", "antipm_pic", None)
        await message.edit("antipm picture set to default.")
        return

    await message.edit("Setting antipm picture...")

    photo = await message.reply_to_message.download("./antipm_pic.jpg")

    old_antipm_pic = db.get("core.antipm", "antipm_pic", None)
    if old_antipm_pic:
        db.remove("core.antipm", "antipm_pic")
    db.set("core.antipm", "antipm_pic", photo)
    await message.edit("antipm picture set successfully.")


modules_help["antipm"] = {
    "antipm [enable|disable]*": "Enable Pm permit",
    "antipm_report [enable|disable]*": "Enable spam reporting",
    "antipm_block [enable|disable]*": "Enable user blocking",
    "setantipmmsg [reply to message]*": "Set antipm message. Use {user} to mention the user and {my_name} to mention your name and {warns} to mention the warns count.",
    "sam [reply to message]*": "Set antipm message. Use {user} to mention the user and {my_name} to mention your name and {warns} to mention the warns count.",
    "setantipmpic [reply to photo]*": "Set antipm picture.",
    "sap [reply to photo]*": "Set antipm picture.",
    "a": "Approve User",
    "d": "DisApprove User",
}
