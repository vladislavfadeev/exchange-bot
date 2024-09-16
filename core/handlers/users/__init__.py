import logging

from aiogram import Dispatcher

from .events import setup_events_handlers
from .exchange import setup_exchande_handlers
from .crypto_exchange import setup_crypto_exchande_handlers



async def setup_users_handlers(dp: Dispatcher):
    await setup_events_handlers(dp)
    await setup_exchande_handlers(dp)
    await setup_crypto_exchande_handlers(dp)
    logging.info('users handlers are installed')