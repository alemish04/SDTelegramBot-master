

import asyncio
import logging
from aiogram import executor
import time
from settings.bot_config import is_wait_sd_launch, time_the_next_check_s, launch_sd_at_bot_started
from loader import dp, bot
import handlers, middlewares

from utils.db_services import db_service
from utils.db_services.db_service import admins_and_users_initialization_in_db
from utils.misc_func import is_sd_launched, check_sd_path, start_sd_process, users, create_workers
from utils.notifier import users_and_admins_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    await db_service.db_create_table()
    # Устанавливаем дефолтные команды
    await set_default_commands(dispatcher)
    # await asyncio.sleep(4)
    # await admins_and_users_initialization_in_db()
    # Уведомляет про запуск
    await users_and_admins_notify(dispatcher, msg="📢 Бот запущен, введите команду /start для начала генерации...")
    # await add_main()
    # await users()


# from aiogram import Bot, Dispatcher, types
# from aiogram.contrib.fsm_storage.memory import MemoryStorage
# import logging
# from settings import bot_config


# bot = Bot(token=bot_config.BOT_TOKEN, parse_mode=types.ParseMode.HTML)
# storage = MemoryStorage()
# dp = Dispatcher(bot, storage=storage)

logging.basicConfig(level=logging.INFO)


# async def handle_messages(queue):
#     while True:
#         message = await queue.get()
#
#         # Обработка сообщения
#         # ...
#
#         # Отправка результата пользователю
#         await bot.send_message(chat_id=message.chat.id, text="Результат обработки")
#
#         queue.task_done()

async def start(x):
    await db_service.db_create_table()
    # Устанавливаем дефолтные команды
    await set_default_commands(dp)
    # await asyncio.sleep(4)
    # await admins_and_users_initialization_in_db()
    # Уведомляет про запуск
    await users_and_admins_notify(dp, msg="📢 Бот запущен, введите команду /start для начала генерации...")
    asyncio.create_task(users())
    asyncio.create_task(create_workers())
#
# async def start_bot(dp):


# @dp.message_handler(content_types=types.ContentTypes.TEXT)
# async def handle_message(message: types.Message):
#     # Помещаем сообщение в очередь для последующей обработки
#     await queue.put(message)
#     print(queue)

# async def on_startup(dp):
#     await executor.start_polling(dp, on_startup=start)
#     # await dp.start_polling()
#
#     # await add_main()
#
# await on_startup(dp)


# async def run():
#     # token = "YOUR_BOT_TOKEN"
#
#     # Создаем очередь сообщений
#
#
#     # Запускаем бота
#     await asyncio.gather(
#         dp.start_polling(),
#         users()
#     )

# async def run():
#     await asyncio.gather(executor.start_polling(dp, on_startup=on_startup), users())


if __name__ == '__main__':
    # start_time = time.time()
    # loop = asyncio.get_event_loop()
    # loop.create_task(users())
    # # if is_sd_launched():
    # asyncio.run(run())
    #
    executor.start_polling(dp, skip_updates=True, on_startup=start)

    # elif launch_sd_at_bot_started and check_sd_path():
    #     start_sd_process()
    #     logging.info("Начинаю запуск SD...")
    #
    #     while True:
    #         if is_sd_launched():
    #             current_time = time.time()
    #             logging.info(f"SD запущена - {int(current_time - start_time)}s.")
    #
    #             executor.start_polling(dp, on_startup=on_startup)
    #             break
    #         time.sleep(time_the_next_check_s)
    #
    # elif is_wait_sd_launch:
    #     count = 1
    #
    #     while True:
    #         if is_sd_launched():
    #             current_time = time.time()
    #             logging.info(f"SD запущена - {int(current_time - start_time)}s.")
    #
    #             executor.start_polling(dp, on_startup=on_startup)
    #             break
    #         logging.warning(f"LAUNCH ATTEMPT {count}, STABLE DIFFUSION NOT LAUNCHED!")
    #         count += 1
    #         time.sleep(time_the_next_check_s)
    #
    # elif not is_wait_sd_launch:
    #     logging.warning("SD не запущена!")
