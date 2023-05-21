from datetime import datetime
from typing import Dict, Any, Callable, Awaitable
from aiogram import BaseMiddleware, Bot, Dispatcher
from aiogram.types.base import TelegramObject
from aiogram.types import Update
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from apscheduler_di import ContextSchedulerDecorator



class InstanceContextMiddleware(BaseMiddleware):

    def __init__(
        self,
        dp: Dispatcher,
        scheduler: ContextSchedulerDecorator
    ):
        super().__init__()
        self._scheduler = scheduler
        self._dp = dp

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data:Dict[str, Any]
        ):
        data["apscheduler"] = self._scheduler
        data["dp"] = self._dp
        return await handler(event, data)
    


class LastActionMiddleware(BaseMiddleware):

    def __init__(self, bot: Bot, dp: Dispatcher):
        super().__init__()
        self._bot = bot
        self._dp = dp

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data:Dict[str, Any]
    ):
        if event.message:
            user_id: int = event.message.from_user.id
        elif event.callback_query:
            user_id: int = event.callback_query.from_user.id

        state: FSMContext = FSMContext(
            bot=self._bot,
            storage=self._dp.storage,
            key=StorageKey(
                chat_id=user_id,
                user_id=user_id,
                bot_id=self._bot.id
            )
        )
        update_time: dict[int, datetime] = {}
        await state.update_data(last_action = update_time)
        return await handler(event, data)