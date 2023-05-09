from typing import Dict, Any, Callable, Awaitable
from aiogram import BaseMiddleware, Dispatcher
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
    


class DispatcherMiddleware(BaseMiddleware):

    def __init__(self, dp: Dispatcher):
        super().__init__()
        self._dispatcher = dp

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data:Dict[str, Any]
        ):
        data["dp"] = self._dispatcher
        return await handler(event, data)