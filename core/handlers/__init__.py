import logging
from aiogram import Dispatcher

from .changers import setup_changers_handlers
from .users import setup_users_handlers
from .home import setup_home_handlers


async def setup_handlers(dp: Dispatcher):
    await setup_changers_handlers(dp)
    await setup_users_handlers(dp)
    await setup_home_handlers(dp)
    logging.info('all handlers are installed')