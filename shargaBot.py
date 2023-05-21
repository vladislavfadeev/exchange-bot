import asyncio
import jsonpickle
from logging.config import dictConfig

from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode

from core.handlers import setup_handlers
from core.utils.notifier import main_msg_updater
from core.middlwares.settigns import appSettings
from core.middlwares import setup_middleware
from create_storage import scheduler, storage, LOGGING_CONFIG



async def updater_job():
    job_list: list = scheduler.get_jobs()
    job_id_list: list = [job.id for job in job_list]
    main_msg_updater_id = 'main_msg_updater'

    if main_msg_updater_id not in job_id_list:

        scheduler.add_job(
            main_msg_updater,
            'cron',
            day_of_week= 'mon-sun',
            hour='2, 6',
            id=main_msg_updater_id,
        )


async def main():
    
    bot = Bot(
        token = appSettings.botSetting.botToken,
        parse_mode=ParseMode.HTML,
    )
    dp = Dispatcher(storage=storage)

    await setup_middleware(bot, dp, scheduler)
    await setup_handlers(dp)

    bot.session.json_loads = jsonpickle.loads
    bot.session.json_dumps = jsonpickle.dumps

    scheduler.ctx.add_instance(bot, declared_class=Bot)
    scheduler.ctx.add_instance(dp, declared_class=Dispatcher)
    
    try:
        
        scheduler.start()
        await updater_job()
        await dp.start_polling(bot, skip_updates=True,)
        
    finally:
        # await bot.send_message(
        #     appSettings.botSetting.adminId,
        #     'Bot has been stoped!'
        # )
        await bot.session.close()



if __name__ == '__main__':
    dictConfig(LOGGING_CONFIG)
    asyncio.run(main())
