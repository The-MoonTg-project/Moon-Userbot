import os
import yara
import time
import apkid as ap
from apkid.apkid import Options, Scanner, OutputFormatter, RulesManager

from pyrogram import Client, filters, enums
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import progress


class CustomOutputFormatter(OutputFormatter):
    def init(self, *args, **kwargs):
        super().init(*args, **kwargs)

    def write(self, results):
        if self.json:
            return self._build_json_output(results)
        else:
            return self._build_console_output(results)

    def _build_console_output(self, results):
        output = ""
        for key, raw_matches in results.items():
            match_results = self._build_match_results(raw_matches)
            if len(match_results) == 0:
                continue
            output += f"ᴛᴀʀɢᴇᴛ: {key}\n"
            for tags in sorted(match_results):
                descriptions = ', '.join(sorted(match_results[tags]))
                if self.include_types:
                    tags_str = self._colorize_tags(tags)
                else:
                    tags_str = tags
                output += f" |-> {tags_str} : {descriptions}\n\n"
        return output


@Client.on_message(filters.command("apkid", prefix) & filters.me)
async def apkid(_, message: Message):
    if not message.reply_to_message:
        return await message.edit("Kindly reply to a file")
    await message.edit("Please wait...")
    if message.reply_to_message:
        text = "Downloading..."
        await message.edit(text)
        apk = await message.reply_to_message.download(progress=progress, progress_args=(message, time.time(), text))
        text += "\nFile Downloaded."
        text += "\nScanning File..."
        await message.edit(text)
        rules_file_path = os.path.join(os.path.dirname(ap.file), "rules", "rules.yarc")
        rules = yara.load(filepath=rules_file_path)
        options = Options()
        result = Scanner(rules=rules, options=options).scan_file(apk)
        formatter = CustomOutputFormatter(json_output=False, output_dir=None, rules_manager=RulesManager(), include_types=False)
        output = formatter.write(result)
        if output == "":
            output = "No results found."
        if os.path.exists(apk):
            os.remove(apk)
        return await message.edit(output, parse_mode=enums.ParseMode.MARKDOWN)

    if os.path.exists(apk):
        os.remove(apk)
    return await message.edit("Please reply to a file!")

modules_help["apkid"] = {"apkid": "apkid scanner"}
