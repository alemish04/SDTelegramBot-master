

import asyncio
import base64
import copy
import datetime
import io
import logging
import os
import threading
import time

import psutil as psutil

from aiogram import types, Bot
from keyboards.inline import inline_menu
from loader import dp
from settings.bot_config import sd_path, send_photo_without_compression
from settings.sd_config import save_files, output_folder
from utils.db_services import db_service
from utils.notifier import admin_notify, users_and_admins_notify
from utils.progress_bar import progress_bar
from utils.sd_api import api_service
from utils.sd_api.api_service import get_request_sd_api

last_seed = ""
is_busy = False


# async def generate_image(tg_id: int, last_prompt, seed, worker):
#     db_result = await db_service.db_get_sd_settings(tg_id)
#     params = {
#         "prompt": last_prompt,
#         "negative_prompt": db_result[4],
#         "styles": db_result[2].split('&'),
#         "cfg_scale": db_result[8],
#         "steps": db_result[6],
#         "width": int(db_result[7].split('x')[0]),
#         "height": int(db_result[7].split('x')[1]),
#         "sampler_name": db_result[5],
#         "batch_size": db_result[9],
#         "save_images": 'true' if save_files else 'false',
#         "seed": seed,
#         "enable_hr": db_result[10],
#         "hr_upscaler": db_result[11],
#         "hr_second_pass_steps": db_result[12],
#         "denoising_strength": db_result[13],
#         "hr_scale": db_result[14],
#     }
#     if save_files:
#         api_service.post_request_sd_api("options", {"outdir_txt2img_samples": f"{output_folder}"})
#     response = api_service.post_request_sd_api("txt2img", params, worker)
#     return response


async def change_sd_model(tg_id: int, worker):
    # sd_model = await api_service.get_request_sd_api("options").json()['sd_model_checkpoint']
    sd_model = await api_service.get_request_sd_api("options")
    sd_model = sd_model['sd_model_checkpoint']
    db_model = await db_service.db_get_sd_setting(tg_id, "sd_model")
    if db_model != sd_model:
        params = {
            "sd_model_checkpoint": db_model
        }
        await api_service.post_request_sd_api("options", params, worker)
        return db_model
    else:
        return db_model


async def is_sd_launched():
    response =await api_service.get_request_sd_api("options", is_logging=False)
    if response is None:
        return False
    else:
        return True


async def change_style_db(tg_id: int, entered_style):
    db_styles_list = await db_service.db_get_sd_setting(tg_id, 'sd_style')
    if db_styles_list == "":
        await db_service.db_set_sd_settings(tg_id, 'sd_style', entered_style)
        return True
    else:
        result = db_styles_list.split('&')
        if entered_style not in result:
            result = db_styles_list + '&' + entered_style
            await db_service.db_set_sd_settings(tg_id, 'sd_style', result)
            return True
        else:
            result.remove(entered_style)
            await db_service.db_set_sd_settings(tg_id, 'sd_style', '&'.join(result))
            return False


async def change_lora_db(tg_id: int, entered_lora):
    db_lora_list = await db_service.db_get_sd_setting(tg_id, 'sd_lora')
    if db_lora_list == "":
        await db_service.db_set_sd_settings(tg_id, 'sd_lora', entered_lora)
        return True
    else:
        result = db_lora_list.split('&')
        if entered_lora not in result:
            result = db_lora_list + '&' + entered_lora
            await db_service.db_set_sd_settings(tg_id, 'sd_lora', result)
            return True
        else:
            result.remove(entered_lora)
            await db_service.db_set_sd_settings(tg_id, 'sd_lora', '&'.join(result))
            return False


async def user_samplers(api_samplers, hide_user_samplers):
    return [x for x in api_samplers if x['name'] not in hide_user_samplers]


async def reformat_lora(lora):
    if lora == "":
        return ""
    else:
        lora_list = lora.split('&')
        result = (f'<lora:{x}:0.7>' for x in lora_list)
        return ', '.join(result) + ", "


async def kill_sd_process():
    for proc in psutil.process_iter():
        if proc.name() == "python.exe" and proc.cmdline()[1] == "launch.py":
            pid = proc.pid
            os.system(f"taskkill /Pid {pid} /f")
            await asyncio.sleep(1)
    for proc in psutil.process_iter():
        if proc.name() == "cmd.exe" and "webui-user.bat" in proc.cmdline():
            pid = proc.pid
            os.system(f"taskkill /Pid {pid} /f")
            await asyncio.sleep(1)


def start_sd_process():
    os.system(f"cd {sd_path} && start webui-user.bat")


def check_sd_path():
    if sd_path != "":
        try:
            list_files = os.listdir(sd_path)
            if "webui-user.bat" in list_files:
                return True
            else:
                logging.warning("Не найден файл webui-user.bat, проверь путь в config.")
                return False
        except FileNotFoundError:
            logging.warning("Путь к папке SD не верный, проверь путь в bot_config.py")
            return False
    else:
        logging.warning("Путь к папке SD не указан в файле bot_config.py")
        return False


async def restart_sd():
    await kill_sd_process()
    start_sd_process()


def generate_image_callback(user_id, prompt, seed, response, worker):
    loop = asyncio.run(generate_image(tg_id=user_id, last_prompt=prompt, seed=seed, worker=worker))
    # loop = generate_image(tg_id=user_id, last_prompt=prompt, seed=seed, worker=worker)
    # loop = await generate_image(tg_id=user_id, last_prompt=prompt, seed=seed, worker=worker)
    response.append(loop)
    return loop


def change_model_callback(user_id, response):
    loop = asyncio.run(change_sd_model(user_id))
    response.append(loop)
    return loop


# workers_free=["194.190.216.164", "194.190.216.163"]
# workers_free=asyncio.LifoQueue(maxsize=10)
# async def add_main():
#     # await workers_free.put("194.190.216.164")
#     # await workers_free.put("194.190.216.163")
#     await workers_free.put("127.0.0.1:8000")
#     await workers_free.put("127.0.0.1:8001")

# queue_users = asyncio.LifoQueue(maxsize=1000)
queue = asyncio.LifoQueue(maxsize=1000)
messages_to_generate = asyncio.LifoQueue(maxsize=1000)


async def add(message, user_id, last_prompt, response_list):
    print("add")
    global queue, messages_to_generate
    # if user_id not in queue_users:
    await messages_to_generate.put([message, user_id, last_prompt, response_list])
    # await queue_users.put(user_id)
    # print(queue)

    # if not queue.empty() and is_busy == True:
    #     await message.answer(f"ждите, номер в очереди : {queue.qsize() + 1}")

    # await message.answer("вы уже стоите в очереди на генерацию, не мухлевать(((")


# async def check_queue():
#     global queue, workers_free
#     # if not queue.empty() and is_busy == False:
#     print(queue.qsize(), workers_free)
#     if not queue.empty() and not workers_free.empty():
#         # print("_____длина очереди_____________________", queue.qsize())
#         a, b, c, d = await queue.get()
#  #       await queue_users.get()
#  #        queue.task_done()
#         # print(a, b, c, d)
#         # print("_____длина очереди теперь_____________________", queue.qsize())
#         worker = await workers_free.get()
#         await send_photo(a, b, c, d, worker)

async def users():
    global task_queue, queue
    count = 1
    while True:

        if not messages_to_generate.empty():
            temp = await messages_to_generate.get()
            await queue.put(temp)
            print("Добавлено в очередь")
            await asyncio.sleep(2)
        else:
            # print("пусто")
            await asyncio.sleep(2)

        # await asyncio.sleep(random.uniform(5, 5))
        # task = f"Задача {count}"
        # count += 1
        # print(f"Добавлена новая задача: {task}")
        #
        # await task_queue.put(task)


async def worker(worker_id):
    print(f"размер очереди - {queue.qsize()}")
    # print("worker")
    while True:
        # Получение задачи из очереди
        a, b, c, d = await queue.get()
        # await a.bot.delete_message(a.chat.id, a.message_id)
        await a.answer(f"Вами занимается воркер {worker_id}")
        print(f"Воркер {worker_id} начал выполнение задачи: {a, b, c, d}")

        # answer = await api_service.post_request_sd_api(a, b, c, d, worker_id) # рабочая версия

        # await a.bot.delete_message(a.chat.id, a.message_id)

        await send_photo(a, b, c, d, worker_id)

        await a.answer("Ответ получен%%%")
        # print(f"ответ сервера - {answer}")
        print(f"Воркер {worker_id} Закончил выполнение задачи: {a, b, c, d}")
        queue.task_done()
        print(queue.qsize())


async def create_workers():
    print("main")
    num_workers = 1
    workers = [asyncio.create_task(worker(i)) for i in range(num_workers)]  # launch workers

    # Запуск генератора задач
    task_generator_task = asyncio.create_task(users())  # check queue

    # progress_bar_laucher = [asyncio.create_task(progress_bar(i)) for i in range(num_workers)]   #
    # Ожидание завершения всех задач
    # await asyncio.gather(task_generator_task)
    # await task_queue.join()  # Ожидание завершения всех задач в очереди
    #
    # # Остановка воркеров
    # for worker_task in workers:
    #     worker_task.cancel()


# async def pool():
#     while True:
#         await asyncio.sleep(1)
#         print(queue.qsize())
#         await check_queue()

async def generate_image(tg_id: int, last_prompt, seed, worker):
    db_result = await db_service.db_get_sd_settings(tg_id)
    params = {
        "prompt": last_prompt,
        "negative_prompt": db_result[4],
        "styles": db_result[2].split('&'),
        "cfg_scale": db_result[8],
        "steps": db_result[6],
        "width": int(db_result[7].split('x')[0]),
        "height": int(db_result[7].split('x')[1]),
        "sampler_name": db_result[5],
        "batch_size": db_result[9],
        "save_images": 'true' if save_files else 'false',
        "seed": seed,
        "enable_hr": db_result[10],
        "hr_upscaler": db_result[11],
        "hr_second_pass_steps": db_result[12],
        "denoising_strength": db_result[13],
        "hr_scale": db_result[14],
    }
    if save_files:
        await api_service.post_request_sd_api("options", {"outdir_txt2img_samples": f"{output_folder}"})
    response = await api_service.post_request_sd_api("txt2img", params, worker)
    return response


# def generate_image_callback(user_id, prompt, seed, response, worker):
#     loop = asyncio.run(generate_image(tg_id=user_id, last_prompt=prompt, seed=seed, worker=worker))
#     # loop = generate_image(tg_id=user_id, last_prompt=prompt, seed=seed, worker=worker)
#     # loop = await generate_image(tg_id=user_id, last_prompt=prompt, seed=seed, worker=worker)
#     response.append(loop)
#     return loop

# async def generate_image_callback(user_id, prompt, seed, response, worker):
#     # loop = asyncio.run(generate_image(tg_id=user_id, last_prompt=prompt, seed=seed, worker=worker))
#     # loop = generate_image(tg_id=user_id, last_prompt=prompt, seed=seed, worker=worker)
#     # loop = await generate_image(tg_id=user_id, last_prompt=prompt, seed=seed, worker=worker)
#     loop = await generate_image(tg_id=user_id, last_prompt=prompt, seed=seed, worker=worker)
#     response.append(loop)
#     return loop


async def send_photo(message, user_id, last_prompt, response_list, worker, with_seed=False):
    global last_seed, queue
    # is_busy = True
    # workers_free.remove(worker)
    print(worker, last_prompt)
    # chat_id=user_id
    # message_id=message.message_id
    if with_seed:
        last_prompt = last_seed + "&" + last_prompt
    sd_model = await change_sd_model(user_id, worker)
    lora = await db_service.db_get_sd_setting(user_id, 'sd_lora')
    reform_lora = await reformat_lora(lora)
    seed, prompt = await message_parse(last_prompt)
    # thread_generate_image = threading.Thread(target=generate_image_callback, args=(
    #     user_id, reform_lora + prompt, seed, response_list, worker))

    # ready = await generate_image_callback(user_id, reform_lora + prompt, seed, response_list, worker)
    thread_generate_image = threading.Thread(target=generate_image_callback, 
                                             name=f"{worker}", 
                                             args=( user_id, 
                                                    reform_lora + prompt, 
                                                    seed, 
                                                    response_list, 
                                                    worker))

    thread_generate_image.start()

    chat_id, message_id = await progress_bar(message.chat.id, thread_generate_image)

    thread_generate_image.join()

    style = await db_service.db_get_sd_setting(user_id, 'sd_style')
    style_caption = f"\n<b>Styles: </b><i>{style.replace('&', ', ')}</i>"
    lora_caption = f"\n<b>LoRa: </b><i>{lora.replace('&', ', ')}</i>"
    caption = f"<b>Positive prompt:</b>\n<code>{prompt}</code>\n" \
              f"<b>Model:</b>\n<i>{sd_model}</i>"
    if style != '':
        caption += style_caption
    if lora != '':
        caption += lora_caption

    if response_list[0] is not None and "error" not in response_list[0].keys():
        media = types.MediaGroup()
        if len(response_list[0]['images']) > 1:
            try:
                count = 1
                for i in response_list[0]['images']:
                    image = types.InputFile(io.BytesIO(base64.b64decode(i.split(",", 1)[0])))
                    media.attach_photo(image)
                    image_seed = await api_service.get_image_seed(i)
                    last_seed = image_seed
                    caption += f"\n<b>Seed {count}:</b> <code>{image_seed}</code>"
                    count += 1
                await message.bot.delete_message(chat_id=chat_id, message_id=message_id)
                await message.answer_media_group(media=media)
                await message.answer(caption)
                await message.answer(f"📖 Меню генерации", reply_markup=inline_menu.main_menu)
            except Exception as err:
                await message.answer("Ошибка генерации фото, информация об ошибке уже передана администраторам",
                                     reply_markup=inline_menu.main_menu)
                await admin_notify(dp, msg="[ERROR] Ошибка генерации фото\n" + str(err))
        else:
            for i in response_list[0]['images']:
                image_seed = await api_service.get_image_seed(i, worker)
                image = types.InputFile(io.BytesIO(base64.b64decode(i.split(",", 1)[0])),
                                        filename=f"{prompt}_{image_seed}_{datetime.date.today()}.jpg")

                last_seed = image_seed
                caption += f"\n<b>Seed:</b> <code>{image_seed}</code>"
                await message.bot.delete_message(chat_id=chat_id, message_id=message_id)
                last_image = copy.deepcopy(image)
                await message.answer_photo(photo=image)
                if send_photo_without_compression:
                    await message.answer_document(last_image)
                await message.answer(caption)
                await message.answer(f"📖 Меню генерации", reply_markup=inline_menu.main_menu)
    else:
        await message.answer("Ошибка генерации фото, информация об ошибке уже передана администраторам",
                             reply_markup=inline_menu.main_menu)
        await admin_notify(dp,
                           msg="[ERROR] Ошибка генерации фото\n Ошибка в функции send_photo " + str(
                               response_list[0]))

    response_list.clear()

    # is_busy = False
    # is_busy -= 1
    # await check_queue()


async def restarting_sd(message):
    await message.message.edit_text("⛔️ SD не отвечает...\n🔃 Перезапускаю SD!",
                                    reply_markup=main_menu)
    await restart_sd()
    start_time = time.time()
    while True:
        if await is_sd_launched():
            current_time = time.time()
            logging.info(f"SD запущена - {int(current_time - start_time)}s.")
            await users_and_admins_notify(dp, f"✅ SD запущена - {int(current_time - start_time)}s.")
            break
        await asyncio.sleep(1)


async def message_parse(message):
    if message.find('&') != -1:
        message_list = message.split('&')
        return message_list[0], message_list[1]
    else:
        return -1, message
