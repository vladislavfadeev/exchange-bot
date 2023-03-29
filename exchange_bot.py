from aiogram.utils import executor
from create_bot import dp
# from data_base import sqlite_db
import logging


logging.basicConfig(level=logging.DEBUG)

async def on_startup(_):
    print('Бот в онлайне')
    # sqlite_db.sql_start()


from handlers import main, admin, exchange, changers

main.register_handlers_main(dp)
admin.register_handlers_admin(dp)
exchange.register_handlers_exchange(dp)
changers.register_handlers_exchange(dp)


executor.start_polling(dp, skip_updates=True, on_startup=on_startup)