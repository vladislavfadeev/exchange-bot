import types
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.enums.parse_mode import ParseMode
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.middlwares.settigns import appSettings
import os


# bot = Bot(token = os.getenv('TOKEN'))
bot = Bot(
    token = appSettings.botSetting.botToken,
    parse_mode=ParseMode.HTML
)
dp = Dispatcher()
scheduler = AsyncIOScheduler()
