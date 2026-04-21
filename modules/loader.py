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

import hashlib
import os
import shutil
import subprocess
import sys

import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message

from utils import modules_help, prefix
from utils.db import db
from utils.scripts import load_module, unload_module

BASE_PATH = os.path.abspath(os.getcwd())
CATEGORIES = [
    "ai",
    "dl",
    "admin",
    "anime",
    "fun",
    "images",
    "info",
    "misc",
    "music",
    "news",
    "paste",
    "rev",
    "tts",
    "utils",
]


@Client.on_message(filters.command(["modhash", "mh"], prefix) & filters.me)
async def get_mod_hash(_, message: Message):
    if len(message.command) == 1:
        return
    url = message.command[1].lower()
    async with aiohttp.ClientSession() as session, session.get(url) as resp:
        if resp.status != 200:
            await message.edit(
                f"<b>Troubleshooting with downloading module <code>{url}</code></b>"
            )
            return
        content = await resp.read()

    await message.edit(
        f"<b>Module hash: <code>{hashlib.sha256(content).hexdigest()}</code>\n"
        f"Link: <code>{url}</code>\nFile: <code>{url.split('/')[-1]}</code></b>",
    )


@Client.on_message(filters.command(["loadmod", "lm"], prefix) & filters.me)
async def loadmod(client: Client, message: Message):
    if (
        not (
            message.reply_to_message
            and message.reply_to_message.document
            and message.reply_to_message.document.file_name.endswith(".py")
        )
        and len(message.command) == 1
    ):
        await message.edit("<b>Specify module to download</b>")
        return

    if len(message.command) > 1:
        await message.edit("<b>Fetching module...</b>")
        url = message.command[1].lower()

        if url.startswith(
            "https://raw.githubusercontent.com/The-MoonTg-project/custom_modules/main/"
        ):
            module_name = url.split("/")[-1].split(".")[0]
        elif "." not in url:
            module_name = url.lower()
            try:
                async with (
                    aiohttp.ClientSession() as session,
                    session.get(
                        "https://raw.githubusercontent.com/The-MoonTg-project/custom_modules/main/full.txt"
                    ) as resp,
                ):
                    f = await resp.text()
            except Exception:
                return await message.edit("Failed to fetch custom modules list")
            modules_dict = {
                line.split("/")[-1].split()[0]: line.strip() for line in f.splitlines()
            }
            if module_name in modules_dict:
                url = f"https://raw.githubusercontent.com/The-MoonTg-project/custom_modules/main/{modules_dict[module_name]}.py"
            else:
                await message.edit(
                    f"<b>Module <code>{module_name}</code> is not found</b>"
                )
                return
        else:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    "https://raw.githubusercontent.com/The-MoonTg-project/custom_modules/main/modules_hashes.txt"
                ) as resp:
                    modules_hashes = await resp.text()
                async with session.get(url) as resp:
                    if resp.status != 200:
                        await message.edit(
                            f"<b>Troubleshooting with downloading module <code>{url}</code></b>",
                        )
                        return
                    resp_content = await resp.read()

            if hashlib.sha256(resp_content).hexdigest() not in modules_hashes:
                return await message.edit(
                    "<b>Only <a href=https://github.com/The-MoonTg-project/custom_modules/tree/main/modules_hashes.txt>"
                    "verified</a> modules or from the official "
                    "<a href=https://github.com/The-MoonTg-project/custom_modules>"
                    "custom_modules</a> repository are supported!</b>",
                    disable_web_page_preview=True,
                )

            module_name = url.split("/")[-1].split(".")[0]

        async with aiohttp.ClientSession() as session, session.get(url) as resp:
            if resp.status != 200:
                await message.edit(
                    f"<b>Module <code>{module_name}</code> is not found</b>"
                )
                return
            resp_content = await resp.read()

        if not os.path.exists(f"{BASE_PATH}/modules/custom_modules"):
            os.mkdir(f"{BASE_PATH}/modules/custom_modules")

        with open(f"./modules/custom_modules/{module_name}.py", "wb") as f:
            f.write(resp_content)
    else:
        file_name = await message.reply_to_message.download()
        module_name = message.reply_to_message.document.file_name[:-3]

        with open(file_name, "rb") as f:
            content = f.read()

        async with (
            aiohttp.ClientSession() as session,
            session.get(
                "https://raw.githubusercontent.com/The-MoonTg-project/custom_modules/main/modules_hashes.txt"
            ) as resp,
        ):
            modules_hashes = await resp.text()

        if hashlib.sha256(content).hexdigest() not in modules_hashes:
            os.remove(file_name)
            return await message.edit(
                "<b>Only <a href=https://github.com/The-MoonTg-project/custom_modules/tree/main/modules_hashes.txt>"
                "verified</a> modules or from the official "
                "<a href=https://github.com/The-MoonTg-project/custom_modules>"
                "custom_modules</a> repository are supported!</b>",
                disable_web_page_preview=True,
            )
        os.rename(file_name, f"./modules/custom_modules/{module_name}.py")

    all_modules = db.get("custom.modules", "allModules", [])
    if module_name not in all_modules:
        all_modules.append(module_name)
        db.set("custom.modules", "allModules", all_modules)
    try:
        await load_module(module_name, client, message)
        await message.edit(f"<b>The module <code>{module_name}</code> is loaded!</b>")
    except Exception as e:
        await message.edit(
            f"<b>Failed to load module <code>{module_name}</code>:\n{e}</b>"
        )


@Client.on_message(filters.command(["unloadmod", "ulm"], prefix) & filters.me)
async def unload_mods(client: Client, message: Message):
    if len(message.command) <= 1:
        return

    module_name = message.command[1].lower()

    if module_name.startswith(
        "https://raw.githubusercontent.com/The-MoonTg-project/custom_modules/main/"
    ):
        module_name = module_name.split("/")[-1].split(".")[0]

    if os.path.exists(f"{BASE_PATH}/modules/custom_modules/{module_name}.py"):
        await unload_module(module_name, client)
        os.remove(f"{BASE_PATH}/modules/custom_modules/{module_name}.py")
        if module_name == "musicbot":
            subprocess.run(
                [sys.executable, "-m", "pip", "uninstall", "-y", "requirements.txt"],
                cwd=f"{BASE_PATH}/musicbot",
            )
            shutil.rmtree(f"{BASE_PATH}/musicbot")
        all_modules = db.get("custom.modules", "allModules", [])
        if module_name in all_modules:
            all_modules.remove(module_name)
            db.set("custom.modules", "allModules", all_modules)
        await message.edit(f"<b>The module <code>{module_name}</code> removed!</b>")
    elif os.path.exists(f"{BASE_PATH}/modules/{module_name}.py"):
        await message.edit(
            "<b>It is forbidden to remove built-in modules, it will disrupt the updater</b>"
        )
    else:
        await message.edit(f"<b>Module <code>{module_name}</code> is not found</b>")


@Client.on_message(filters.command(["loadallmods", "lmall"], prefix) & filters.me)
async def load_all_mods(client: Client, message: Message):
    await message.edit("<b>Fetching info...</b>")

    if not os.path.exists(f"{BASE_PATH}/modules/custom_modules"):
        os.mkdir(f"{BASE_PATH}/modules/custom_modules")

    try:
        async with (
            aiohttp.ClientSession() as session,
            session.get(
                "https://raw.githubusercontent.com/The-MoonTg-project/custom_modules/main/full.txt"
            ) as resp,
        ):
            f = await resp.text()
    except Exception:
        return await message.edit("Failed to fetch custom modules list")
    modules_list = f.splitlines()

    await message.edit("<b>Loading modules...</b>")
    async with aiohttp.ClientSession() as session:
        for module_name in modules_list:
            url = f"https://raw.githubusercontent.com/The-MoonTg-project/custom_modules/main/{module_name}.py"
            async with session.get(url) as resp:
                if resp.status != 200:
                    continue
                content = await resp.read()
            with open(
                f"./modules/custom_modules/{module_name.split('/')[1]}.py", "wb"
            ) as f:
                f.write(content)

    loaded = 0
    for module_name in modules_list:
        name = module_name.split("/")[-1].split()[0]
        try:
            await load_module(name, client)
            loaded += 1
        except Exception:
            pass

    await message.edit(
        f"<b>Successfully loaded new modules: {loaded}</b>",
    )


@Client.on_message(filters.command(["unloadallmods", "ulmall"], prefix) & filters.me)
async def unload_all_mods(client, message: Message):
    await message.edit("<b>Fetching info...</b>")

    if not os.path.exists(f"{BASE_PATH}/modules/custom_modules"):
        return await message.edit("<b>You don't have any modules installed</b>")

    custom_modules = [
        f[:-3]
        for f in os.listdir(f"{BASE_PATH}/modules/custom_modules")
        if f.endswith(".py")
    ]
    for name in custom_modules:
        await unload_module(name, client)

    shutil.rmtree(f"{BASE_PATH}/modules/custom_modules")
    db.set("custom.modules", "allModules", [])
    await message.edit("<b>Successfully unloaded all modules!</b>")


@Client.on_message(filters.command(["updateallmods"], prefix) & filters.me)
async def updateallmods(client, message: Message):
    await message.edit("<b>Updating modules...</b>")

    if not os.path.exists(f"{BASE_PATH}/modules/custom_modules"):
        os.mkdir(f"{BASE_PATH}/modules/custom_modules")

    modules_installed = list(os.walk("modules/custom_modules"))[0][2]

    if not modules_installed:
        return await message.edit("<b>You don't have any modules installed</b>")

    updated = 0
    async with aiohttp.ClientSession() as session:
        for module_file in modules_installed:
            if not module_file.endswith(".py"):
                continue
            try:
                async with session.get(
                    "https://raw.githubusercontent.com/The-MoonTg-project/custom_modules/main/full.txt"
                ) as resp:
                    f = await resp.text()
            except Exception:
                return await message.edit("Failed to fetch custom modules list")
            modules_dict = {
                line.split("/")[-1].split()[0]: line.strip() for line in f.splitlines()
            }
            module_name = module_file[:-3]
            if module_name in modules_dict:
                async with session.get(
                    f"https://raw.githubusercontent.com/The-MoonTg-project/custom_modules/main/{modules_dict[module_name]}.py"
                ) as resp:
                    if resp.status != 200:
                        continue
                    content = await resp.read()

                with open(f"./modules/custom_modules/{module_name}.py", "wb") as f:
                    f.write(content)
                try:
                    await load_module(module_name, client)
                    updated += 1
                except Exception:
                    pass

    await message.edit(f"<b>Successfully updated {updated} modules</b>")


modules_help["loader"] = {
    "loadmod [module_name]*": "Download module.\n"
    "Only modules from the official custom_modules repository and proven "
    "modules whose hashes are in modules_hashes.txt are supported",
    "unloadmod [module_name]*": "Delete module",
    "modhash [link]*": "Get module hash by link",
    "loadallmods": "Load all custom modules (use it at your own risk)",
    "unloadallmods": "Unload all custom modules",
    "updateallmods": "Update all custom modules"
    "\n\n* - required argument"
    "\n <b>short cmds:</b>"
    "\n loadmod - lm"
    "\n unloadmod - ulm"
    "\n modhash - mh"
    "\n loadallmods - lmall"
    "\n unloadallmods - ulmall",
}
