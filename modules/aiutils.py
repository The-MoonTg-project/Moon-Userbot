import base64
import os

import aiohttp
from pyrogram import Client, enums, filters
from pyrogram.errors import MessageTooLong
from pyrogram.types import Message

from utils.config import vca_api_key
from utils.misc import modules_help, prefix
from utils.scripts import format_exc

api_url = "https://visioncraft.top"


async def fetch_models():
    """Get all available SDXL models"""
    async with aiohttp.ClientSession() as session:
        async with session.get("https://visioncraft.top/sd/models") as response:
            return await response.json()


async def fetch_upscale_models():
    """Get all available upscale models"""
    async with aiohttp.ClientSession() as session:
        async with session.get("https://visioncraft.top/models-upscale") as response:
            return await response.json()


async def generate_gifs(data):
    """Helper Function to generate GIF"""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{api_url}/generate-gif", json=data, verify_ssl=False
        ) as response:
            return await response.json()


async def generate_images(data):
    """Helper Function to generate image using SDXL"""
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{api_url}/sd", json=data) as response:
            return await response.read()


async def generate_dalle(data):
    """Helper Function to generate image using DALL-E 3"""
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{api_url}/dalle", json=data) as response:
            return await response.read()


async def download_image(session, image_url, filename):
    """Get The Image Data From Response"""
    async with session.get(image_url) as response:
        image_data = await response.read()
        with open(filename, "wb") as f:
            f.write(image_data)


async def upscale_request(api_key, image_data):
    """Request Maker Helper function to upscale image for VisionCraft API"""
    image_base64 = base64.b64encode(image_data).decode("utf-8")

    payload = {
        "token": api_key,
        "image": image_base64,
        "model": "R-ESRGAN 4x+",
        "resize": 4,
    }

    # Set up the headers
    headers = {"Content-Type": "application/json"}

    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{api_url}/upscale", json=payload, headers=headers
        ) as response:
            return await response.read()


async def transcribe_audio(api_key, audio_data, language, task):
    """Request Maker Helper function to transcribe audio"""

    audio_base64 = base64.b64encode(audio_data).decode("utf-8")

    payload = {
        "token": api_key,
        "audio": audio_base64,
        "language": language,
        "task": task,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{api_url}/whisper", json=payload) as response:
            return await response.json()


@Client.on_message(filters.command("vdxl", prefix) & filters.me)
async def vdxl(c: Client, message: Message):
    """Text to Image Generation Using SDXL"""

    await message.edit_text("<code>Please Wait...</code>")

    try:
        chat_id = message.chat.id
        models = await fetch_models()

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
            "<b>Model List is too long</b> See the Full List <a href='https://visioncraft.top/sd/models'> Here </a>"
        )
        return

    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")


@Client.on_message(filters.command("dalle", prefix) & filters.me)
async def dalle(c: Client, message: Message):
    """Text to Image Generation Using DALL-E 3"""
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

        data = {"prompt": prompt, "token": vca_api_key, "size": "1792x1024"}

        response = await generate_dalle(data)

        try:
            with open("generated_image.png", "wb") as f:
                f.write(response)
            await message.delete()
            await c.send_document(
                chat_id,
                document="generated_image.png",
                caption=f"<b>Prompt: </b><code>{prompt}</code>\n<b>Model: </b><code>DALL-E 3</code>",
            )
            os.remove("generated_image.png")
        except KeyError:
            try:
                error = response["error"]
                await message.edit_text(f"<code>{error}</code>")
            except KeyError:
                detail = response["detail"]
                await message.edit_text(f"<code>{detail}</code>")

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


@Client.on_message(filters.command("upscale", prefix) & filters.me)
async def upscale(c: Client, message: Message):
    """Default Upscaler of Moon-Userbot: Uses VisionCraft APi"""
    try:
        photo_data = await message.download()
        message_id = message.id
    except ValueError:
        try:
            photo_data = await message.reply_to_message.download()
            message_id = message.reply_to_message.id
        except ValueError:
            await message.edit("<b>File not found</b>")
            return
    i = await message.edit("<code>Processing...</code>")

    api_key = vca_api_key
    with open(photo_data, "rb") as image_file:
        image = image_file.read()
    upscaled_image_data = await upscale_request(api_key, image)
    with open("upscaled_image.png", "wb") as file:
        file.write(upscaled_image_data)
        await i.delete()
        await c.send_document(
            message.chat.id,
            "upscaled_image.png",
            caption="Upscaled!",
            reply_to_message_id=message_id,
        )
        os.remove("upscaled_image.png")


@Client.on_message(filters.command("whisp", prefix) & filters.me)
async def whisp(message: Message):
    """Get Text From Audio: Uses VisionCraft API"""
    try:
        audio_data = await message.reply_to_message.download()
        try:
            if (
                audio_data == enums.MessageMediaType.AUDIO
                or enums.MessageMediaType.VOICE
            ):
                await message.edit("<code>Processing...</code>")

                api_key = vca_api_key
                with open(audio_data, "rb") as audio_file:
                    audio = audio_file.read()
                language = "auto"
                task = "transcribe"
                task_result = await transcribe_audio(api_key, audio, language, task)
                # print(task_result)
                ouput = task_result["text"]
                await message.edit_text(f"Transcribed result:\n <code>{ouput}</code>")
            else:
                await message.edit("<b>To be used on AUIDO files only</b>")
        except KeyError:
            try:
                error = task_result["error"]
                await message.edit_text(f"<code>{error}</code>")
            except KeyError:
                detail = task_result["detail"]
                await message.edit_text(f"<code>{detail}</code>")
    except ValueError:
        await message.edit("<b>File not found</b>")
        return
    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")


modules_help["aiutils"] = {
    "vdxl [model]* [prompt/reply to prompt]*": "Text to Image with SDXL model",
    "vgif [prompt/reply to prompt]*": "Text to GIF",
    "upscale [cap/reply to image]*": "Upscale Image through VisionCraft API",
    "lupscale [cap/reply to image]*": "Upscale Image through Lexica API",
    "whisp": "Audio transcription or translation",
    "dalle [prompt/reply to prompt]": "Generate image using DALL-E 3",
}
