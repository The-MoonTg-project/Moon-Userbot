import logging
from pathlib import Path
from typing import Optional

from pyrogram import Client

from utils.scripts import load_module
from utils.misc import modules_help


class ModuleManager:
    _instance: Optional["ModuleManager"] = None

    def __init__(self):
        self.success_modules = 0
        self.failed_modules = 0
        self.failed_list = []
        self.help_navigator = None

    @classmethod
    def get_instance(cls) -> "ModuleManager":
        if cls._instance is None:
            cls._instance = ModuleManager()
        return cls._instance

    async def load_modules(self, app: Client):
        """Load all modules and initialize help navigator"""
        for path in Path("modules").rglob("*.py"):
            try:
                await load_module(
                    path.stem, app, core="custom_modules" not in path.parent.parts
                )
            except Exception:
                logging.warning("Can't import module %s", path.stem, exc_info=True)
                self.failed_modules += 1
                self.failed_list.append(path.stem)
            else:
                self.success_modules += 1

        logging.info("Imported %d modules", self.success_modules)
        if self.failed_modules:
            logging.warning("Failed to import %d modules", self.failed_modules)

        self.help_navigator = HelpNavigator()
        return self.help_navigator


class HelpNavigator:
    def __init__(self):
        self.current_page = 1
        self.module_list = list(modules_help.keys())
        self.total_pages = (len(modules_help) + 9) // 10
        logging.info("Initialized HelpNavigator with %d modules", len(self.module_list))

    async def send_page(self, message):
        from utils.misc import prefix

        start_index = (self.current_page - 1) * 10
        end_index = start_index + 10
        page_modules = self.module_list[start_index:end_index]
        text = "<b>Help for <a href=https://t.me/Moonub_chat>Moon-Userbot</a></b>\n"
        text += f"For more help on how to use a command, type <code>{prefix}help [module]</code>\n\n"
        text += f"Help Page No: {self.current_page}/{self.total_pages}\n\n"
        for module_name in page_modules:
            commands = modules_help[module_name]
            text += f"<b>• {module_name.title()}:</b> {', '.join([f'<code>{prefix + cmd_name.split()[0]}</code>' for cmd_name in commands.keys()])}\n"
        text += f"\n<b>The number of modules in the userbot: {len(modules_help)}</b>"
        await message.edit(text, disable_web_page_preview=True)

    def next_page(self) -> bool:
        if self.current_page < self.total_pages:
            self.current_page += 1
            return True
        return False

    def prev_page(self) -> bool:
        if self.current_page > 1:
            self.current_page -= 1
            return True
        return False
