import os
import requests

from pyrogram import Client, filters
from pyrogram.types import Message

from utils.misc import modules_help, prefix
from utils.scripts import format_exc
from utils.lexicapi import ImageGeneration, UpscaleImages, ImageModels

@Client.on_message(filters.command("lupscale", prefix) & filters.me)
async def lupscale(client: Client, message: Message):
    """Upscale Image Using Lexica API"""

    await message.edit("<code>Processing...</code>")
    try:
        photo_data = await message.download()
    except ValueError:
        try:
            photo_data = await message.reply_to_message.download()
        except ValueError:
            await message.edit("<b>File not found</b>")
            return
    try:
        with open(photo_data, 'rb') as image_file:
            image = image_file.read()
        upscaled_image = await UpscaleImages(image)
        if message.reply_to_message:
            message_id = message.reply_to_message.id
            await message.delete()
        else:
            message_id = message.id
        await client.send_document(message.chat.id, upscaled_image, caption="Upscaled!", reply_to_message_id=message_id)
        os.remove(upscaled_image)
    except Exception as e:
        await message.edit(format_exc(e))

@Client.on_message(filters.command("lgen", prefix) & filters.me)
async def lgen(client: Client, message: Message):
    try:
        await message.edit_text("<code>Processing...</code>")

        models = ImageModels()
        models_ids = models.values()

        if len(message.command) > 2:
            model_id = int(message.text.split()[1])
            if model_id not in models_ids:
                return await message.edit_text(f"<b>Usage: </b><code>{prefix}lgen [model_id]* [prompt/reply to prompt]*</code>\n <b>Available Models and IDs:</b> <blockquote>{models}</blockquote>")
            message_id = None
            prompt = ' '.join(message.text.split()[2:])
        elif message.reply_to_message and len(message.command) > 1:
            model_id = int(message.text.split()[1])
            if model_id not in models_ids:
                return await message.edit_text(f"<b>Usage: </b><code>{prefix}lgen [model_id]* [prompt/reply to prompt]*</code>\n <b>Available Models and IDs:</b> <blockquote>{models}</blockquote>")
            message_id = message.reply_to_message.id
            prompt = message.reply_to_message.text
        else:
            return await message.edit_text(f"<b>Usage: </b><code>{prefix}lgen [model_id]* [prompt/reply to prompt]*</code>\n <b>Available Models and IDs:</b> <blockquote>{models}</blockquote>")

        for key, val in models.items():
            if val == model_id:
                model_name = key

        img = await ImageGeneration(model_id, prompt)
        if img is None or img == 1 or img == 2:
            return await message.edit_text("Something went wrong!")
        if img == 69:
            return await message.edit_text("NSFW is not allowed")
        img_url = img[0]
        with open("generated_image.png", 'wb') as f:
            f.write(requests.get(img_url, timeout=5).content)

        await client.send_document(message.chat.id, "generated_image.png", caption=f"<b>Prompt: </b><code>{prompt}</code>\n<b>Model: </b><code>{model_name}</code>", reply_to_message_id=message_id)
        os.remove("generated_image.png")
    except Exception as e:
        await message.edit(format_exc(e))

modules_help["lexica"] = {
    "lgen [model_id]* [prompt/reply to prompt]*": "Generate Image with Lexica API",
    "lupscale [cap/reply to image]*": "Upscale Image through Lexica API",
}
