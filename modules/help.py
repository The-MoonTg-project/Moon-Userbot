#  Moon-Userbot - telegram userbot
#  Copyright (C) 2020-present Moon Userbot Organization
#
#  This program is free software: you can redistribute it and/or modify

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import format_module_help, with_reply
from utils.module import ModuleManager

module_manager = ModuleManager.get_instance()


@Client.on_message(filters.command(["help", "h"], prefix) & filters.me)
async def help_cmd(_, message: Message):
    if not module_manager.help_navigator:
        await message.edit("<b>Help system is not initialized yet. Please wait...</b>")
        return

    if len(message.command) == 1:
        await module_manager.help_navigator.send_page(message)
    elif message.command[1].lower() in modules_help:
        await message.edit(format_module_help(message.command[1].lower(), prefix))
    else:
        command_name = message.command[1].lower()
        module_found = False
        for module_name, commands in modules_help.items():
            for command in commands.keys():
                if command.split()[0] == command_name:
                    cmd = command.split(maxsplit=1)
                    cmd_desc = commands[command]
                    module_found = True
                    return await message.edit(
                        f"<b>Help for command <code>{prefix}{command_name}</code></b>\n"
                        f"Module: {module_name} (<code>{prefix}help {module_name}</code>)\n\n"
                        f"<code>{prefix}{cmd[0]}</code>"
                        f"{' <code>' + cmd[1] + '</code>' if len(cmd) > 1 else ''}"
                        f" — <i>{cmd_desc}</i>",
                    )
        if not module_found:
            await message.edit(f"<b>Module or command {command_name} not found</b>")


@Client.on_message(filters.command(["pn", "pp", "pq"], prefix) & filters.me)
@with_reply
async def handle_navigation(_, message: Message):
    if not module_manager.help_navigator:
        await message.edit("<b>Help system is not initialized yet. Please wait...</b>")
        return

    reply_message = message.reply_to_message
    if reply_message and "Help Page No:" in message.reply_to_message.text:
        cmd = message.command[0].lower()
        if cmd == "pn":
            if module_manager.help_navigator.next_page():
                await module_manager.help_navigator.send_page(reply_message)
                return await message.delete()
            await message.edit("No more pages available.")
        elif cmd == "pp":
            if module_manager.help_navigator.prev_page():
                await module_manager.help_navigator.send_page(reply_message)
                return await message.delete()
            return await message.edit("This is the first page.")
        elif cmd == "pq":
            await reply_message.delete()
            return await message.edit("Help closed.")


modules_help["help"] = {
    "help [module/command name]": "Get common/module/command help",
    "pn/pp/pq": "Navigate through help pages"
    + " (pn: next page, pp: previous page, pq: quit help)",
}
