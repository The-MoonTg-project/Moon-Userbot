import requests, base64, os
import aiohttp
import asyncio

from pyrogram import Client, enums, filters
from pyrogram.types import Message

from utils.config import vca_api_key
from utils.misc import modules_help, prefix
from utils.scripts import format_exc, edit_or_reply, import_library

lexica = import_library("lexica", "lexica-api")
from lexica import Client as lcl

async def fetch_models():
    """Get all available SD 1.X models"""
    async with aiohttp.ClientSession() as session:
        async with session.get('https://visioncraft.top/models') as response:
            return await response.json()

async def fetch_upscale_models():
    """Get all available upscale models"""
    async with aiohttp.ClientSession() as session:
        async with session.get('https://visioncraft.top/models-upscale') as response:
            return await response.json()

async def generate_gifs(api_url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{api_url}/generate-gif", json=data, verify_ssl=False) as response:
            return await response.json()

async def generate_images(api_url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{api_url}/generate", json=data) as response:
            return await response.json()

async def download_image(session, image_url, filename):
    async with session.get(image_url) as response:
        image_data = await response.read()
        with open(filename, "wb") as f:
            f.write(image_data)

def upscale_request_lexica(image: bytes) -> bytes:
    client = lcl()
    imageBytes = client.upscale(image)
    with open('upscaled.png', 'wb') as f:
        f.write(imageBytes)

async def upscale_request_vc(api_url, api_key, image_data):
    # Encode the image data to base64
    image_base64 = base64.b64encode(image_data).decode('utf-8')

    # Set up the payload
    payload = {
        "token": api_key,
        "image": image_base64,
        "model": "R-ESRGAN 4x+",
        "resize": 4
    }

    # Set up the headers
    headers = {"Content-Type": "application/json"}

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{api_url}/upscale", json=payload, headers=headers) as response:
            return await response.read()

async def transcribe_audio(api_url, api_key, audio_data, language, task):
    # Encode the audio data to base64
    audio_base64 = base64.b64encode(audio_data).decode("utf-8")

    # Set up the payload
    payload = {
        "token": api_key,
        "audio": audio_base64,
        "language": language,
        "task": task
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(f"{api_url}/whisper", json=payload) as response:
            return await response.json()

@Client.on_message(filters.command("vdxl", prefix) & filters.me)
async def vdxl(c: Client, message: Message):
    try:
        chat_id = message.chat.id
        api_url = "https://visioncraft.top"
        models = await fetch_models()

        await message.edit_text("<code>Please Wait...</code>")

        if len(message.command) >= 2:
         model, prompt = message.text.split(maxsplit=2)[1:]
         if model not in models:
            await message.edit_text(f"<b>Usage: </b><code>{prefix}vdxl [model]* [prompt/reply to prompt]*</code>\n <b>Available Models:</b> <blockquote>{models}</blockquote>")

        elif message.reply_to_message and len(message.command) > 1:
         model = message.text.split(maxsplit=1)[1]
         if model in models:
            prompt = message.reply_to_message.text
         else:
            await message.edit_text(f"<b>Usage: </b><code>{prefix}vdxl [model]* [prompt/reply to prompt]*</code>\n <b>Available Models:</b> <blockquote>{models}</blockquote>")

        else:
         await message.edit_text(
            f"<b>Usage: </b><code>{prefix}vdxl [model]* [prompt/reply to prompt]*</code>\n <b>Available Models:</b> <blockquote>{models}</blockquote>"
        )
         return

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
            "upscale": True
        }
        

        # Generate images asynchronously
        response = await generate_images(api_url, data)

        try:
            image_urls = response["images"]
            if isinstance(image_urls, list) and image_urls:
                # Extract the first URL from the list
                image_url = image_urls[0]
                # print(image_url)

                # Download and save the generated images
                async with aiohttp.ClientSession() as session:
                    await download_image(session, image_url, f"generated_image.png")
                    await message.delete()
                    await c.send_document(chat_id, document=f"generated_image.png", caption=f"<b>Prompt: </b><code>{prompt}</code>\n<b>Model: </b><code>{model}</code>")
                    await os.remove(f"generated_image.png")
            else:
                await message.edit_text("No valid URL's found in response")
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
    try:
        chat_id = message.chat.id
        api_url = "https://visioncraft.top"

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
            "sampler": "Euler"
        }
        

        # Generate images asynchronously
        response = await generate_gifs(api_url, data)

        try:
            image_url = response["images"][0]

            # Download and save the generated images
            async with aiohttp.ClientSession() as session:
                await download_image(session, image_url, f"generated_image.gif")
                await message.delete()
                await c.send_media_group(chat_id, media=f"generated_image.gif")
                await os.remove(f"generated_image.gif")
        except KeyError:
            try:
                error = response["error"]
                await message.edit_text(f"<code>{error}</code>")
            except KeyError:
                detail = response["detail"]
                await message.edit_text(f"<code>{detail}</code>")

    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")


@Client.on_message(filters.command("lupscale", prefix) & filters.me)
async def lupscale(client: Client, message: Message):
        try:
            photo_data = await message.download()
        except ValueError:
            try:
                photo_data = await message.reply_to_message.download()
            except ValueError:
                await message.edit("<b>File not found</b>", parse_mode=enums.ParseMode.HTML)
                return
        await message.edit("<code>Processing...</code>", parse_mode=enums.ParseMode.HTML)
        image = open(photo_data, 'rb').read()
        upscaled_image = upscale_request_lexica(image)
        # await message.delete()
        await client.send_document(message.chat.id, 'upscaled.png', caption="Upscaled!", reply_to_message_id=message.id)
        os.remove('upscaled.png')

@Client.on_message(filters.command("upscale", prefix) & filters.me)
async def upscale(c: Client, message: Message):
        try:
            photo_data = await message.download()
            message_id = message.id
        except ValueError:
            try:
                photo_data = await message.reply_to_message.download()
                message_id = message.reply_to_message.id
            except ValueError:
                await message.edit("<b>File not found</b>", parse_mode=enums.ParseMode.HTML)
                return
        i = await message.edit("<code>Processing...</code>", parse_mode=enums.ParseMode.HTML)

        api_url = "https://visioncraft.top"
        api_key = vca_api_key

        image = open(photo_data, 'rb').read()
        upscaled_image_data = await upscale_request_vc(api_url, api_key, image)
        with open('upscaled_image.png', 'wb') as file:
            file.write(upscaled_image_data)
            await i.delete()
            await c.send_document(message.chat.id, 'upscaled_image.png', caption="Upscaled!", reply_to_message_id=message_id)
            os.remove('upscaled_image.png')

@Client.on_message(filters.command("whisp", prefix) & filters.me)
async def whisp(c: Client, message: Message):
    try:
        audio_data = await message.reply_to_message.download()
        message_id = message.reply_to_message.id
        try:
            if audio_data == enums.MessageMediaType.AUDIO or enums.MessageMediaType.VOICE:
                i = await message.edit("<code>Processing...</code>", parse_mode=enums.ParseMode.HTML)
                api_url = "https://visioncraft.top"
                api_key = vca_api_key
                audio = open(audio_data, 'rb').read()
                language = 'auto'
                task = 'transcribe'
                task_result = await transcribe_audio(api_url, api_key, audio, language, task)
                # print(task_result)
                ouput = task_result['text']
                await message.edit_text(f"Transcribed result:\n <code>{ouput}</code>")
            else:
                await message.edit("<b>To be used on AUIDO files only</b>", parse_mode=enums.ParseMode.HTML)
        except KeyError:
            try:
                error = task_result["error"]
                await message.edit_text(f"<code>{error}</code>")
            except KeyError:
                detail = task_result["detail"]
                await message.edit_text(f"<code>{detail}</code>")
    except ValueError:
        await message.edit("<b>File not found</b>", parse_mode=enums.ParseMode.HTML)
        return
    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")

modules_help["aiutils"] = {
    "vdxl [model]* [prompt/reply to prompt]*": "Text to Image with SDXL model",
    "vgif [prompt/reply to prompt]*": "Text to GIF",
    "upscale [cap/reply to image]*": "Upscale Image through VisionCraft API",
    "lupscale [cap/reply to image]*": "Upscale Image through Lexica API",
    "whisp": "Audio transcription or translation"
}
