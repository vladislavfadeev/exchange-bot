from aiogram.fsm.storage.redis import RedisStorage
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler_di import ContextSchedulerDecorator
from core.middlwares.settigns import appSettings



storage = RedisStorage.from_url(
    'redis://'
    f'{appSettings.stateStorage.username}:'
    f'{appSettings.stateStorage.passwd}@'
    f'{appSettings.stateStorage.host}:'
    f'{appSettings.stateStorage.port}/'
    f'{appSettings.stateStorage.db}'
)

jobstores = {
    'default': RedisJobStore(
        host=appSettings.jobStorage.host,
        port=appSettings.jobStorage.port,
        db=appSettings.jobStorage.db,
        username=appSettings.jobStorage.username,
        password=appSettings.jobStorage.passwd
    )
}

scheduler = ContextSchedulerDecorator(AsyncIOScheduler(jobstores=jobstores))


