from core.middlwares.settigns import appSettings
from core.handlers.home import (
    register_handlers_home,
    register_callback_handlers_home,
)
from core.handlers.user import (
    register_message_handlers_user,
    register_callback_handler_user
)
from core.handlers.changers import (
    register_message_handlers_changer,
    register_callback_handler_changer
)
from create_bot import bot, dp, scheduler
import asyncio
import logging



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - "
            "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
)


async def register_handlers():

    await register_message_handlers_user()
    await register_callback_handler_user()
    await register_message_handlers_changer()
    await register_callback_handler_changer()
    await register_handlers_home()
    await register_callback_handlers_home()


async def start_bot():

    await register_handlers()

    try:
        scheduler.start()
        await dp.start_polling(bot)
    finally:
        # await bot.send_message(
        #     appSettings.botSetting.adminId,
        #     'Bot has been stoped!'
        # )
        await bot.session.close()



if __name__ == '__main__':
    asyncio.run(start_bot())













# from aiogram.utils import executor
# from create_bot import dp
# # from data_base import sqlite_db
# import logging


# logging.basicConfig(level=logging.DEBUG)

# async def on_startup(_):
#     print('Бот в онлайне')
#     # sqlite_db.sql_start()


# from handlers import main, admin, exchange, changers

# main.register_handlers_main(dp)
# admin.register_handlers_admin(dp)
# exchange.register_handlers_exchange(dp)
# changers.register_handlers_exchange(dp)


# executor.start_polling(dp, skip_updates=True, on_startup=on_startup)