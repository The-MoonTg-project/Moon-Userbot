from . import get_help

__doc__ = get_help("help_antiflood")

import re
from pyrogram import Client, filters
from pyrogram.types import ChatPermissions

from pyUltroid.dB import DEVLIST
from pyUltroid.dB.antiflood_db import get_flood, get_flood_limit, rem_flood, set_flood
from pyUltroid.fns.admins import admin_check

from . import Button, Redis, asst, callback, eod, get_string, ultroid_cmd

_check_flood = {}

if Redis("ANTIFLOOD"):
    @Client.on_message(filters.chat(list(get_flood().keys())))
    async def flood_check(client, message):
        count = 1
        chat = message.chat.title
        chat_id = message.chat.id
        sender_id = message.from_user.id

        if chat_id in _check_flood:
            if sender_id in _check_flood[chat_id]:
                count = _check_flood[chat_id][sender_id]
                _check_flood[chat_id][sender_id] += 1
            else:
                _check_flood[chat_id][sender_id] = count
        else:
            _check_flood[chat_id] = {sender_id: count}

        if await admin_check(message, silent=True) or message.from_user.is_bot:
            return
        if sender_id in DEVLIST:
            return
        if _check_flood[chat_id][sender_id] >= int(get_flood_limit(chat_id)):
            try:
                name = message.from_user.first_name
                await client.restrict_chat_member(
                    chat_id, sender_id, permissions=ChatPermissions(can_send_messages=False)
                )
                del _check_flood[chat_id]
                await message.reply(f"#AntiFlood\n\n{get_string('antiflood_3')}")
                await asst.send_message(
                    int(Redis("LOG_CHANNEL")),
                    f"#Antiflood\n\n`Muted `[{name}](tg://user?id={sender_id})` in {chat}`",
                    reply_markup=Button.inline(
                        "Unmute", data=f"anti_{sender_id}_{chat_id}"
                    ),
                )
            except BaseException:
                pass

    @Client.on_callback_query(filters.regex("anti_(.*)"))
    async def unmuting(client, callback_query):
        ino = callback_query.data.decode("UTF-8").split("_")
        user = int(ino[1])
        chat = int(ino[2])
        user_name = (await client.get_users(user)).first_name
        chat_title = (await client.get_chat(chat)).title
        await client.restrict_chat_member(chat, user, permissions=ChatPermissions(can_send_messages=True))
        await callback_query.message.edit(
            f"#Antiflood\n\n`Unmuted `[{user_name}](tg://user?id={user})` in {chat_title}`"
        )

@ultroid_cmd(
    pattern="setflood ?(\\d+)",
    admins_only=True,
)
async def setflood(client, message):
    input_ = message.text.strip().split(" ")[1]
    if not input_:
        return await eod(message, "`What?`", time=5)
    if not input_.isdigit():
        return await eod(message, get_string("com_3"), time=5)
    if m := set_flood(message.chat.id, input_):
        return await eod(message, get_string("antiflood_4").format(input_))

@ultroid_cmd(
    pattern="remflood$",
    admins_only=True,
)
async def remove_flood(client, message):
    hmm = rem_flood(message.chat.id)
    try:
        del _check_flood[message.chat.id]
    except BaseException:
        pass
    if hmm:
        return await eod(message, get_string("antiflood_1"), time=5)
    await eod(message, get_string("antiflood_2"), time=5)

@ultroid_cmd(
    pattern="getflood$",
    admins_only=True,
)
async def getflood(client, message):
    if ok := get_flood_limit(message.chat.id):
        return await eod(message, get_string("antiflood_5").format(ok), time=5)
    await eod(message, get_string("antiflood_2"), time=5)
