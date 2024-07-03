


from aiogram import types
from aiogram.dispatcher.filters import CommandHelp

from loader import dp


@dp.message_handler(CommandHelp(), state='*')
async def bot_help(message: types.Message):
    text = ("Список команд: ",
            "/start - Начать генерировать",
            "/settings - Настройки генерации",
            "/help - Справка",
            "Поблагодарить автора:",
            "Qiwi: <code>+79803778005</code>",
            "Карта МИР: <code>2200 1509 9863 3876</code>",)

    await message.answer("\n".join(text))
