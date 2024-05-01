import datetime
import os
import subprocess
import time

import aiofiles
from pyrogram import Client, enums, filters
from pyrogram.errors import MessageTooLong
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import edit_or_reply, format_exc, progress


async def read_file(file_path):
    async with aiofiles.open(file_path, mode="r") as file:
        content = await file.read()
    return content


def check_extension(file_path):
    if file_path.lower().endswith(".txt"):
        code_start = "```txt"
    elif file_path.lower().endswith(".py"):
        code_start = "```py"
    elif file_path.lower().endswith(".js"):
        code_start = "```js"
    elif file_path.lower().endswith(".json"):
        code_start = "```json"
    elif file_path.lower().endswith(".smali"):
        code_start = "```smali"
    elif file_path.lower().endswith(".sh"):
        code_start = "```bash"
    elif file_path.lower().endswith(".c"):
        code_start = "```C"
    elif file_path.lower().endswith(".java"):
        code_start = "```java"
    elif file_path.lower().endswith(".php"):
        code_start = "```php"
    elif file_path.lower().endswith(".doc"):
        code_start = "```doc"
    elif file_path.lower().endswith(".docx"):
        code_start = "```docx"
    elif file_path.lower().endswith(".rtf"):
        code_start = "```rtf"
    elif file_path.lower().endswith(".s"):
        code_start = "```asm"
    elif file_path.lower().endswith(".dart"):
        code_start = "```dart"
    elif file_path.lower().endswith(".cfg"):
        code_start = "```cfg"
    elif file_path.lower().endswith(".swift"):
        code_start = "```swift"
    elif file_path.lower().endswith(".cs"):
        code_start = "```C#"
    elif file_path.lower().endswith(".vb"):
        code_start = "```vb"
    elif file_path.lower().endswith(".css"):
        code_start = "```css"
    elif file_path.lower().endswith(".htm") or file_path.lower().endswith(".html"):
        code_start = "```html"
    elif file_path.lower().endswith(".rss"):
        code_start = "```rss"
    elif file_path.lower().endswith(".swift"):
        code_start = "```swift"
    elif file_path.lower().endswith(".xhtml"):
        code_start = "```xhtml"
    elif file_path.lower().endswith(".cpp"):
        code_start = "```cpp"
    else:
        code_start = "```"

    return code_start


@Client.on_message(filters.command("open", prefix) & filters.me)
async def openfile(client: Client, message: Message):
    if not message.reply_to_message:
        return await message.edit_text("Kindly Reply to a File")

    try:
        ms = await edit_or_reply(message, "`Downloading...")
        ct = time.time()
        file_path = await message.reply_to_message.download(
            progress=progress, progress_args=(ms, ct, "Downloading...")
        )
        await ms.edit_text("<code>Trying to open file...</code>")
        file_info = os.stat(file_path)
        file_name = file_path.split("/")[-1:]
        file_size = file_info.st_size
        last_modified = datetime.datetime.fromtimestamp(file_info.st_mtime).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        code_start = check_extension(file_path=file_path)
        code_end = "```"
        content = await read_file(file_path=file_path)
        await ms.edit_text(
            f"**File Name:** `{file_name[0]}`\n**Size:** `{file_size} bytes`\n**Last Modified:** `{last_modified}`\n**Content:** {code_start}\n{content}{code_end}",
            parse_mode=enums.ParseMode.MARKDOWN,
        )

    except MessageTooLong:
        await ms.edit_text(
            "<code>File Content is too long... Pasting to rentry...</code>"
        )
        content_new = f"{code_start}\n{content}{code_end}"
        paste = subprocess.run(
            ["rentry", "new", content_new], capture_output=True, text=True
        )
        await client.send_message("me", paste.stdout, disable_web_page_preview=True)
        lines = paste.stdout.split("\n")
        for line in lines:
            parts = line.split()
            if parts[0].strip() == "Url:":
                url = "".join(parts[1:]).split()[0]
                await ms.edit_text(
                    f"**File Name:** `{file_name[0]}`\n**Size:** `{file_size} bytes`\n**Last Modified:** `{last_modified}`\n**Content:** {url}\n**Note:** `Edit Code has been sent to your saved messages`",
                    parse_mode=enums.ParseMode.MARKDOWN,
                    disable_web_page_preview=True,
                )
                break

    except Exception as e:
        await ms.edit_text(format_exc(e))

    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


modules_help["open"] = {
    "open": "Open content of any text supported filetype and show it's raw data"
}
