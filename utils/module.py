import logging
from difflib import SequenceMatcher
from pathlib import Path
from typing import Callable, Optional

from pyrogram import Client

from utils import modules_help


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

    async def load_modules(self, app: Client, loader: Callable):
        """Load all modules and initialize help navigator"""
        for path in Path("modules").rglob("*.py"):
            try:
                await loader(
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

    def refresh(self):
        self.module_list = list(modules_help.keys())
        self.total_pages = (len(modules_help) + 9) // 10
        if self.current_page > self.total_pages:
            self.current_page = max(1, self.total_pages)
        logging.info(
            "Refreshed HelpNavigator: %d modules, %d pages",
            len(self.module_list),
            self.total_pages,
        )

    async def send_page(self, message):
        from utils import prefix

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

    @staticmethod
    def fuzzy_search(query: str, fuzzy_threshold: float = 0.7) -> list:
        """Search modules and commands using substring + fuzzy matching.

        Returns a list of (match_type, name, module_name, score) tuples
        sorted by relevance. match_type is 'module' or 'command'.

        Substring matches (query is part of the name) are always included.
        Fuzzy matches (for typos) only appear if similarity >= fuzzy_threshold.
        """
        query = query.lower()
        results = []

        for module_name, commands in modules_help.items():
            mod_lower = module_name.lower()
            if query in mod_lower:
                score = 0.8 + (len(query) / len(mod_lower)) * 0.2
                results.append(("module", module_name, module_name, score))
            else:
                score = SequenceMatcher(None, query, mod_lower).ratio()
                if score >= fuzzy_threshold:
                    results.append(("module", module_name, module_name, score))

            for cmd_key in commands:
                cmd_name = cmd_key.split()[0].lower()
                if query in cmd_name:
                    score = 0.8 + (len(query) / len(cmd_name)) * 0.2
                    results.append(("command", cmd_name, module_name, score))
                else:
                    score = SequenceMatcher(None, query, cmd_name).ratio()
                    if score >= fuzzy_threshold:
                        results.append(("command", cmd_name, module_name, score))

        # Sort by score descending, deduplicate
        results.sort(key=lambda x: x[3], reverse=True)
        seen = set()
        unique = []
        for r in results:
            key = (r[0], r[1])
            if key not in seen:
                seen.add(key)
                unique.append(r)
        return unique[:15]

    async def send_search_results(self, message, query: str):
        """Search and display fuzzy results."""
        from utils import prefix

        results = self.fuzzy_search(query)
        if not results:
            return None

        text = f"<b>Search results for</b> <code>{query}</code>:\n\n"
        for match_type, name, module_name, _score in results:
            if match_type == "module":
                cmds = modules_help[module_name]
                cmd_list = ", ".join(
                    f"<code>{prefix}{c.split()[0]}</code>" for c in cmds
                )
                text += f"<b>• {module_name}</b> (module): {cmd_list}\n"
            else:
                desc = ""
                for cmd_key, cmd_desc in modules_help[module_name].items():
                    if cmd_key.split()[0].lower() == name:
                        desc = cmd_desc
                        break
                text += (
                    f"  ◦ <code>{prefix}{name}</code>"
                    f" — <i>{desc}</i>"
                    f"  [<code>{module_name}</code>]\n"
                )

        text += f"\n<b>Tip:</b> <code>{prefix}help [name]</code> for full details"
        await message.edit(text, disable_web_page_preview=True)
        return True
