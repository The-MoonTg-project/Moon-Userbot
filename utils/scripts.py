#  Moon-Userbot - telegram userbot
#  Copyright (C) 2020-present Moon Userbot Organization
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

from pyrogram import Client, errors, types, enums
from typing import Optional
import asyncio
import sys
from .misc import modules_help, prefix, requirements_list


def text(message: types.Message):
    return message.text if message.text else message.caption


def restart():
    if re.match(r'^[\w\.-]+$', sys.executable):
        os.execvp(sys.executable, [sys.executable, "main.py"])
    else:
        raise ValueError("Invalid characters in program path")


def format_exc(e: Exception, hint: str = None):
    traceback.print_exc()
    if isinstance(e, errors.RPCError):
        return (
            f"<b>Telegram API error!</b>\n"
            f"<code>[{e.error_code} {e.error_message}] - {e.error_details}</code>"
        )
    else:
        if hint:
            hint_text = f"\n\n<b>Hint: {hint}</b>"
        else:
            hint_text = ""
        return (
            f"<b>Error!</b>\n" f"<code>{e.__class__.__name__}: {e}</code>" + hint_text
        )


def with_reply(func):
    async def wrapped(client: Client, message: types.Message):
        if not message.reply_to_message:
            await message.edit("<b>Reply to message is required</b>")
        else:
            return await func(client, message)

    return wrapped


async def interact_with(message: types.Message) -> types.Message:
    """
    Check history with bot and return bot's response
    Example:
    .. code-block:: python
        bot_msg = await interact_with(await bot.send_message("@BotFather", "/start"))
    :param message: already sent message to bot
    :return: bot's response
    """

    await asyncio.sleep(1)
    # noinspection PyProtectedMember
    response = await message._client.get_history(message.chat.id, limit=1)
    seconds_waiting = 0

    while response[0].from_user.is_self:
        seconds_waiting += 1
        if seconds_waiting >= 5:
            raise RuntimeError("bot didn't answer in 5 seconds")

        await asyncio.sleep(1)
        # noinspection PyProtectedMember
        response = await message._client.get_history(message.chat.id, limit=1)

    interact_with_to_delete.append(message.message_id)
    interact_with_to_delete.append(response[0].message_id)

    return response[0]


interact_with_to_delete = []


def format_module_help(module_name: str, prefix):
    commands = modules_help[module_name]

    help_text = f"<b>Help for |{module_name}|\n\nUsage:</b>\n"

    for command, desc in commands.items():
        cmd = command.split(maxsplit=1)
        args = " <code>" + cmd[1] + "</code>" if len(cmd) > 1 else ""
        help_text += f"<code>{prefix}{cmd[0]}</code>{args} — <i>{desc}</i>\n"

    return help_text


def format_small_module_help(module_name: str):
    commands = modules_help[module_name]

    help_text = f"<b>Help for |{module_name}|\n\nCommands list:\n"
    for command, _ in commands.items():
        cmd = command.split(maxsplit=1)
        args = " <code>" + cmd[1] + "</code>" if len(cmd) > 1 else ""
        help_text += f"<code>{prefix}{cmd[0]}</code>{args}\n"
    help_text += f"\nGet full usage: <code>{prefix}help {module_name}</code></b>"

    return help_text

async def edit_or_reply(message, text, parse_mode=enums.ParseMode.HTML):
    """Edit Message If Its From Self, Else Reply To Message"""
    if not message:
        return await message.edit(text, parse_mode=parse_mode)
    if not message.from_user:
        return await message.edit(text, parse_mode=parse_mode)
        if img.width == img.height:
            size = (512, 512)
        elif img.width < img.height:
            size = (max(512 * img.width // img.height, 1), 512)
        else:
            size = (512, max(512 * img.height // img.width, 1))

        img.resize(size).save(output, img_type)

    return output
