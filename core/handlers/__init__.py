import logging
from aiogram import Dispatcher

from .changers import setup_changers_handlers


async def setup_handlers(dp: Dispatcher):
    await setup_changers_handlers(dp)
    logging.info('all handlers are installed')