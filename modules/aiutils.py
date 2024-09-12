import os

import aiohttp
from pyrogram import Client, filters
from pyrogram.errors import MessageTooLong
from pyrogram.types import Message

from utils.config import vca_api_key
from utils.misc import modules_help, prefix
from utils.scripts import format_exc

api_url = "https://visioncraft.top/api"


async def fetch_models(category: str):
    """Get all available SDXL models"""
    async with aiohttp.ClientSession() as session, session.get(
        f"https://visioncraft.top/api/image/models/{category}"
    ) as response:
        return await response.json()


async def generate_video(api_url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{api_url}/image/generate", json=data) as response:
            result = await response.json()
            image_url = result["image_url"]
            return image_url


async def generate_images(data):
    async with aiohttp.ClientSession() as session, session.post(
        f"{api_url}/image/generate", json=data
    ) as response:
        result = await response.json()
        return result


async def download_image(session, image_url, filename):
    """Get The Image Data From Response"""
    async with session.get(image_url) as response:
        image_data = await response.read()
        with open(filename, "wb") as f:
            f.write(image_data)


@Client.on_message(filters.command("vdxl", prefix) & filters.me)
async def vdxl(c: Client, message: Message):
    """Text to Image Generation Using SDXL"""

    await message.edit_text("<code>Please Wait...</code>")

    try:
        chat_id = message.chat.id
        model_category = "SDXL-1.0"
        models = await fetch_models(category=model_category)

        if not message.reply_to_message and len(message.command) > 2:
            model_found = False
            for m in models:
                if message.text.startswith(f"{prefix}vdxl {m}"):
                    model = m
                    prompt = message.text[len(f"{prefix}vdxl {m}") :].strip()
                    model_found = True
                    break
            if not model_found:
                return await message.edit_text(
                    f"<b>Usage: </b><code>{prefix}vdxl [model]* [prompt/reply to prompt]*</code>\n <b>Available Models:</b> <blockquote>{models}</blockquote>"
                )
        elif message.reply_to_message and len(message.command) > 1:
            model = message.text.split(maxsplit=1)[1]
            print(model)
            if model in models:
                prompt = message.reply_to_message.text
            else:
                return await message.edit_text(
                    f"<b>Usage: </b><code>{prefix}vdxl [model]* [prompt/reply to prompt]*</code>\n <b>Available Models:</b> <blockquote>{models}</blockquote>"
                )
        else:
            return await message.edit_text(
                f"<b>Usage: </b><code>{prefix}vdxl [model]* [prompt/reply to prompt]*</code>\n <b>Available Models:</b> <blockquote>{models}</blockquote>"
            )

        data = {
            "model": model,
            "prompt": prompt,
            "negative_prompt": "bad quality",
            "token": vca_api_key,
            "sampler": "Euler",
            "steps": 30,
            "width": 1024,
            "height": 1024,
            "cfg_scale": 7,
            "loras": {},
            "seed": -1,
            "stream": False,
        }

        response = await generate_images(data)
        try:
            image_url = response["image_url"]
            async with aiohttp.ClientSession() as session:
                filename = f"{chat_id}_{message.id}.png"
                await message.edit_text("<code>Downloading Image...</code>")
                await download_image(session, image_url, filename)
                await message.edit_text("<code>Uploading Image...</code>")
                await c.send_document(
                    chat_id,
                    filename,
                    caption=f"<b>Prompt: </b><code>{prompt}</code>\n<b>Model: </b><code>{model}</code>",
                )
                os.remove(filename)
                await message.delete()
        except KeyError:
            try:
                error = response["error"]
                mes = response["message"]
                return await message.edit_text(f"<b>{error}: </b><code>{mes}</code>")
            except KeyError:
                details = response["detail"]
                mes = response["message"]
                return await message.edit_text(f"<b>{details}: </b><code>{mes}</code>")

    except MessageTooLong:
        await message.edit_text(
            f"<b>Model List is too long</b> See the Full List <a href='https://visioncraft.top/api/image/models/{model_category}'> Here </a>"
        )
        return

    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")


@Client.on_message(filters.command("vdxl2", prefix) & filters.me)
async def vdxl2(c: Client, message: Message):
    """Text to Image Generation Using SDXL"""

    await message.edit_text("<code>Please Wait...</code>")

    try:
        chat_id = message.chat.id
        model_category = "SD-2.0"
        models = await fetch_models(category=model_category)

        if not message.reply_to_message and len(message.command) > 2:
            model_found = False
            for m in models:
                if message.text.startswith(f"{prefix}vdxl2 {m}"):
                    model = m
                    prompt = message.text[len(f"{prefix}vdxl2 {m}") :].strip()
                    model_found = True
                    break
            if not model_found:
                return await message.edit_text(
                    f"<b>Usage: </b><code>{prefix}vdxl2 [model]* [prompt/reply to prompt]*</code>\n <b>Available Models:</b> <blockquote>{models}</blockquote>"
                )
        elif message.reply_to_message and len(message.command) > 1:
            model = message.text.split(maxsplit=1)[1]
            print(model)
            if model in models:
                prompt = message.reply_to_message.text
            else:
                return await message.edit_text(
                    f"<b>Usage: </b><code>{prefix}vdxl2 [model]* [prompt/reply to prompt]*</code>\n <b>Available Models:</b> <blockquote>{models}</blockquote>"
                )
        else:
            return await message.edit_text(
                f"<b>Usage: </b><code>{prefix}vdxl2 [model]* [prompt/reply to prompt]*</code>\n <b>Available Models:</b> <blockquote>{models}</blockquote>"
            )

        data = {
            "model": model,
            "prompt": prompt,
            "negative_prompt": "bad quality",
            "token": vca_api_key,
            "sampler": "Euler",
            "steps": 30,
            "width": 1024,
            "height": 1024,
            "cfg_scale": 7,
            "loras": {},
            "seed": -1,
            "stream": False,
        }

        response = await generate_images(data)
        try:
            image_url = response["image_url"]
            async with aiohttp.ClientSession() as session:
                filename = f"{chat_id}_{message.id}.png"
                await message.edit_text("<code>Downloading Image...</code>")
                await download_image(session, image_url, filename)
                await message.edit_text("<code>Uploading Image...</code>")
                await c.send_document(
                    chat_id,
                    filename,
                    caption=f"<b>Prompt: </b><code>{prompt}</code>\n<b>Model: </b><code>{model}</code>",
                )
                os.remove(filename)
                await message.delete()
        except KeyError:
            try:
                error = response["error"]
                mes = response["message"]
                return await message.edit_text(f"<b>{error}: </b><code>{mes}</code>")
            except KeyError:
                details = response["detail"]
                mes = response["message"]
                return await message.edit_text(f"<b>{details}: </b><code>{mes}</code>")

    except MessageTooLong:
        await message.edit_text(
            f"<b>Model List is too long</b> See the Full List <a href='https://visioncraft.top/api/image/models/{model_category}'> Here </a>"
        )
        return

    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")


@Client.on_message(filters.command("vdxl3", prefix) & filters.me)
async def vdxl3(c: Client, message: Message):
    """Text to Image Generation Using SDXL"""

    await message.edit_text("<code>Please Wait...</code>")

    try:
        chat_id = message.chat.id
        model_category = "SD-3.0"
        models = await fetch_models(category=model_category)

        if not message.reply_to_message and len(message.command) > 2:
            model_found = False
            for m in models:
                if message.text.startswith(f"{prefix}vdxl3 {m}"):
                    model = m
                    prompt = message.text[len(f"{prefix}vdxl3 {m}") :].strip()
                    model_found = True
                    break
            if not model_found:
                return await message.edit_text(
                    f"<b>Usage: </b><code>{prefix}vdxl3 [model]* [prompt/reply to prompt]*</code>\n <b>Available Models:</b> <blockquote>{models}</blockquote>"
                )
        elif message.reply_to_message and len(message.command) > 1:
            model = message.text.split(maxsplit=1)[1]
            print(model)
            if model in models:
                prompt = message.reply_to_message.text
            else:
                return await message.edit_text(
                    f"<b>Usage: </b><code>{prefix}vdxl3 [model]* [prompt/reply to prompt]*</code>\n <b>Available Models:</b> <blockquote>{models}</blockquote>"
                )
        else:
            return await message.edit_text(
                f"<b>Usage: </b><code>{prefix}vdxl3 [model]* [prompt/reply to prompt]*</code>\n <b>Available Models:</b> <blockquote>{models}</blockquote>"
            )

        data = {
            "model": model,
            "prompt": prompt,
            "negative_prompt": "bad quality",
            "token": vca_api_key,
            "sampler": "Euler",
            "steps": 30,
            "width": 1024,
            "height": 1024,
            "cfg_scale": 7,
            "loras": {},
            "seed": -1,
            "stream": False,
        }

        response = await generate_images(data)
        try:
            image_url = response["image_url"]
            async with aiohttp.ClientSession() as session:
                filename = f"{chat_id}_{message.id}.png"
                await message.edit_text("<code>Downloading Image...</code>")
                await download_image(session, image_url, filename)
                await message.edit_text("<code>Uploading Image...</code>")
                await c.send_document(
                    chat_id,
                    filename,
                    caption=f"<b>Prompt: </b><code>{prompt}</code>\n<b>Model: </b><code>{model}</code>",
                )
                os.remove(filename)
                await message.delete()
        except KeyError:
            try:
                error = response["error"]
                mes = response["message"]
                return await message.edit_text(f"<b>{error}: </b><code>{mes}</code>")
            except KeyError:
                details = response["detail"]
                mes = response["message"]
                return await message.edit_text(f"<b>{details}: </b><code>{mes}</code>")

    except MessageTooLong:
        await message.edit_text(
            f"<b>Model List is too long</b> See the Full List <a href='https://visioncraft.top/api/image/models/{model_category}'> Here </a>"
        )
        return

    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")


@Client.on_message(filters.command("vfxl", prefix) & filters.me)
async def vfxl(c: Client, message: Message):
    """Text to Image Generation Using SDXL"""

    await message.edit_text("<code>Please Wait...</code>")

    try:
        chat_id = message.chat.id
        model_category = "FLUX.1"
        models = await fetch_models(category=model_category)

        if not message.reply_to_message and len(message.command) > 2:
            model_found = False
            for m in models:
                if message.text.startswith(f"{prefix}vfxl {m}"):
                    model = m
                    prompt = message.text[len(f"{prefix}vfxl {m}") :].strip()
                    model_found = True
                    break
            if not model_found:
                return await message.edit_text(
                    f"<b>Usage: </b><code>{prefix}vfxl [model]* [prompt/reply to prompt]*</code>\n <b>Available Models:</b> <blockquote>{models}</blockquote>"
                )
        elif message.reply_to_message and len(message.command) > 1:
            model = message.text.split(maxsplit=1)[1]
            print(model)
            if model in models:
                prompt = message.reply_to_message.text
            else:
                return await message.edit_text(
                    f"<b>Usage: </b><code>{prefix}vfxl [model]* [prompt/reply to prompt]*</code>\n <b>Available Models:</b> <blockquote>{models}</blockquote>"
                )
        else:
            return await message.edit_text(
                f"<b>Usage: </b><code>{prefix}vfxl [model]* [prompt/reply to prompt]*</code>\n <b>Available Models:</b> <blockquote>{models}</blockquote>"
            )

        data = {
            "model": model,
            "prompt": prompt,
            "negative_prompt": "bad quality",
            "token": vca_api_key,
            "sampler": "Euler",
            "steps": 30,
            "width": 1024,
            "height": 1024,
            "cfg_scale": 1,
            "loras": {},
            "seed": -1,
            "stream": False,
        }

        response = await generate_images(data)
        try:
            image_url = response["image_url"]
            async with aiohttp.ClientSession() as session:
                filename = f"{chat_id}_{message.id}.png"
                await message.edit_text("<code>Downloading Image...</code>")
                await download_image(session, image_url, filename)
                await message.edit_text("<code>Uploading Image...</code>")
                await c.send_document(
                    chat_id,
                    filename,
                    caption=f"<b>Prompt: </b><code>{prompt}</code>\n<b>Model: </b><code>{model}</code>",
                )
                os.remove(filename)
                await message.delete()
        except KeyError:
            try:
                error = response["error"]
                mes = response["message"]
                return await message.edit_text(f"<b>{error}: </b><code>{mes}</code>")
            except KeyError:
                details = response["detail"]
                mes = response["message"]
                return await message.edit_text(f"<b>{details}: </b><code>{mes}</code>")

    except MessageTooLong:
        await message.edit_text(
            f"<b>Model List is too long</b> See the Full List <a href='https://visioncraft.top/api/image/models/{model_category}'> Here </a>"
        )
        return

    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")


@Client.on_message(filters.command("vpxl", prefix) & filters.me)
async def vpxl(c: Client, message: Message):
    """Text to Image Generation Using SDXL"""

    await message.edit_text("<code>Please Wait...</code>")

    try:
        chat_id = message.chat.id
        model_category = "Playground-v2"
        models = await fetch_models(category=model_category)

        if not message.reply_to_message and len(message.command) > 2:
            model_found = False
            for m in models:
                if message.text.startswith(f"{prefix}vpxl {m}"):
                    model = m
                    prompt = message.text[len(f"{prefix}vpxl {m}") :].strip()
                    model_found = True
                    break
            if not model_found:
                return await message.edit_text(
                    f"<b>Usage: </b><code>{prefix}vpxl [model]* [prompt/reply to prompt]*</code>\n <b>Available Models:</b> <blockquote>{models}</blockquote>"
                )
        elif message.reply_to_message and len(message.command) > 1:
            model = message.text.split(maxsplit=1)[1]
            print(model)
            if model in models:
                prompt = message.reply_to_message.text
            else:
                return await message.edit_text(
                    f"<b>Usage: </b><code>{prefix}vpxl [model]* [prompt/reply to prompt]*</code>\n <b>Available Models:</b> <blockquote>{models}</blockquote>"
                )
        else:
            return await message.edit_text(
                f"<b>Usage: </b><code>{prefix}vpxl [model]* [prompt/reply to prompt]*</code>\n <b>Available Models:</b> <blockquote>{models}</blockquote>"
            )

        data = {
            "model": model,
            "prompt": prompt,
            "negative_prompt": "bad quality",
            "token": vca_api_key,
            "sampler": "Euler",
            "steps": 30,
            "width": 1024,
            "height": 1024,
            "cfg_scale": 7,
            "loras": {},
            "seed": -1,
            "stream": False,
        }

        response = await generate_images(data)
        try:
            image_url = response["image_url"]
            async with aiohttp.ClientSession() as session:
                filename = f"{chat_id}_{message.id}.png"
                await message.edit_text("<code>Downloading Image...</code>")
                await download_image(session, image_url, filename)
                await message.edit_text("<code>Uploading Image...</code>")
                await c.send_document(
                    chat_id,
                    filename,
                    caption=f"<b>Prompt: </b><code>{prompt}</code>\n<b>Model: </b><code>{model}</code>",
                )
                os.remove(filename)
                await message.delete()
        except KeyError:
            try:
                error = response["error"]
                mes = response["message"]
                return await message.edit_text(f"<b>{error}: </b><code>{mes}</code>")
            except KeyError:
                details = response["detail"]
                mes = response["message"]
                return await message.edit_text(f"<b>{details}: </b><code>{mes}</code>")

    except MessageTooLong:
        await message.edit_text(
            f"<b>Model List is too long</b> See the Full List <a href='https://visioncraft.top/api/image/models/{model_category}'> Here </a>"
        )
        return

    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")


@Client.on_message(filters.command("vpixl", prefix) & filters.me)
async def vpixl(c: Client, message: Message):
    """Text to Image Generation Using SDXL"""

    await message.edit_text("<code>Please Wait...</code>")

    try:
        chat_id = message.chat.id
        model_category = "PixArt"
        models = await fetch_models(category=model_category)

        if not message.reply_to_message and len(message.command) > 2:
            model_found = False
            for m in models:
                if message.text.startswith(f"{prefix}vpixl {m}"):
                    model = m
                    prompt = message.text[len(f"{prefix}vpixl {m}") :].strip()
                    model_found = True
                    break
            if not model_found:
                return await message.edit_text(
                    f"<b>Usage: </b><code>{prefix}vpixl [model]* [prompt/reply to prompt]*</code>\n <b>Available Models:</b> <blockquote>{models}</blockquote>"
                )
        elif message.reply_to_message and len(message.command) > 1:
            model = message.text.split(maxsplit=1)[1]
            print(model)
            if model in models:
                prompt = message.reply_to_message.text
            else:
                return await message.edit_text(
                    f"<b>Usage: </b><code>{prefix}vpixl [model]* [prompt/reply to prompt]*</code>\n <b>Available Models:</b> <blockquote>{models}</blockquote>"
                )
        else:
            return await message.edit_text(
                f"<b>Usage: </b><code>{prefix}vpixl [model]* [prompt/reply to prompt]*</code>\n <b>Available Models:</b> <blockquote>{models}</blockquote>"
            )

        data = {
            "model": model,
            "prompt": prompt,
            "negative_prompt": "bad quality",
            "token": vca_api_key,
            "sampler": "Euler",
            "steps": 30,
            "width": 1024,
            "height": 1024,
            "cfg_scale": 7,
            "loras": {},
            "seed": -1,
            "stream": False,
        }

        response = await generate_images(data)
        try:
            image_url = response["image_url"]
            async with aiohttp.ClientSession() as session:
                filename = f"{chat_id}_{message.id}.png"
                await message.edit_text("<code>Downloading Image...</code>")
                await download_image(session, image_url, filename)
                await message.edit_text("<code>Uploading Image...</code>")
                await c.send_document(
                    chat_id,
                    filename,
                    caption=f"<b>Prompt: </b><code>{prompt}</code>\n<b>Model: </b><code>{model}</code>",
                )
                os.remove(filename)
                await message.delete()
        except KeyError:
            try:
                error = response["error"]
                mes = response["message"]
                return await message.edit_text(f"<b>{error}: </b><code>{mes}</code>")
            except KeyError:
                details = response["detail"]
                mes = response["message"]
                return await message.edit_text(f"<b>{details}: </b><code>{mes}</code>")

    except MessageTooLong:
        await message.edit_text(
            f"<b>Model List is too long</b> See the Full List <a href='https://visioncraft.top/api/image/models/{model_category}'> Here </a>"
        )
        return

    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")


@Client.on_message(filters.command("vkxl", prefix) & filters.me)
async def vkxl(c: Client, message: Message):
    """Text to Image Generation Using SDXL"""

    await message.edit_text("<code>Please Wait...</code>")

    try:
        chat_id = message.chat.id
        model_category = "Kolors"
        models = await fetch_models(category=model_category)

        if not message.reply_to_message and len(message.command) > 2:
            model_found = False
            for m in models:
                if message.text.startswith(f"{prefix}vkxl {m}"):
                    model = m
                    prompt = message.text[len(f"{prefix}vkxl {m}") :].strip()
                    model_found = True
                    break
            if not model_found:
                return await message.edit_text(
                    f"<b>Usage: </b><code>{prefix}vkxl [model]* [prompt/reply to prompt]*</code>\n <b>Available Models:</b> <blockquote>{models}</blockquote>"
                )
        elif message.reply_to_message and len(message.command) > 1:
            model = message.text.split(maxsplit=1)[1]
            print(model)
            if model in models:
                prompt = message.reply_to_message.text
            else:
                return await message.edit_text(
                    f"<b>Usage: </b><code>{prefix}vkxl [model]* [prompt/reply to prompt]*</code>\n <b>Available Models:</b> <blockquote>{models}</blockquote>"
                )
        else:
            return await message.edit_text(
                f"<b>Usage: </b><code>{prefix}vkxl [model]* [prompt/reply to prompt]*</code>\n <b>Available Models:</b> <blockquote>{models}</blockquote>"
            )

        data = {
            "model": model,
            "prompt": prompt,
            "negative_prompt": "bad quality",
            "token": vca_api_key,
            "sampler": "Euler",
            "steps": 30,
            "width": 1024,
            "height": 1024,
            "cfg_scale": 7,
            "loras": {},
            "seed": -1,
            "stream": False,
        }

        response = await generate_images(data)
        try:
            image_url = response["image_url"]
            async with aiohttp.ClientSession() as session:
                filename = f"{chat_id}_{message.id}.png"
                await message.edit_text("<code>Downloading Image...</code>")
                await download_image(session, image_url, filename)
                await message.edit_text("<code>Uploading Image...</code>")
                await c.send_document(
                    chat_id,
                    filename,
                    caption=f"<b>Prompt: </b><code>{prompt}</code>\n<b>Model: </b><code>{model}</code>",
                )
                os.remove(filename)
                await message.delete()
        except KeyError:
            try:
                error = response["error"]
                mes = response["message"]
                return await message.edit_text(f"<b>{error}: </b><code>{mes}</code>")
            except KeyError:
                details = response["detail"]
                mes = response["message"]
                return await message.edit_text(f"<b>{details}: </b><code>{mes}</code>")

    except MessageTooLong:
        await message.edit_text(
            f"<b>Model List is too long</b> See the Full List <a href='https://visioncraft.top/api/image/models/{model_category}'> Here </a>"
        )
        return

    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")


@Client.on_message(filters.command("vgif", prefix) & filters.me)
async def vgiff(c: Client, message: Message):
    """Text to video Generation Using SDXL"""

    await message.edit_text("<code>Please Wait...</code>")

    try:
        chat_id = message.chat.id
        model_category = "SD-1.5"
        models = await fetch_models(category=model_category)

        if not message.reply_to_message and len(message.command) > 2:
            model_found = False
            for m in models:
                if message.text.startswith(f"{prefix}vgif {m}"):
                    model = m
                    prompt = message.text[len(f"{prefix}vgif {m}") :].strip()
                    model_found = True
                    break
            if not model_found:
                return await message.edit_text(
                    f"<b>Usage: </b><code>{prefix}vgif [model]* [prompt/reply to prompt]*</code>\n <b>Available Models:</b> <blockquote>{models}</blockquote>"
                )
        elif message.reply_to_message and len(message.command) > 1:
            model = message.text.split(maxsplit=1)[1]
            print(model)
            if model in models:
                prompt = message.reply_to_message.text
            else:
                return await message.edit_text(
                    f"<b>Usage: </b><code>{prefix}vgif [model]* [prompt/reply to prompt]*</code>\n <b>Available Models:</b> <blockquote>{models}</blockquote>"
                )
        else:
            return await message.edit_text(
                f"<b>Usage: </b><code>{prefix}vgif [model]* [prompt/reply to prompt]*</code>\n <b>Available Models:</b> <blockquote>{models}</blockquote>"
            )

        data = {
            "prompt": prompt,
            "model": model,
            "negative_prompt":"EasyNegative, blurry, bad quality",
            "token": vca_api_key,
            "width": 512,
            "height": 512,
            "steps": 30,
            "fps": 16,
            "frames": 16,
            "is_video": True,
            "cfg_scale": 7,
            "sampler": "Euler",
            "loras": {}
        }

        response = await generate_video(data)
        try:
            image_url = response["image_url"]
            async with aiohttp.ClientSession() as session:
                filename = f"{chat_id}_{message.id}.gif"
                await message.edit_text("<code>Downloading Image...</code>")
                await download_image(session, image_url, filename)
                await message.edit_text("<code>Uploading Image...</code>")
                await c.send_document(
                    chat_id,
                    filename,
                    caption=f"<b>Prompt: </b><code>{prompt}</code>\n<b>Model: </b><code>{model}</code>",
                )
                os.remove(filename)
                await message.delete()
        except KeyError:
            try:
                error = response["error"]
                mes = response["message"]
                return await message.edit_text(f"<b>{error}: </b><code>{mes}</code>")
            except KeyError:
                details = response["detail"]
                mes = response["message"]
                return await message.edit_text(f"<b>{details}: </b><code>{mes}</code>")

    except MessageTooLong:
        await message.edit_text(
            f"<b>Model List is too long</b> See the Full List <a href='https://visioncraft.top/api/image/models/{model_category}'> Here </a>"
        )
        return

    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")





modules_help["aiutils"] = {
    "vdxl [model]* [prompt/reply to prompt]*": "Text to Image with SDXL model",
    "vdxl2 [model]* [prompt/reply to prompt]*": "Text to Image with SDXL-2 model",
    "vdxl3 [model]* [prompt/reply to prompt]*": "Text to Image with SDXL-3 model",
    "vpxl [model]* [prompt/reply to prompt]*": "Text to Image with Playground model",
    "vfxl [model]* [prompt/reply to prompt]*": "Text to Image with FLUX model",
    "vpixl [model]* [prompt/reply to prompt]*": "Text to Image with PixArt model",
    "vkxl [model]* [prompt/reply to prompt]*": "Text to Image with Kolors model",
    "vgif [prompt/reply to prompt]*": "Text to GIF",
}
