import logging

from aiogram import Dispatcher

from .create_offers import setup_create_offer_handlers
from .edit_banks import setup_edit_banks_handlers
from .edit_offers import setup_edit_offers_handlers
from .exchange import setup_exchange_handlers
from .menu import setup_menu_handlers


async def setup_changers_handlers(dp: Dispatcher):
    await setup_create_offer_handlers(dp)
    await setup_edit_banks_handlers(dp)
    await setup_edit_offers_handlers(dp)
    await setup_exchange_handlers(dp)
    await setup_menu_handlers(dp)
    logging.info('changers handlers are installed')