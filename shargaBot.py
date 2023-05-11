from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from core.utils.notifier import main_msg_updater
from core.middlwares.settigns import appSettings
from core.middlwares.middleware import (
    DispatcherMiddleware,
    SchedulerMiddleware
)
from core.handlers.home import (
    register_handlers_home,
    register_callback_handlers_home,
)
from core.handlers.user import (
    register_message_handlers_user,
    register_callback_handler_user
)
from core.handlers.changers import (
    register_message_handlers_changer,
    register_callback_handler_changer
)
from create_bot import scheduler, storage
import asyncio
import logging
import jsonpickle



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - [%(levelname)s] - %(name)s - "
            "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s"
)


async def updater_job():
    job_list: list = scheduler.get_jobs()
    job_id_list: list = [job.id for job in job_list]
    main_msg_updater_id = 'main_msg_updater'

    if main_msg_updater_id not in job_id_list:

        scheduler.add_job(
            main_msg_updater,
            'cron',
            day='1-7',
            hour='2, 6',
            id=main_msg_updater_id,
        )



async def register_middleware(dp: Dispatcher):
    
    dp.update.middleware.register(SchedulerMiddleware(scheduler))
    dp.update.middleware.register(DispatcherMiddleware(dp))



async def register_handlers(dp: Dispatcher):

    await register_message_handlers_user(dp)
    await register_callback_handler_user(dp)
    await register_message_handlers_changer(dp)
    await register_callback_handler_changer(dp)
    await register_handlers_home(dp)
    await register_callback_handlers_home(dp)



async def main():
    
    bot = Bot(
        token = appSettings.botSetting.botToken,
        parse_mode=ParseMode.HTML,
    )
    dp = Dispatcher(storage=storage)

    await register_middleware(dp)
    await register_handlers(dp)

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
    asyncio.run(main())
