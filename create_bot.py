from aiogram import Bot, Dispatcher
from aiogram.types import Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.middlwares.settigns import appSettings
import os


# bot = Bot(token = os.getenv('TOKEN'))
bot = Bot(token = appSettings.botSetting.botToken)
dp = Dispatcher()
scheduler = AsyncIOScheduler()
