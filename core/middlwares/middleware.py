from typing import Dict, Any, Callable, Awaitable
from aiogram import BaseMiddleware
from aiogram.types.base import TelegramObject
from apscheduler_di import ContextSchedulerDecorator



class SchedulerMiddleware(BaseMiddleware):

    def __init__(self,scheduler: ContextSchedulerDecorator):
        super().__init__()
        self._scheduler = scheduler

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data:Dict[str, Any]
        ):
        data["apscheduler"] = self._scheduler
        return await handler(event, data)
    