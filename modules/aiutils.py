import requests, base64, os

from pyrogram import Client, enums, filters
from pyrogram.types import Message

from utils.config import vca_api_key
from utils.misc import modules_help, prefix
from utils.scripts import format_exc, edit_or_reply, import_library

lexica = import_library("lexica", "lexica-api")
from lexica import Client as lcl

# Define the API endpoint
api_url = "https://api.visioncraft.top"

def upscale_request_lexica(image: bytes) -> bytes:
    client = lcl()
    imageBytes = client.upscale(image)
    with open('upscaled.png', 'wb') as f:
        f.write(imageBytes)

def upscale_request_vc(image):
    b = base64.b64encode(image).decode('utf-8')
    payload = {
        "token": vca_api_key,
        "image": b
    }
    url = 'https://visioncraft-rs24.koyeb.app/upscale'
    headers = {"content-type": "application/json"}

    resp = requests.post(url, json=payload, headers=headers)
    content = resp.content
    return content

@Client.on_message(filters.command("vdxl", prefix) & filters.me)
async def vdxl(c: Client, message: Message):
    try:
        chat_id = message.chat.id
        await message.edit_text("<code>Please Wait...</code>")

        if len(message.command) > 1:
         prompt = message.text.split(maxsplit=1)[1]
        elif message.reply_to_message:
         prompt = message.reply_to_message.text
        else:
         await message.edit_text(
            f"<b>Usage: </b><code>{prefix}vdxl [prompt/reply to prompt]</code>"
        )
         return

        data = {
            "prompt": prompt,
            "model": "sdxl-turbo",
            "negative_prompt": "bad quality"
            "token": vca_api_key,
            "width": 1024,
            "height": 1024,
            # "steps": 30,
            # "cfg_scale": 8,
            "sampler": "euler",
            "scheduler": "normal",
            "watermark": False
        }
        
        # Send the request to generate images
        response = requests.post(f"{api_url}/generate-xl", json=data)

        # Get the image from the response
        image = response.content

        # Save the image locally
        with open(f"generated_image.png", "wb") as f:
            f.write(image)

            await message.delete()
        #for i, image_url in enumerate(image_urls):
            await c.send_photo(chat_id, photo=f"generated_image.png", caption=f"<b>Prompt:</b><code>{prompt}</code>")

    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")
    finally:
        os.remove(f"generated_image.png")


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
async def upscale(client: Client, message: Message):
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
        upscaled_image = upscale_request_vc(image)
        with open('upscaled.png', 'wb') as f:
            f.write(upscaled_image)
        # await message.delete()
        await client.send_document(message.chat.id, 'upscaled.png', caption="Upscaled!", reply_to_message_id=message.id)
        os.remove('upscaled.png')

modules_help["aiutils"] = {
    "vdxl [prompt/reply to prompt]*": "Text to Image with SDXL model",
    "upscale [cap/reply to image]*": "Upscale Image through VisionCraft API",
    "lupscale [cap/reply to image]*": "Upscale Image through Lexica API",
}
