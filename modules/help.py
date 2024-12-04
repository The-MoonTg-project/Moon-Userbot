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

current_page = 0
total_pages = 0


async def send_page(message, module_list, page, total_page):
    start_index = (page - 1) * 10
    end_index = start_index + 10
    page_modules = module_list[start_index:end_index]
    text = "<b>Help for <a href=https://t.me/Moonub_chat>Moon-Userbot</a></b>\n"
    text += f"For more help on how to use a command, type <code>{prefix}help [module]</code>\n\n"
    text += f"Help Page No: {page}/{total_page}\n\n"
    for module_name in page_modules:
        commands = modules_help[module_name]
        text += f"<b>• {module_name.title()}:</b> {', '.join([f'<code>{prefix + cmd_name.split()[0]}</code>' for cmd_name in commands.keys()])}\n"
    text += f"\n<b>The number of modules in the userbot: {len(modules_help)}</b>"
    await message.edit(text, disable_web_page_preview=True)


@Client.on_message(filters.command(["help", "h"], prefix) & filters.me)
async def help_cmd(_, message: Message):
    if len(message.command) == 1:
        global current_page, total_pages
        module_list = list(modules_help.keys())
        total_pages = (len(module_list) + 9) // 10
        current_page = 1
        await send_page(message, module_list, current_page, total_pages)
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
    if message.reply_to_message and "Help Page No:" in message.reply_to_message.text:
        global current_page
        if message.command[0].lower() == "pn":
            if current_page < total_pages:
                current_page += 1
                await send_page(
                    message, list(modules_help.keys()), current_page, total_pages
                )
                return await message.reply_to_message.delete()
            await message.edit("No more pages available.")
        elif message.command[0].lower() == "pp":
            if current_page > 1:
                current_page -= 1
                await send_page(
                    message, list(modules_help.keys()), current_page, total_pages
                )
                return await message.reply_to_message.delete()
            return await message.edit("This is the first page.")
        elif message.command[0].lower() == "pq":
            await message.reply_to_message.delete()
            return await message.edit("Help closed.")


modules_help["help"] = {
    "help [module/command name]": "Get common/module/command help",
    "pn/pp/pq": "Navigate through help pages"
    + " (pn: next page, pp: previous page, pq: quit help)",
}
