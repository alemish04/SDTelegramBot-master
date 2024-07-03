

import requests
import logging

# def post_request_sd_api(endpoint, params, worker,  is_logging=True):
#
#     # url = f"http://127.0.0.1:7861/sdapi/v1/{endpoint}"
#     # url = f"http://194.190.216.163:7860/sdapi/v1/{endpoint}"
#
#     # url = f"http://{worker}/sdapi/v1/{endpoint}"
#     url = f"http://{worker}"
#
#     try:
#         response = requests.post(url, json=params)
#         return response.json()
#     except requests.exceptions.ConnectionError:
#         if is_logging:
#             logging.critical("Ошибка запроса к SD API. Проверь SD")
#         return None


# def post_request_sd_api(worker,  is_logging=True):

# url = f"http://127.0.0.1:7861/sdapi/v1/{endpoint}"
# url = f"http://194.190.216.163:7860/sdapi/v1/{endpoint}"

# url = f"http://{worker}/sdapi/v1/{endpoint}"
# def post_request_sd_api(worker, is_logging=True):
#
#
#     url = f"http://{worker}"
#
#     try:
#         response = requests.post(url)
#         return response.json()
#     except requests.exceptions.ConnectionError:
#         if is_logging:
#             logging.critical("Ошибка запроса к SD API. Проверь SD")
#         return None


import aiohttp
import asyncio


# async def post_request_sd_api(message, user_id, last_prompt, response_list, worker, is_logging=True):
#     if worker == 1:
#         u = "127.0.0.1:8001"
#     elif worker == 0:
#         u = "127.0.0.1:8000"
#
#     url = f"http://{u}"
#
#     try:
#         async with aiohttp.ClientSession() as session:
#             async with session.get(url) as response:
#                 return await response.text
#     except aiohttp.ClientConnectionError:
#         if is_logging:
#             logging.critical("Ошибка запроса к SD API. Проверь SD")
#         return None


async def post_request_sd_api(endpoint, params, worker, is_logging=True):
    if worker == 1:
        u = "127.0.0.1:8001"
    elif worker == 0:
        u = "194.190.216.163:7860"

    url = f"http://{u}/sdapi/v1/{endpoint}"
    # url = f"https://a5054aa2784c5630f4.gradio.live/{endpoint}"


    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=params) as response:
                return await response.json()
    except aiohttp.ClientConnectionError:
        if is_logging:
            logging.critical("Ошибка запроса к SD API. Проверь SD")
        return None



# def get_request_sd_api(endpoint, is_logging=True):
#     # url = f"http://127.0.0.1:7861/sdapi/v1/{endpoint}"
#     url = f"http://194.190.216.163:7860/sdapi/v1/{endpoint}"
#     # url = f"https://a5054aa2784c5630f4.gradio.live/{endpoint}"
#     try:
#         response = requests.get(url)
#         return response
#     except requests.exceptions.ConnectionError:
#         if is_logging:
#             logging.critical("Ошибка запроса к SD API. Проверь SD")
#         return None


async def get_request_sd_api(endpoint, is_logging=True):
    # url = f"http://127.0.0.1:7861/sdapi/v1/{endpoint}"
    url = f"http://194.190.216.163:7860/sdapi/v1/{endpoint}"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()
    except aiohttp.ClientConnectionError:
        if is_logging:
            logging.critical("Ошибка запроса к SD API. Проверь SD")
        return None


async def get_models_sd_api():
    # return await get_request_sd_api("sd-models").json()
    return await get_request_sd_api("sd-models")


async def get_hr_upscaler_sd_api():
    # return await get_request_sd_api("upscalers").json()
    return await get_request_sd_api("upscalers")


async def get_image_seed(image, worker):
    png_payload = {
        "image": "data:image/png;base64," + image
    }
    # image_info = await post_request_sd_api("png-info", png_payload, worker=worker).get('info')
    image_info = await post_request_sd_api("png-info", png_payload, worker=worker)
    image_info=image_info.get('info')

    image_info = image_info.split(', ')
    for j in range(len(image_info) - 1, 0, -1):
        if image_info[j].find("Seed:") != -1:
            return image_info[j][6:]
