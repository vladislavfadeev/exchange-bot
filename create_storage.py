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

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'basic': {
            'format': '%(asctime)s - [%(levelname)s] - %(name)s - (%(filename)s).%(funcName)s(%(lineno)d) - %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'formatter': 'basic',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'WARNING',
            'formatter': 'basic',
            'filename': f'{appSettings.botSetting.log_dir}sharga_bot.log',
            'maxBytes': 1048576,
            'backupCount': 5,
            'mode': 'a'
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': [
            'console',
            'file'
        ]
    }
}
