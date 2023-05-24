import logging
from aiogram import Bot, Dispatcher
from apscheduler_di import ContextSchedulerDecorator

from core.api_actions.bot_api import SimpleAPI

from .middleware import (
    InstanceContextMiddleware,
    LastActionMiddleware
)

async def setup_middleware(
        bot: Bot,
        dp: Dispatcher,
        api_gateway: SimpleAPI,
        scheduler: ContextSchedulerDecorator
    ):
    dp.update.middleware.register(
        InstanceContextMiddleware(
            dp,
            api_gateway,
            scheduler
        )
    )
    dp.update.middleware.register(
        LastActionMiddleware(
            bot,
            dp
        )
    )
    logging.info('middlewares are installed')