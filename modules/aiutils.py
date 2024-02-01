import requests, base64, os

from pyrogram import Client, enums, filters
from pyrogram.types import Message

from utils.config import vca_api_key
from utils.misc import modules_help, prefix
from utils.scripts import format_exc, edit_or_reply, import_library

lexica = import_library("lexica", "lexica-api")
from lexica import Client as lcl

# Define the API endpoint
api_url = "https://visioncraft-rs24.koyeb.app"

def upscale_request(image: bytes) -> bytes:
    client = lcl()
    imageBytes = client.upscale(image)
    with open('upscaled.png', 'wb') as f:
        f.write(imageBytes)

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
    "model": "juggernaut-xl-V5",
    "prompt": prompt,
    "negative_prompt": "",
    "image_count": 1,
    "token": vca_api_key,
    "width": 1024,
    "height": 768,
    "enhance": True,

    "watermark": False
}
        # Send the request to generate images
        response = requests.post(f"{api_url}/generate-xl", json=data, verify=False)
        
        job_id = response.json()["job_id"]

        while True:
            response = requests.post("https://visioncraft-rs24.koyeb.app/job-status", json={"job_id": job_id})
            if response.json()["image"]:
            image_url = response.json()["image"]
            break

        # Download and save the generated images
        for i, image_url in enumerate(image_urls):
            # Get the image data from the URL
            response = requests.get(image_url)
            # Save the image locally
            with open(f"generated_image_{i}.png", "wb") as f:
                f.write(response.content)

            await message.delete()
        #for i, image_url in enumerate(image_urls):
            await c.send_photo(chat_id, photo=f"generated_image_{i}.png", caption=f"<b>Prompt:</b><code>{prompt}</code>")

    except Exception as e:
        await message.edit_text(f"An error occurred: {format_exc(e)}")
    finally:
        for i, image_url in enumerate(image_urls):
            os.remove(f"generated_image_{i}.png")


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
        upscaled_image = upscale_request(image)
        # await message.delete()
        await client.send_document(message.chat.id, 'upscaled.png', caption="Upscaled!", reply_to_message_id=message.id)
        os.remove('upscaled.png')

modules_help["aiutils"] = {
    "vdxl [prompt/reply to prompt]*": "Text to Image with SDXL model",
    "upscale [cap/reply to image]*": "As the name says",
}
