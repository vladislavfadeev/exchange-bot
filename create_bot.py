from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler_di import ContextSchedulerDecorator
from core.middlwares.settigns import appSettings
import jsonpickle
import os



storage = RedisStorage.from_url(
    'redis://aio-state:HPV5g8qmHtzQnDxGCRVaIZIVibRLBr9tTmEZ+KMpfc@127.0.0.1:6379/1'
)

jobstores = {
    'default': RedisJobStore(
        host='127.0.0.1',
        port=6379,
        db=2,
        username='apscheduler',
        password='PoGjaaQAAQURoTj1dwKANhiEItQoWBQ7f+SlxJ0kac'
    )
}

# bot = Bot(token = os.getenv('TOKEN'))
bot = Bot(
    token = appSettings.botSetting.botToken,
    parse_mode=ParseMode.HTML,
)

bot.session.json_loads = jsonpickle.loads
bot.session.json_dumps = jsonpickle.dumps

dp = Dispatcher(storage=storage)

scheduler = ContextSchedulerDecorator(AsyncIOScheduler(jobstores=jobstores))

# scheduler.ctx.add_instance(bot, declared_class=Bot)
# scheduler.ctx.add_instance(dp, declared_class=Dispatcher)

