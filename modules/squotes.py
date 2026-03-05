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

import base64
from io import BytesIO

import requests
from pyrogram import Client, errors, filters, types
from pyrogram.types import Message

from utils import modules_help, prefix
from utils.config import quotes_api as QUOTES_API
from utils.scripts import format_exc, resize_image, with_reply

FLAGS = {"!png", "!file", "!me", "!ls", "!noreply", "!nr"}


async def _generate_and_send_quote(
    client: Client, message, params: dict, is_png: bool, send_for_me: bool
):
    response = requests.post(QUOTES_API, json=params)
    if not response.ok:
        return await message.edit(
            f"<b>Quotes API error!</b>\n<code>{response.text}</code>"
        )

    resized = resize_image(
        BytesIO(response.content), img_type="PNG" if is_png else "WEBP"
    )
    await message.edit("<b>Sending...</b>")

    try:
        func = client.send_document if is_png else client.send_sticker
        chat_id = "me" if send_for_me else message.chat.id
        await func(chat_id, resized)
    except errors.RPCError as e:
        await message.edit(format_exc(e))
    else:
        await message.delete()


@Client.on_message(filters.command(["q", "quote"], prefix) & filters.me)
@with_reply
async def quote_cmd(client: Client, message: Message):
    if len(message.command) > 1 and message.command[1].isdigit():
        count = max(1, min(int(message.command[1]), 15))
    else:
        count = 1

    is_png = "!png" in message.command or "!file" in message.command
    send_for_me = "!me" in message.command or "!ls" in message.command
    no_reply = "!noreply" in message.command or "!nr" in message.command

    reply_id = message.reply_to_message.id
    msg_ids = list(range(reply_id, reply_id + count))

    messages = await client.get_messages(message.chat.id, msg_ids)
    if not isinstance(messages, list):
        messages = [messages]
    messages = [msg for msg in messages if not msg.empty]  # type: ignore

    if no_reply:
        for msg in messages:
            msg.reply_to_message = None  # type: ignore

    if send_for_me:
        await message.delete()
        message = await client.send_message("me", "<b>Generating...</b>")
    else:
        await message.edit("<b>Generating...</b>")

    params = {
        "messages": [
            await render_message(client, msg)  # type: ignore
            for msg in messages
            if not msg.empty  # type: ignore
        ],
        "quote_color": "#162330",
        "text_color": "#fff",
    }
    await _generate_and_send_quote(client, message, params, is_png, send_for_me)


@Client.on_message(filters.command(["fq", "fakequote"], prefix) & filters.me)
@with_reply
async def fake_quote_cmd(client: Client, message: types.Message):
    is_png = "!png" in message.command or "!file" in message.command
    send_for_me = "!me" in message.command or "!ls" in message.command
    no_reply = "!noreply" in message.command or "!nr" in message.command

    fake_quote_text = " ".join(arg for arg in message.command[1:] if arg not in FLAGS)

    if not fake_quote_text:
        return await message.edit("<b>Fake quote text is empty</b>")

    q_message = await client.get_messages(message.chat.id, message.reply_to_message.id)
    q_message.text = fake_quote_text  # type: ignore
    q_message.entities = None  # type: ignore
    if no_reply:
        q_message.reply_to_message = None  # type: ignore

    if send_for_me:
        await message.delete()
        message = await client.send_message("me", "<b>Generating...</b>")
    else:
        await message.edit("<b>Generating...</b>")

    params = {
        "messages": [await render_message(client, q_message)],  # type: ignore
        "quote_color": "#162330",
        "text_color": "#fff",
    }
    await _generate_and_send_quote(client, message, params, is_png, send_for_me)


files_cache = {}


async def _get_cached_file(app: Client, file_id: str) -> str:
    if file_id in files_cache:
        return files_cache[file_id]

    content = await app.download_media(file_id, in_memory=True)
    data = base64.b64encode(bytes(content.getbuffer())).decode()  # type: ignore
    files_cache[file_id] = data
    return data


def _apply_forward_origin(msg: types.Message):
    if not msg.forward_origin:
        return
    if isinstance(msg.forward_origin, types.MessageOriginUser):
        msg.from_user = msg.forward_origin.sender_user
    elif isinstance(msg.forward_origin, types.MessageOriginHiddenUser):
        msg.from_user.id = 0
        msg.from_user.first_name = msg.forward_origin.sender_user_name
        msg.from_user.last_name = ""
    elif isinstance(msg.forward_origin, types.MessageOriginChat):
        msg.sender_chat = msg.forward_origin.sender_chat
        msg.from_user.id = 0
        if msg.forward_origin.author_signature:
            msg.author_signature = msg.forward_origin.author_signature


async def _build_author(app: Client, message: types.Message) -> dict:
    author = {}
    if message.from_user and message.from_user.id != 0:
        from_user = message.from_user

        author["id"] = from_user.id
        author["name"] = get_full_name(from_user)

        if message.author_signature:
            author["rank"] = message.author_signature
        elif message.chat.type != "supergroup" or message.forward_date:
            author["rank"] = ""
        else:
            try:
                member = await message.chat.get_member(from_user.id)
            except errors.UserNotParticipant:
                author["rank"] = ""
            else:
                author["rank"] = getattr(member, "title", "") or (
                    "owner"
                    if member.status == "creator"
                    else "admin"
                    if member.status == "administrator"
                    else ""
                )

        if from_user.photo:
            author["avatar"] = await _get_cached_file(app, from_user.photo.big_file_id)
        elif from_user.username:
            # may be user blocked us, we will try to get avatar via t.me
            t_me_page = requests.get(f"https://t.me/{from_user.username}").text
            sub = '<meta property="og:image" content='
            index = t_me_page.find(sub)
            if index != -1:
                link = t_me_page[index + 35 :].split('"')
                if (
                    len(link) > 0
                    and link[0]
                    and link[0] != "https://telegram.org/img/t_logo.png"
                ):
                    # found valid link
                    avatar = requests.get(link[0]).content
                    author["avatar"] = base64.b64encode(avatar).decode()
                else:
                    author["avatar"] = ""
            else:
                author["avatar"] = ""
        else:
            author["avatar"] = ""
    elif message.from_user and message.from_user.id == 0:
        author["id"] = 0
        author["name"] = message.from_user.first_name
        author["rank"] = ""
    else:
        author["id"] = message.sender_chat.id
        author["name"] = message.sender_chat.title
        author["rank"] = "channel" if message.sender_chat.type == "channel" else ""

        if message.sender_chat.photo:
            author["avatar"] = await _get_cached_file(
                app, message.sender_chat.photo.big_file_id
            )
        else:
            author["avatar"] = ""
    author["via_bot"] = message.via_bot.username if message.via_bot else ""
    return author


async def render_message(app: Client, message: types.Message) -> dict:
    _apply_forward_origin(message)

    # text
    if message.photo:
        text = message.caption if message.caption else ""
    elif message.poll:
        text = get_poll_text(message.poll)
    elif message.sticker:
        text = ""
    else:
        text = get_reply_text(message)

    # media
    if message.photo:
        media = await _get_cached_file(app, message.photo.file_id)
    elif message.sticker:
        media = await _get_cached_file(app, message.sticker.file_id)
    else:
        media = ""

    # entities
    entities = []
    if message.entities:
        for entity in message.entities:
            entities.append(
                {
                    "offset": entity.offset,
                    "length": entity.length,
                    "type": str(entity.type).split(".")[-1].lower(),
                }
            )

    # reply
    reply = {}
    reply_msg = message.reply_to_message
    if reply_msg and not reply_msg.empty:
        _apply_forward_origin(reply_msg)

        if reply_msg.from_user:
            reply["id"] = reply_msg.from_user.id
            reply["name"] = get_full_name(reply_msg.from_user)
        else:
            reply["id"] = reply_msg.sender_chat.id
            reply["name"] = reply_msg.sender_chat.title

        reply["text"] = get_reply_text(reply_msg)

    return {
        "text": text,
        "media": media,
        "entities": entities,
        "author": await _build_author(app, message),
        "reply": reply,
    }


def get_audio_text(audio: types.Audio) -> str:
    if audio.title and audio.performer:
        return f" ({audio.title} — {audio.performer})"
    if audio.title:
        return f" ({audio.title})"
    if audio.performer:
        return f" ({audio.performer})"
    return ""


def get_reply_text(reply: types.Message) -> str:
    if reply.photo:
        return "📷 Photo" + ("\n" + reply.caption if reply.caption else "")
    if reply.poll:
        return get_reply_poll_text(reply.poll)
    if reply.location or reply.venue:
        return "📍 Location"
    if reply.contact:
        return "👤 Contact"
    if reply.animation:
        return "🖼 GIF"
    if reply.audio:
        return "🎧 Music" + get_audio_text(reply.audio)
    if reply.video:
        return "📹 Video"
    if reply.video_note:
        return "📹 Videomessage"
    if reply.voice:
        return "🎵 Voice"
    if reply.sticker:
        sprefix = reply.sticker.emoji + " " if reply.sticker.emoji else ""
        return sprefix + "Sticker"
    if reply.document:
        return "💾 File " + reply.document.file_name
    if reply.game:
        return "🎮 Game"
    if reply.game_high_score:
        return "🎮 set new record"
    if reply.dice:
        return f"{reply.dice.emoji} - {reply.dice.value}"
    if reply.new_chat_members:
        if reply.new_chat_members[0].id == reply.from_user.id:
            return "👤 joined the group"
        return f"👤 invited {get_full_name(reply.new_chat_members[0])} to the group"
    if reply.left_chat_member:
        if reply.left_chat_member.id == reply.from_user.id:
            return "👤 left the group"
        return f"👤 removed {get_full_name(reply.left_chat_member)}"
    if reply.new_chat_title:
        return f"✏ changed group name to {reply.new_chat_title}"
    if reply.new_chat_photo:
        return "🖼 changed group photo"
    if reply.delete_chat_photo:
        return "🖼 removed group photo"
    if reply.pinned_message:
        return "📍 pinned message"
    if reply.video_chat_started:
        return "🎤 started a new video chat"
    if reply.video_chat_ended:
        return "🎤 ended the video chat"
    if reply.video_chat_members_invited:
        return "🎤 invited participants to the video chat"
    if reply.group_chat_created or reply.supergroup_chat_created:
        return "👥 created the group"
    if reply.channel_chat_created:
        return "👥 created the channel"
    return reply.text or "unsupported message"


def get_poll_text(poll: types.Poll) -> str:
    text = get_reply_poll_text(poll) + "\n"

    text += poll.question + "\n"
    for option in poll.options:
        text += f"- {option.text}"
        if option.voter_count > 0:
            text += f" ({option.voter_count} voted)"
        text += "\n"

    text += f"Total: {poll.total_voter_count} voted"

    return text


def get_reply_poll_text(poll: types.Poll) -> str:
    if poll.is_anonymous:
        text = "📊 Anonymous poll" if poll.type == "regular" else "📊 Anonymous quiz"
    else:
        text = "📊 Poll" if poll.type == "regular" else "📊 Quiz"
    if poll.is_closed:
        text += " (closed)"

    return text


def get_full_name(user: types.User) -> str:
    name = user.first_name
    if user.last_name:
        name += " " + user.last_name
    return name


modules_help["squotes"] = {
    "q [reply]* [count 1-15] [!png] [!me] [!noreply]": "Generate a quote\n"
    "Available options: !png — send as PNG, !me — send quote to"
    "saved messages, !noreply — generate quote without reply",
    "fq [reply]* [!png] [!me] [!noreply] [text]*": "Generate a fake quote",
}
