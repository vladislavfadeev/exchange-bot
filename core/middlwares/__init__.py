import logging
from aiogram import Bot, Dispatcher
from apscheduler_di import ContextSchedulerDecorator

from .middleware import InstanceContextMiddleware, LastActionMiddleware


async def setup_middleware(
        bot: Bot,
        dp: Dispatcher,
        scheduler: ContextSchedulerDecorator
    ):
    dp.update.middleware.register(InstanceContextMiddleware(dp, scheduler))
    dp.update.middleware.register(LastActionMiddleware(bot, dp))
    logging.info('middlewares are installed')