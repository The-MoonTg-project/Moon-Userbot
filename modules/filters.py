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
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from pyrogram import Client, ContinuePropagation
from pyrogram import enums as enums
from pyrogram import errors, filters
from pyrogram.types import (
    InputMediaAudio,
    InputMediaDocument,
    InputMediaPhoto,
    InputMediaVideo,
    Message,
)

# noinspection PyUnresolvedReferences
from utils.db import db

# noinspection PyUnresolvedReferences
from utils.misc import modules_help, prefix
from utils.scripts import format_exc


def get_filters_chat(chat_id):
    return db.get("core.filters", f"{chat_id}", {})


def set_filters_chat(chat_id, filters_):
    return db.set("core.filters", f"{chat_id}", filters_)


async def contains_filter(_, __, m):
    return m.text and m.text.lower() in get_filters_chat(m.chat.id).keys()


contains = filters.create(contains_filter)


# noinspection PyTypeChecker
@Client.on_message(contains)
async def filters_main_handler(client: Client, message: Message):
    value = get_filters_chat(message.chat.id)[message.text.lower()]
    try:
        await client.get_messages(int(value["CHAT_ID"]), int(value["MESSAGE_ID"]))
    except errors.RPCError:
        raise ContinuePropagation

    if value.get("MEDIA_GROUP"):
        messages_grouped = await client.get_media_group(
            int(value["CHAT_ID"]), int(value["MESSAGE_ID"])
        )
        media_grouped_list = []
        for _ in messages_grouped:
            if _.photo:
                if _.caption:
                    media_grouped_list.append(
                        InputMediaPhoto(_.photo.file_id, _.caption.markdown)
                    )
                else:
                    media_grouped_list.append(InputMediaPhoto(_.photo.file_id))
            elif _.video:
                if _.caption:
                    if _.video.thumbs:
                        media_grouped_list.append(
                            InputMediaVideo(
                                _.video.file_id,
                                _.video.thumbs[0].file_id,
                                _.caption.markdown,
                            )
                        )
                    else:
                        media_grouped_list.append(
                            InputMediaVideo(_.video.file_id, _.caption.markdown)
                        )
                elif _.video.thumbs:
                    media_grouped_list.append(
                        InputMediaVideo(_.video.file_id, _.video.thumbs[0].file_id)
                    )
                else:
                    media_grouped_list.append(InputMediaVideo(_.video.file_id))
            elif _.audio:
                if _.caption:
                    media_grouped_list.append(
                        InputMediaAudio(_.audio.file_id, _.caption.markdown)
                    )
                else:
                    media_grouped_list.append(InputMediaAudio(_.audio.file_id))
            elif _.document:
                if _.caption:
                    if _.document.thumbs:
                        media_grouped_list.append(
                            InputMediaDocument(
                                _.document.file_id,
                                _.document.thumbs[0].file_id,
                                _.caption.markdown,
                            )
                        )
                    else:
                        media_grouped_list.append(
                            InputMediaDocument(_.document.file_id, _.caption.markdown)
                        )
                elif _.document.thumbs:
                    media_grouped_list.append(
                        InputMediaDocument(
                            _.document.file_id, _.document.thumbs[0].file_id
                        )
                    )
                else:
                    media_grouped_list.append(InputMediaDocument(_.document.file_id))
        await client.send_media_group(
            message.chat.id,
            media_grouped_list,
            reply_to_message_id=message.message_id,
        )
    else:
        await client.copy_message(
            message.chat.id,
            int(value["CHAT_ID"]),
            int(value["MESSAGE_ID"]),
            reply_to_message_id=message.message_id,
        )
    raise ContinuePropagation


@Client.on_message(filters.command(["filter"], prefix) & filters.me)
async def filter_handler(client: Client, message: Message):
    try:
        if len(message.text.split()) < 2:
            return await message.edit(
                f"<b>Usage</b>: <code>{prefix}filter [name] (Reply required)</code>",
                parse_mode=enums.ParseMode.HTML,
            )
        name = message.text.split(maxsplit=1)[1].lower()
        chat_filters = get_filters_chat(message.chat.id)
        if name in chat_filters.keys():
            return await message.edit(
                f"<b>Filter</b> <code>{name}</code> already exists.",
                parse_mode=enums.ParseMode.HTML,
            )
        if not message.reply_to_message:
            return await message.edit(
                "<b>Reply to message</b> please.", parse_mode=enums.ParseMode.HTML
            )

        try:
            chat = await client.get_chat(db.get("core.notes", "chat_id", 0))
        except (errors.RPCError, ValueError, KeyError):
            # group is not accessible or isn't created
            chat = await client.create_supergroup(
                "Moon_Userbot_Notes_Filters", "Don't touch this group, please"
            )
            db.set("core.notes", "chat_id", chat.id)

        chat_id = chat.id

        if message.reply_to_message.media_group_id:
            get_media_group = [
                _.message_id
                for _ in await client.get_media_group(
                    message.chat.id, message.reply_to_message.message_id
                )
            ]
            try:
                message_id = await client.forward_messages(
                    chat_id, message.chat.id, get_media_group
                )
            except errors.ChatForwardsRestricted:
                await message.edit(
                    "<b>Forwarding messages is restricted by chat admins</b>",
                    parse_mode=enums.ParseMode.HTML,
                )
                return
            filter_ = {
                "MESSAGE_ID": str(message_id[1].message_id),
                "MEDIA_GROUP": True,
                "CHAT_ID": str(chat_id),
            }
        else:
            try:
                message_id = await message.reply_to_message.forward(chat_id)
            except errors.ChatForwardsRestricted:
                if message.reply_to_message.text:
                    # manual copy
                    message_id = await client.send_message(
                        chat_id,
                        message.reply_to_message.text,
                        parse_mode=enums.ParseMode.HTML,
                    )
                else:
                    await message.edit(
                        "<b>Forwarding messages is restricted by chat admins</b>",
                        parse_mode=enums.ParseMode.HTML,
                    )
                    return
            filter_ = {
                "MEDIA_GROUP": False,
                "MESSAGE_ID": str(message_id.message_id),
                "CHAT_ID": str(chat_id),
            }

        chat_filters.update({name: filter_})

        set_filters_chat(message.chat.id, chat_filters)
        return await message.edit(
            f"<b>Filter</b> <code>{name}</code> has been added.",
            parse_mode=enums.ParseMode.HTML,
        )
    except Exception as e:
        return await message.edit(format_exc(e), parse_mode=enums.ParseMode.HTML)


@Client.on_message(filters.command(["filters"], prefix) & filters.me)
async def filters_handler(client: Client, message: Message):
    try:
        text = ""
        for index, a in enumerate(get_filters_chat(message.chat.id).items(), start=1):
            key, item = a
            key = key.replace("<", "").replace(">", "")
            text += f"{index}. <code>{key}</code>\n"
        text = f"<b>Your filters in current chat</b>:\n\n" f"{text}"
        text = text[:4096]
        return await message.edit(text, parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        return await message.edit(format_exc(e))


@Client.on_message(
    filters.command(["delfilter", "filterdel", "fdel"], prefix) & filters.me
)
async def filter_del_handler(client: Client, message: Message):
    try:
        if len(message.text.split()) < 2:
            return await message.edit(
                f"<b>Usage</b>: <code>{prefix}fdel [name]</code>",
                parse_mode=enums.ParseMode.HTML,
            )
        name = message.text.split(maxsplit=1)[1].lower()
        chat_filters = get_filters_chat(message.chat.id)
        if name not in chat_filters.keys():
            return await message.edit(
                f"<b>Filter</b> <code>{name}</code> doesn't exists.",
                parse_mode=enums.ParseMode.HTML,
            )
        del chat_filters[name]
        set_filters_chat(message.chat.id, chat_filters)
        return await message.edit(
            f"<b>Filter</b> <code>{name}</code> has been deleted.",
            parse_mode=enums.ParseMode.HTML,
        )
    except Exception as e:
        return await message.edit(format_exc(e))


@Client.on_message(filters.command(["fsearch"], prefix) & filters.me)
async def filter_search_handler(client: Client, message: Message):
    try:
        if len(message.text.split()) < 2:
            return await message.edit(
                f"<b>Usage</b>: <code>{prefix}fsearch [name]</code>",
                parse_mode=enums.ParseMode.HTML,
            )
        name = message.text.split(maxsplit=1)[1].lower()
        chat_filters = get_filters_chat(message.chat.id)
        if name not in chat_filters.keys():
            return await message.edit(
                f"<b>Filter</b> <code>{name}</code> doesn't exists.",
                parse_mode=enums.ParseMode.HTML,
            )
        return await message.edit(
            f"<b>Trigger</b>:\n<code>{name}</code"
            f">\n<b>Answer</b>:\n{chat_filters[name]}",
            parse_mode=enums.ParseMode.HTML,
        )
    except Exception as e:
        return await message.edit(format_exc(e))


modules_help["filters"] = {
    "filter [name]": "Create filter (Reply required)",
    "filters": "List of all triggers",
    "fdel [name]": "Delete filter by name",
    "fsearch [name]": "Info filter by name",
}
