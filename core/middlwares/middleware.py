from typing import Dict, Any
from aiogram import BaseMiddleware
from aiogram.types.base import TelegramObject
from apscheduler.schedulers.async_ import AsyncScheduler



class SchedulerMiddleware(BaseMiddleware):

    def __init__(self, scheduler: AsyncScheduler):
        super().__init__()
        self._scheduler = scheduler

    async def pre_process(self, obj: TelegramObject, data: Dict[str, Any], *args: Any):
        data["scheduler"] = self._scheduler