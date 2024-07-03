


from aiogram.dispatcher.filters.builtin import CommandStart
from aiogram.types import Message
import asyncio
from keyboards.inline.inline_menu import main_menu
from loader import dp
from settings.bot_config import ADMINS
from states.all_states import SDStates
from utils.db_services import db_service
# from utils.misc_func import pool, add_main


@dp.message_handler(CommandStart())
async def bot_start(message: Message):
    db_users_response = await db_service.db_get_sd_setting(message.from_user.id, 'tg_id')
    if message.from_user.id == db_users_response or message.from_user.id in ADMINS:

        await message.answer(f"🖐 Привет, {message.from_user.full_name}!")
        await message.answer(f"Я генерирую фото по любому тексту...")
        await message.answer(f"📖 Меню генерации", reply_markup=main_menu)
        await SDStates.enter_prompt.set()
        # await asyncio.create_task(main())
        # asyncio.run(main())
        # await main()
        # await pool()


