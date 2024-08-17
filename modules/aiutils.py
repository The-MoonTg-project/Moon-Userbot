import os

import aiohttp
from pyrogram import Client, filters
from pyrogram.errors import MessageTooLong
from pyrogram.types import Message

from utils.config import vca_api_key
from utils.misc import modules_help, prefix
from utils.scripts import format_exc

api_url = "https://visioncraft.top"


async def fetch_models(category: str):
    """Get all available SDXL models"""
    async with aiohttp.ClientSession() as session, session.get(
        f"https://visioncraft.top/image/models/{category}"
    ) as response:
        return await response.json()


async def generate_gifs(data):
    """Helper Function to generate GIF"""
    async with aiohttp.ClientSession() as session, session.post(
        f"{api_url}/generate-gif", json=data, verify_ssl=False
    ) as response:
        return await response.json()


async def generate_images(data):
    """Helper Function to generate image using SDXL"""
    async with aiohttp.ClientSession() as session, session.post(
        f"{api_url}/image/generate", json=data
    ) as response:
        return await response.read()


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
            "prompt": prompt,
            "model": model,
            "negative_prompt": "canvas frame, cartoon, ((disfigured)), ((bad art)), ((deformed)),((extra limbs)),((close up)),((b&w)), weird colors, blurry, (((duplicate))), ((morbid)), ((mutilated)), [out of frame], extra fingers, mutated hands, ((poorly drawn hands)), ((poorly drawn face)), (((mutation))), (((deformed))), ((ugly)), blurry, ((bad anatomy)), (((bad proportions))), ((extra limbs)), cloned face, (((disfigured))), out of frame, ugly, extra limbs, (bad anatomy), gross proportions, (malformed limbs), ((missing arms)), ((missing legs)), (((extra arms))), (((extra legs))), mutated hands, (fused fingers), (too many fingers), (((long neck))), Photoshop, video game, ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, mutation, mutated, extra limbs, extra legs, extra arms, disfigured, deformed, cross-eye, body out of frame, blurry, bad art, bad anatomy",
            "token": vca_api_key,
            "image_count": 1,
            "width": 1024,
            "height": 1024,
            "steps": 30,
            "cfg_scale": 8,
            "sampler": "Euler",
            "upscale": True,
        }

        response = await generate_images(data)

        try:
            with open("generated_image.png", "wb") as f:
                f.write(response)
            await message.delete()
            await c.send_document(
                chat_id,
                document="generated_image.png",
                caption=f"<b>Prompt: </b><code>{prompt}</code>\n<b>Model: </b><code>{model}</code>",
            )
            os.remove("generated_image.png")
        except KeyError:
            try:
                error = response["error"]
                await message.edit_text(f"<code>{error}</code>")
            except KeyError:
                detail = response["detail"]
                await message.edit_text(f"<code>{detail}</code>")

    except MessageTooLong:
        await message.edit_text(
            f"<b>Model List is too long</b> See the Full List <a href='https://visioncraft.top/image/models/{model_category}'> Here </a>"
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
            "prompt": prompt,
            "model": model,
            "negative_prompt": "canvas frame, cartoon, ((disfigured)), ((bad art)), ((deformed)),((extra limbs)),((close up)),((b&w)), weird colors, blurry, (((duplicate))), ((morbid)), ((mutilated)), [out of frame], extra fingers, mutated hands, ((poorly drawn hands)), ((poorly drawn face)), (((mutation))), (((deformed))), ((ugly)), blurry, ((bad anatomy)), (((bad proportions))), ((extra limbs)), cloned face, (((disfigured))), out of frame, ugly, extra limbs, (bad anatomy), gross proportions, (malformed limbs), ((missing arms)), ((missing legs)), (((extra arms))), (((extra legs))), mutated hands, (fused fingers), (too many fingers), (((long neck))), Photoshop, video game, ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, mutation, mutated, extra limbs, extra legs, extra arms, disfigured, deformed, cross-eye, body out of frame, blurry, bad art, bad anatomy",
            "token": vca_api_key,
            "image_count": 1,
            "width": 1024,
            "height": 1024,
            "steps": 30,
            "cfg_scale": 8,
            "sampler": "Euler",
            "upscale": True,
        }

        response = await generate_images(data)

        try:
            with open("generated_image.png", "wb") as f:
                f.write(response)
            await message.delete()
            await c.send_document(
                chat_id,
                document="generated_image.png",
                caption=f"<b>Prompt: </b><code>{prompt}</code>\n<b>Model: </b><code>{model}</code>",
            )
            os.remove("generated_image.png")
        except KeyError:
            try:
                error = response["error"]
                await message.edit_text(f"<code>{error}</code>")
            except KeyError:
                detail = response["detail"]
                await message.edit_text(f"<code>{detail}</code>")

    except MessageTooLong:
        await message.edit_text(
            f"<b>Model List is too long</b> See the Full List <a href='https://visioncraft.top/image/models/{model_category}'> Here </a>"
        )
        return

    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")


@Client.on_message(filters.command("vdxl2", prefix) & filters.me)
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
            "prompt": prompt,
            "model": model,
            "negative_prompt": "canvas frame, cartoon, ((disfigured)), ((bad art)), ((deformed)),((extra limbs)),((close up)),((b&w)), weird colors, blurry, (((duplicate))), ((morbid)), ((mutilated)), [out of frame], extra fingers, mutated hands, ((poorly drawn hands)), ((poorly drawn face)), (((mutation))), (((deformed))), ((ugly)), blurry, ((bad anatomy)), (((bad proportions))), ((extra limbs)), cloned face, (((disfigured))), out of frame, ugly, extra limbs, (bad anatomy), gross proportions, (malformed limbs), ((missing arms)), ((missing legs)), (((extra arms))), (((extra legs))), mutated hands, (fused fingers), (too many fingers), (((long neck))), Photoshop, video game, ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, mutation, mutated, extra limbs, extra legs, extra arms, disfigured, deformed, cross-eye, body out of frame, blurry, bad art, bad anatomy",
            "token": vca_api_key,
            "image_count": 1,
            "width": 1024,
            "height": 1024,
            "steps": 30,
            "cfg_scale": 8,
            "sampler": "Euler",
            "upscale": True,
        }

        response = await generate_images(data)

        try:
            with open("generated_image.png", "wb") as f:
                f.write(response)
            await message.delete()
            await c.send_document(
                chat_id,
                document="generated_image.png",
                caption=f"<b>Prompt: </b><code>{prompt}</code>\n<b>Model: </b><code>{model}</code>",
            )
            os.remove("generated_image.png")
        except KeyError:
            try:
                error = response["error"]
                await message.edit_text(f"<code>{error}</code>")
            except KeyError:
                detail = response["detail"]
                await message.edit_text(f"<code>{detail}</code>")

    except MessageTooLong:
        await message.edit_text(
            f"<b>Model List is too long</b> See the Full List <a href='https://visioncraft.top/image/models/{model_category}'> Here </a>"
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
            "prompt": prompt,
            "model": model,
            "negative_prompt": "canvas frame, cartoon, ((disfigured)), ((bad art)), ((deformed)),((extra limbs)),((close up)),((b&w)), weird colors, blurry, (((duplicate))), ((morbid)), ((mutilated)), [out of frame], extra fingers, mutated hands, ((poorly drawn hands)), ((poorly drawn face)), (((mutation))), (((deformed))), ((ugly)), blurry, ((bad anatomy)), (((bad proportions))), ((extra limbs)), cloned face, (((disfigured))), out of frame, ugly, extra limbs, (bad anatomy), gross proportions, (malformed limbs), ((missing arms)), ((missing legs)), (((extra arms))), (((extra legs))), mutated hands, (fused fingers), (too many fingers), (((long neck))), Photoshop, video game, ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, mutation, mutated, extra limbs, extra legs, extra arms, disfigured, deformed, cross-eye, body out of frame, blurry, bad art, bad anatomy",
            "token": vca_api_key,
            "image_count": 1,
            "width": 1024,
            "height": 1024,
            "steps": 30,
            "cfg_scale": 1,
            "sampler": "Euler",
            "upscale": True,
        }

        response = await generate_images(data)

        try:
            with open("generated_image.png", "wb") as f:
                f.write(response)
            await message.delete()
            await c.send_document(
                chat_id,
                document="generated_image.png",
                caption=f"<b>Prompt: </b><code>{prompt}</code>\n<b>Model: </b><code>{model}</code>",
            )
            os.remove("generated_image.png")
        except KeyError:
            try:
                error = response["error"]
                await message.edit_text(f"<code>{error}</code>")
            except KeyError:
                detail = response["detail"]
                await message.edit_text(f"<code>{detail}</code>")

    except MessageTooLong:
        await message.edit_text(
            f"<b>Model List is too long</b> See the Full List <a href='https://visioncraft.top/image/models/{model_category}'> Here </a>"
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
            "prompt": prompt,
            "model": model,
            "negative_prompt": "canvas frame, cartoon, ((disfigured)), ((bad art)), ((deformed)),((extra limbs)),((close up)),((b&w)), weird colors, blurry, (((duplicate))), ((morbid)), ((mutilated)), [out of frame], extra fingers, mutated hands, ((poorly drawn hands)), ((poorly drawn face)), (((mutation))), (((deformed))), ((ugly)), blurry, ((bad anatomy)), (((bad proportions))), ((extra limbs)), cloned face, (((disfigured))), out of frame, ugly, extra limbs, (bad anatomy), gross proportions, (malformed limbs), ((missing arms)), ((missing legs)), (((extra arms))), (((extra legs))), mutated hands, (fused fingers), (too many fingers), (((long neck))), Photoshop, video game, ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, mutation, mutated, extra limbs, extra legs, extra arms, disfigured, deformed, cross-eye, body out of frame, blurry, bad art, bad anatomy",
            "token": vca_api_key,
            "image_count": 1,
            "width": 1024,
            "height": 1024,
            "steps": 30,
            "cfg_scale": 8,
            "sampler": "Euler",
            "upscale": True,
        }

        response = await generate_images(data)

        try:
            with open("generated_image.png", "wb") as f:
                f.write(response)
            await message.delete()
            await c.send_document(
                chat_id,
                document="generated_image.png",
                caption=f"<b>Prompt: </b><code>{prompt}</code>\n<b>Model: </b><code>{model}</code>",
            )
            os.remove("generated_image.png")
        except KeyError:
            try:
                error = response["error"]
                await message.edit_text(f"<code>{error}</code>")
            except KeyError:
                detail = response["detail"]
                await message.edit_text(f"<code>{detail}</code>")

    except MessageTooLong:
        await message.edit_text(
            f"<b>Model List is too long</b> See the Full List <a href='https://visioncraft.top/image/models/{model_category}'> Here </a>"
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
            "prompt": prompt,
            "model": model,
            "negative_prompt": "canvas frame, cartoon, ((disfigured)), ((bad art)), ((deformed)),((extra limbs)),((close up)),((b&w)), weird colors, blurry, (((duplicate))), ((morbid)), ((mutilated)), [out of frame], extra fingers, mutated hands, ((poorly drawn hands)), ((poorly drawn face)), (((mutation))), (((deformed))), ((ugly)), blurry, ((bad anatomy)), (((bad proportions))), ((extra limbs)), cloned face, (((disfigured))), out of frame, ugly, extra limbs, (bad anatomy), gross proportions, (malformed limbs), ((missing arms)), ((missing legs)), (((extra arms))), (((extra legs))), mutated hands, (fused fingers), (too many fingers), (((long neck))), Photoshop, video game, ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, mutation, mutated, extra limbs, extra legs, extra arms, disfigured, deformed, cross-eye, body out of frame, blurry, bad art, bad anatomy",
            "token": vca_api_key,
            "image_count": 1,
            "width": 1024,
            "height": 1024,
            "steps": 30,
            "cfg_scale": 8,
            "sampler": "Euler",
            "upscale": True,
        }

        response = await generate_images(data)

        try:
            with open("generated_image.png", "wb") as f:
                f.write(response)
            await message.delete()
            await c.send_document(
                chat_id,
                document="generated_image.png",
                caption=f"<b>Prompt: </b><code>{prompt}</code>\n<b>Model: </b><code>{model}</code>",
            )
            os.remove("generated_image.png")
        except KeyError:
            try:
                error = response["error"]
                await message.edit_text(f"<code>{error}</code>")
            except KeyError:
                detail = response["detail"]
                await message.edit_text(f"<code>{detail}</code>")

    except MessageTooLong:
        await message.edit_text(
            f"<b>Model List is too long</b> See the Full List <a href='https://visioncraft.top/image/models/{model_category}'> Here </a>"
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
            "prompt": prompt,
            "model": model,
            "negative_prompt": "canvas frame, cartoon, ((disfigured)), ((bad art)), ((deformed)),((extra limbs)),((close up)),((b&w)), weird colors, blurry, (((duplicate))), ((morbid)), ((mutilated)), [out of frame], extra fingers, mutated hands, ((poorly drawn hands)), ((poorly drawn face)), (((mutation))), (((deformed))), ((ugly)), blurry, ((bad anatomy)), (((bad proportions))), ((extra limbs)), cloned face, (((disfigured))), out of frame, ugly, extra limbs, (bad anatomy), gross proportions, (malformed limbs), ((missing arms)), ((missing legs)), (((extra arms))), (((extra legs))), mutated hands, (fused fingers), (too many fingers), (((long neck))), Photoshop, video game, ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, mutation, mutated, extra limbs, extra legs, extra arms, disfigured, deformed, cross-eye, body out of frame, blurry, bad art, bad anatomy",
            "token": vca_api_key,
            "image_count": 1,
            "width": 1024,
            "height": 1024,
            "steps": 30,
            "cfg_scale": 8,
            "sampler": "Euler",
            "upscale": True,
        }

        response = await generate_images(data)

        try:
            with open("generated_image.png", "wb") as f:
                f.write(response)
            await message.delete()
            await c.send_document(
                chat_id,
                document="generated_image.png",
                caption=f"<b>Prompt: </b><code>{prompt}</code>\n<b>Model: </b><code>{model}</code>",
            )
            os.remove("generated_image.png")
        except KeyError:
            try:
                error = response["error"]
                await message.edit_text(f"<code>{error}</code>")
            except KeyError:
                detail = response["detail"]
                await message.edit_text(f"<code>{detail}</code>")

    except MessageTooLong:
        await message.edit_text(
            f"<b>Model List is too long</b> See the Full List <a href='https://visioncraft.top/image/models/{model_category}'> Here </a>"
        )
        return

    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")


@Client.on_message(filters.command("vgif", prefix) & filters.me)
async def vgif(c: Client, message: Message):
    """Text2GIF Using VisionCraft API"""
    try:
        chat_id = message.chat.id
        await message.edit_text("<code>Please Wait...</code>")

        if len(message.command) >= 2:
            prompt = message.text.split(maxsplit=1)[1]
        elif message.reply_to_message:
            prompt = message.reply_to_message.text
        else:
            await message.edit_text(
                f"<b>Usage: </b><code>{prefix}vgif [prompt/reply to prompt]*</code>"
            )
            return

        data = {
            "prompt": prompt,
            "negative_prompt": "canvas frame, cartoon, ((disfigured)), ((bad art)), ((deformed)),((extra limbs)),((close up)),((b&w)), weird colors, blurry, (((duplicate))), ((morbid)), ((mutilated)), [out of frame], extra fingers, mutated hands, ((poorly drawn hands)), ((poorly drawn face)), (((mutation))), (((deformed))), ((ugly)), blurry, ((bad anatomy)), (((bad proportions))), ((extra limbs)), cloned face, (((disfigured))), out of frame, ugly, extra limbs, (bad anatomy), gross proportions, (malformed limbs), ((missing arms)), ((missing legs)), (((extra arms))), (((extra legs))), mutated hands, (fused fingers), (too many fingers), (((long neck))), Photoshop, video game, ugly, tiling, poorly drawn hands, poorly drawn feet, poorly drawn face, out of frame, mutation, mutated, extra limbs, extra legs, extra arms, disfigured, deformed, cross-eye, body out of frame, blurry, bad art, bad anatomy",
            "token": vca_api_key,
            "steps": 30,
            "cfg_scale": 8,
            "sampler": "Euler",
        }

        response = await generate_gifs(data)

        try:
            image_url = response["images"][0]
            async with aiohttp.ClientSession() as session:
                await download_image(session, image_url, "generated_image.gif")
                await message.delete()
                await c.send_animation(
                    chat_id,
                    animation="generated_image.gif",
                    caption=f"<b>Prompt: </b><code>{prompt}</code>",
                )
                os.remove("generated_image.gif")
        except KeyError:
            try:
                error = response["error"]
                await message.edit_text(f"<code>{error}</code>")
            except KeyError:
                detail = response["detail"]
                await message.edit_text(f"<code>{detail}</code>")

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
