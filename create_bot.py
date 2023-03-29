from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os
import ENV


storage = MemoryStorage()

# bot = Bot(token = os.getenv('TOKEN'))
bot = Bot(token = ENV.token)
dp = Dispatcher(bot, storage=storage)