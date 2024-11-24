# Copyright 2023 Qewertyy, MIT License
import logging
import asyncio
from lexica import AsyncClient, Client


def ImageModels():
    models = Client().models["models"]["image"]
    dict_models = {}
    for model in models:
        model_id = model["id"]
        model_name = model["name"]
        dict_models[model_name] = model_id
    return dict_models


async def ImageGeneration(model, prompt):
    try:
        output = await AsyncClient().generate(model, prompt, "")
        if output["code"] != 1:
            return 2
        if output["code"] == 69:
            return output["code"]
        task_id, request_id = output["task_id"], output["request_id"]
        await asyncio.sleep(20)
        tries = 0
        image_url = None
        resp = await AsyncClient().getImages(task_id, request_id)
        while True:
            if resp["code"] == 2:
                image_url = resp["img_urls"]
                break
            if tries > 15:
                break
            await asyncio.sleep(5)
            resp = await AsyncClient().getImages(task_id, request_id)
            tries += 1
            continue
        return image_url
    except Exception as e:
        logging.warning(e)
    finally:
        await AsyncClient().close()


async def UpscaleImages(image: bytes) -> str:
    content = await AsyncClient().upscale(image)
    await AsyncClient().close()
    upscaled_file_path = "upscaled.png"
    with open(upscaled_file_path, "wb") as output_file:
        output_file.write(content)
    return upscaled_file_path
