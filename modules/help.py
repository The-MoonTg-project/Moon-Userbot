#  Moon-Userbot - telegram userbot
#  Copyright (C) 2020-present Moon Userbot Organization
#
#  This program is free software: you can redistribute it and/or modify
        return await message.edit(
            f"<b>Trigger</b>:\n<code>{name}</code"
            f">\n<b>Answer</b>:\n{chat_filters[name]}",
            parse_mode=enums.ParseMode.HTML
        )

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from pyrogram import Client, filters, enums, enums
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import format_module_help


@Client.on_message(filters.command(["help", "h"], prefix) & filters.me)
async def help_cmd(_, message: Message):
    if len(message.command) == 1:
        msg_edited = False
        text = (
            "<b>Help for <a href=https://t.me/Moonub_chat>Moon-Userbot</a></b>\n"
            f"For more help on how to use a command, type <code>{prefix}help [module]</code>\n\n"
            "Available Modules:\n"
        )

        for module_name, module_commands in modules_help.items():
            text += f"<b>• {module_name.title()}:</b> {', '.join([f'<code>{prefix + cmd_name.split()[0]}</code>' for cmd_name in module_commands.keys()])}\n"
            if len(text) >= 2048:
                text += "</b>"
                if msg_edited:
                    await message.reply(text, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
                else:
                    await message.edit(text, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
                    msg_edited = True
                text = "<b>"

        text += f"<b>The number of modules in the userbot: {len(modules_help)}</b>"

        if msg_edited:
            await message.reply(text, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
        else:
            await message.edit(text, disable_web_page_preview=True, parse_mode=enums.ParseMode.HTML)
    elif message.command[1].lower() in modules_help:
        await message.edit(format_module_help(message.command[1].lower(), prefix), parse_mode=enums.ParseMode.HTML)
    else:
        # TODO: refactor this cringe
        command_name = message.command[1].lower()
        for name, commands in modules_help.items():
            for command in commands.keys():
                if command.split()[0] == command_name:
                    cmd = command.split(maxsplit=1)
                    cmd_desc = commands[command]
                    return await message.edit(
                        f"<b>Help for command <code>{prefix}{command_name}</code></b>\n"
                        f"Module: {name} (<code>{prefix}help {name}</code>)\n\n"
                        f"<code>{prefix}{cmd[0]}</code>"
                        f"{' <code>' + cmd[1] + '</code>' if len(cmd) > 1 else ''}"
                        f" — <i>{cmd_desc}</i>",
                        parse_mode=enums.ParseMode.HTML
                    )
        await message.edit(f"<b>Module {command_name} not found</b>", parse_mode=enums.ParseMode.HTML)

modules_help["help"] = {
    "help [module/command name]": "Get common/module/command help"}
