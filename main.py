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

# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "pip",
#     "pyrofork==2.3.69",
#     "tgcrypto",
#     "humanize",
#     "pymongo",
#     "psutil",
#     "Pillow>=10.3.0",
#     "dnspython",
#     "environs",
#     "dulwich==1.1.0",
#     "aiohttp",
#     "aiofiles",
#     "bottle",
# ]
# ///
import asyncio
import logging
import os
import platform
import socket
import sqlite3
import subprocess
from wsgiref.simple_server import WSGIRequestHandler, WSGIServer, make_server

import aiohttp
from bottle import ServerAdapter
from pyrogram import Client, errors, idle
from pyrogram.enums.parse_mode import ParseMode
from pyrogram.raw.functions.account import DeleteAccount, GetAuthorizations

from app import bottle_app
from utils import config, gitrepo, userbot_version
from utils.db import db
from utils.module import ModuleManager
from utils.rentry import rentry_cleanup_job
from utils.scripts import load_module, restart

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
if SCRIPT_PATH != os.getcwd():
    os.chdir(SCRIPT_PATH)

common_params = {
    "api_id": config.api_id,
    "api_hash": config.api_hash,
    "hide_password": True,
    "workdir": SCRIPT_PATH,
    "app_version": userbot_version,
    "device_model": f"Moon-Userbot @ {gitrepo.head().decode('utf-8')[:7]}",
    "system_version": platform.version() + " " + platform.machine(),
    "sleep_threshold": 30,
    "test_mode": config.test_server,
    "parse_mode": ParseMode.HTML,
}


# Custom AsyncWSGIRefServer based on https://github.com/bottlepy/bottle/blob/2a743a302a71460bfe4c0b8b7cb99a306b0328c6/bottle.py#L3419
class AsyncWSGIRefServer(ServerAdapter):
    def run(self, handler):
        class FixedHandler(WSGIRequestHandler):
            def log_message(inner_self, format, *args):
                if not self.quiet:
                    return WSGIRequestHandler.log_message(inner_self, format, *args)

        handler_cls = self.options.get("handler_class", FixedHandler)
        server_cls = self.options.get("server_class", WSGIServer)

        if ":" in self.host:  # Fix wsgiref for IPv6 addresses.
            if getattr(server_cls, "address_family") == socket.AF_INET:

                class IPv6Server(server_cls):
                    address_family = socket.AF_INET6

                server_cls = IPv6Server

        self.srv = make_server(self.host, self.port, handler, server_cls, handler_cls)
        try:
            self.srv.serve_forever()
        finally:
            self.srv.server_close()

    def shutdown(self):
        if hasattr(self, "srv"):
            self.srv.shutdown()


if config.session_string:
    common_params["session_string"] = config.session_string
    # common_params["in_memory"] = True

app = Client("my_account", **common_params)


async def load_missing_modules():
    all_modules = db.get("custom.modules", "allModules", [])
    if not all_modules:
        return

    custom_modules_path = f"{SCRIPT_PATH}/modules/custom_modules"
    os.makedirs(custom_modules_path, exist_ok=True)

    try:
        async with (
            aiohttp.ClientSession() as session,
            session.get(
                f"https://raw.githubusercontent.com/The-MoonTg-project/custom_modules/{config.modules_repo_branch}/full.txt"
            ) as resp,
        ):
            f = await resp.text()
    except Exception:
        logging.error("Failed to fetch custom modules list")
        return
    modules_dict = {
        line.split("/")[-1].split()[0]: line.strip() for line in f.splitlines()
    }

    async with aiohttp.ClientSession() as session:
        for module_name in all_modules:
            module_path = f"{custom_modules_path}/{module_name}.py"
            if not os.path.exists(module_path) and module_name in modules_dict:
                url = f"https://raw.githubusercontent.com/The-MoonTg-project/custom_modules/{config.modules_repo_branch}/{modules_dict[module_name]}.py"
                async with session.get(url) as resp:
                    if resp.status == 200:
                        with open(module_path, "wb") as f:
                            f.write(await resp.read())
                        logging.info("Loaded missing module: %s", module_name)
                    else:
                        logging.warning("Failed to load module: %s", module_name)


async def main():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("moonlogs.txt"), logging.StreamHandler()],
        level=logging.INFO,
    )
    DeleteAccount.__new__ = None

    try:
        await app.start()
    except sqlite3.OperationalError as e:
        if str(e) == "database is locked" and os.name == "posix":
            logging.warning(
                "Session file is locked. Trying to kill blocking process..."
            )
            subprocess.run(["fuser", "-k", "my_account.session"], check=True)
            restart()
        raise
    except (errors.NotAcceptable, errors.Unauthorized) as e:
        logging.error(
            "%s: %s\nMoving session file to my_account.session-old...",
            e.__class__.__name__,
            e,
        )
        os.rename("./my_account.session", "./my_account.session-old")
        restart()

    await load_missing_modules()
    module_manager = ModuleManager.get_instance()
    info = db.get("core.updater", "restart_info")

    if info:
        try:
            await app.edit_message_text(
                info["chat_id"],
                info["message_id"],
                "<b>Loading modules...</b>",
            )
        except errors.RPCError:
            pass

    await module_manager.load_modules(app, loader=load_module)

    if info:
        text = {
            "restart": "<b>Restart completed!</b>",
            "update": "<b>Update process completed!</b>",
        }[info["type"]]

        if module_manager.failed_modules > 0:
            failed_list = "\n".join(
                [f"• <code>{m}</code>" for m in module_manager.failed_list]
            )
            text += (
                f"\n\n[E] <b>Failed to load {module_manager.failed_modules} module(s):</b>\n"
                f"{failed_list}\n\n"
                "<i>Please check logs for more details.</i>"
            )
        try:
            await app.edit_message_text(info["chat_id"], info["message_id"], text)
        except errors.RPCError:
            pass
        db.remove("core.updater", "restart_info")

    # required for sessionkiller module
    if db.get("core.sessionkiller", "enabled", False):
        db.set(
            "core.sessionkiller",
            "auths_hashes",
            [
                auth.hash
                for auth in (await app.invoke(GetAuthorizations())).authorizations
            ],
        )

    logging.info("Moon-Userbot started!")

    cleanup_task = app.loop.create_task(rentry_cleanup_job())
    server = AsyncWSGIRefServer(host="0.0.0.0", port=config.port)
    webui_task = asyncio.create_task(asyncio.to_thread(server.run, bottle_app))

    try:
        await idle()
    finally:
        logging.info("Shutting down... cancelling background tasks.")
        cleanup_task.cancel()
        server.shutdown()

        try:
            await asyncio.gather(cleanup_task, webui_task, return_exceptions=True)
        except asyncio.CancelledError:
            logging.info("Task rentry_cleanup or webui_task cancelled")
        except Exception as e:
            logging.error(f"Error cancelling task rentry_cleanup or webui_task: {e}")

        gitrepo.close()
        await app.stop()


if __name__ == "__main__":
    app.run(main())
