import os
import requests
import aiofiles
import base64

from pyrogram import Client, filters
from pyrogram.types import Message, InputMediaPhoto
from pyrogram.errors import MediaCaptionTooLong, MessageTooLong

from utils.misc import prefix, modules_help
from utils.scripts import format_exc

url = 'https://api.safone.dev'

headers = {
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'DNT': '1',
    'Referer': 'https://api.safone.dev/docs',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'accept': 'application/json',
    'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"'
}

async def telegraph(title, user_name, content):

    formatted_content = '<br>'.join(content.split('\n'))
    formatted_content = '<p>' + formatted_content + '</p>'

    data = {
    "title": title,
    "content": formatted_content,
    "author_name": user_name
    }

    response = requests.post(url=f"{url}/telegraph/text", headers=headers, json=data, timeout=5)

    result = response.json()

    return result['url']

async def voice_characters():

    response = requests.get(url=f"{url}/speech/characters", headers=headers, timeout=5)

    result = response.json()

    return ', '.join(result['characters'])

@Client.on_message(filters.command("app", prefix) & filters.me)
async def app(client: Client, message: Message):
    try:
        chat_id = message.chat.id
        await message.edit_text("Processing...")
        if len(message.command) > 1:
            query = message.text.split(maxsplit=1)[1]
        else:
            message.edit_text("What should i search? You didn't provided me with any value to search")

        response = requests.get(url=f"{url}/apps?query={query}&limit=1", headers=headers, timeout=5)
        if response.status_code != 200:
            await message.edit_text("Something went wrong")
            return

        result = response.json()

        try:
            coverImage_url = result['results'][0]['icon']
            coverImage = requests.get(url=coverImage_url).content
            async with aiofiles.open('coverImage.jpg', mode='wb') as f:
                await f.write(coverImage)

        except Exception:
            coverImage = None

        description = result['results'][0]['description']
        developer = result['results'][0]['developer']
        IsFree = result['results'][0]['free']
        genre = result['results'][0]['genre']
        package_name = result['results'][0]['id']
        title = result['results'][0]['title']
        price = result['results'][0]['price']
        link = result['results'][0]['link']
        rating = result['results'][0]['rating']

        await message.delete()
        await client.send_media_group(
            chat_id,
            [
                InputMediaPhoto('coverImage.jpg', caption=f"<b>Title:</b> <code>{title}</code>\n<b>Rating:</b> <code>{rating}</code>\n<b>IsFree:</b> <code>{IsFree}</code>\n<b>Price:</b> <code>{price}</code>\n<b>Package Name:</b> <code>{package_name}</code>\n<b>Genres:</b> <code>{genre}</code>\n<b>Developer:</b> <code>{developer}\n<b>Description:</b> {description}\n<b>Link:</b> {link}")
            ])

    except MediaCaptionTooLong:
        description = description[:850]
        await message.delete()
        await client.send_media_group(
            chat_id,
            [
                InputMediaPhoto('coverImage.jpg', caption=f"<b>Title:</b> <code>{title}</code>\n<b>Rating:</b> <code>{rating}</code>\n<b>IsFree:</b> <code>{IsFree}</code>\n<b>Price:</b> <code>{price}</code>\n<b>Package Name:</b> <code>{package_name}</code>\n<b>Genres:</b> <code>{genre}</code>\n<b>Developer:</b> <code>{developer}\n<b>Description:</b> {description}\n<b>Link:</b> {link}")
            ])
    except Exception as e:
        await message.edit_text(format_exc(e))
    finally:
        if os.path.exists('coverImage.jpg'):
            os.remove('coverImage.jpg')


@Client.on_message(filters.command("tsearch", prefix) & filters.me)
async def tsearch(client: Client, message: Message):
    try:
        chat_id = message.chat.id
        limit = 10
        await message.edit_text("Processing...")
        if len(message.command) > 1:
            query = message.text.split(maxsplit=1)[1]
        else:
            message.edit_text("What should i search? You didn't provided me with any value to search")

        response = requests.get(url=f"{url}/torrent?query={query}&limit={limit}", headers=headers)
        if response.status_code != 200:
            await message.edit_text("Something went wrong")
            return

        result = response.json()

        coverImage_url = result['results'][0]['thumbnail']
        description = result['results'][0]['description']
        genre = result['results'][0]['genre']
        category = result['results'][0]['category']
        title = result['results'][0]['name']
        link = result['results'][0]['magnetLink']
        link_result = await telegraph(title=title,user_name=message.from_user.first_name, content=link)
        language = result['results'][0]['language']
        size = result['results'][0]['size']

        results = []

        for i in range(min(limit, len(result['results']))):
            descriptions = result['results'][i]['description']
            genres = result['results'][i]['genre']
            categorys = result['results'][i]['category']
            titles = result['results'][i]['name']
            links = result['results'][i]['magnetLink']
            languages = result['results'][i]['language']
            sizes = result['results'][i]['size']

            r = f"<b>Title:</b> <code>{titles}</code>\n<b>Category:</b> <code>{categorys}</code>\n<b>Language:</b> <code>{languages}</code>\n<b>Size:</b> <code>{sizes}</code>\n<b>Genres:</b> <code>{genres}</code>\n<b>Description:</b> {descriptions}\n<b>Magnet Link:</b> <code>{links}</code><br>"
            results.append(r)

        all_results_content = '<br>'.join(results)

        link_results = await telegraph(title="Search Results", user_name=message.from_user.first_name, content=all_results_content)

        if coverImage_url is not None:
            coverImage = requests.get(url=coverImage_url).content
            async with aiofiles.open('coverImage.jpg', mode='wb') as f:
                await f.write(coverImage)

            await message.delete()
            await client.send_media_group(
                chat_id,
                [
                    InputMediaPhoto('coverImage.jpg', caption=f"<b>Title:</b> <code>{title}</code>\n<b>Category:</b> <code>{category}</code>\n<b>Language:</b> <code>{language}</code>\n<b>Size:</b> <code>{size}</code>\n<b>Genres:</b> <code>{genre}</code>\n<b>Description:</b> {description}\n<b>Magnet Link:</b> <a href='{link_result}'>Click Here</a>\n<b>More Results:</b> <a href='{link_results}'>Click Here</a>")
                ])
        else:
            await message.edit_text(f"<b>Title:</b> <code>{title}</code>\n<b>Category:</b> <code>{category}</code>\n<b>Language:</b> <code>{language}</code>\n<b>Size:</b> <code>{size}</code>\n<b>Genres:</b> <code>{genre}</code>\n<b>Description:</b> {description}\n<b>Magnet Link:</b> <a href='{link_result}'>Click Here</a>\n<b>More Results:</b> <a href='{link_results}'>Click Here</a>", disable_web_page_preview=True)


    except MediaCaptionTooLong:
        description = description[:850]
        await message.delete()
        await client.send_media_group(
            chat_id,
            [
                 InputMediaPhoto('coverImage.jpg', caption=f"<b>Title:</b> <code>{title}</code>\n<b>Category:</b> <code>{category}</code>\n<b>Language:</b> <code>{language}</code>\n<b>Size:</b> <code>{size}</code>\n<b>Genres:</b> <code>{genre}</code>\n<b>Description:</b> {description}\n<b>Magnet Link:</b> <a href='{link_result}'>Click Here</a>")
            ])

    except MessageTooLong:
        description = description[:150]
        await message.edit_text(f"<b>Title:</b> <code>{title}</code>\n<b>Category:</b> <code>{category}</code>\n<b>Language:</b> <code>{language}</code>\n<b>Size:</b> <code>{size}</code>\n<b>Genres:</b> <code>{genre}</code>\n<b>Description:</b> {description}\n<b>Magnet Link:</b> <a href='{link_result}'>Click Here</a>", disable_web_page_preview=True)

    except Exception as e:
        await message.edit_text(format_exc(e))
    finally:
        if os.path.exists('coverImage.jpg'):
            os.remove('coverImage.jpg')

@Client.on_message(filters.command("tts", prefix) & filters.me)
async def tts(client: Client, message: Message):
    characters = await voice_characters()
    await message.edit_text("<code>Please Wait...</code>")
    try:
        if len(message.command) > 2:
         character, prompt = message.text.split(maxsplit=2)[1:]
         if character not in characters:
          await message.edit_text(f"<b>Usage: </b><code>{prefix}tts [character]* [text/reply to text]*</code>\n <b>Available Characters:</b> <blockquote>{characters}</blockquote>")
          return

        elif message.reply_to_message and len(message.command) > 1:
         character = message.text.split(maxsplit=1)[1]
         if character in characters:
            prompt = message.reply_to_message.text
         else:
          await message.edit_text(f"<b>Usage: </b><code>{prefix}tts [character]* [text/reply to text]*</code>\n <b>Available Characters:</b> <blockquote>{characters}</blockquote>")
          return

        else:
         await message.edit_text(
            f"<b>Usage: </b><code>{prefix}tts [character]* [text/reply to text]*</code>\n <b>Available Characters:</b> <blockquote>{characters}</blockquote>"
        )
         return

        data = {
            "text": prompt,
            "character": character
            }
        response = requests.post(url=f"{url}/speech", headers=headers, json=data)
        if response.status_code != 200:
            await message.edit_text("Something went wrong")
            return

        result = response.json()
        audio_data = result['audio']
        audio_data = base64.b64decode(audio_data)
        async with aiofiles.open(f'{prompt}.mp3', mode='wb') as f:
            await f.write(audio_data)

        await message.delete()
        await client.send_audio(chat_id=message.chat.id, audio=f'{prompt}.mp3', caption=f"<b>Characters:</b> <code>{character}</code>\n<b>Prompt:</b> <code>{prompt}</code>")

    except KeyError:
        try:
            error = result['error']
            await message.edit_text(error)
        except KeyError:
            await message.edit_text(f"<b>Usage: </b><code>{prefix}tts [character]* [text/reply to text]*</code>\n <b>Available Characters:</b> <blockquote>{characters}</blockquote>")
    except Exception as e:
        await message.edit_text(format_exc(e))
    finally:
        if os.path.exists(f'{prompt}.mp3'):
            os.remove(f'{prompt}.mp3')


modules_help["safone"] = {
    "app": "Search for an app on Play Store",
    "tsearch": "Search Torrent",
    "tts [character]* [text/reply to text]*": "Convert Text to Speech"
}
