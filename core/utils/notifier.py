from core.keyboards import changer_kb
from core.utils import msg_maker
from core.utils.bot_fsm import FSMSteps
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message
from core.middlwares.routes import r    # Dataclass whith all api routes
from core.api_actions.bot_api import SimpleAPI
from create_bot import bot, dp, scheduler
import logging



async def changer_notifier_db(changer_id):
    '''
    '''
    state: FSMContext = FSMContext(
        bot=bot,
        storage=dp.storage,
        key=StorageKey(
            chat_id=changer_id,
            user_id=changer_id,  
            bot_id=bot.id
        )
    )

    data = await state.get_data()
    current_state = await state.get_state()

    mainMsg = data.get('mainMsg')
    uncompleted_transfers = data.get('uncompleted_transfers')

    if uncompleted_transfers and \
        current_state == FSMSteps.STUFF_INIT_STATE:

        await mainMsg.delete()

        alertMsg = await bot.send_message(
            mainMsg.chat.id,
            text= await msg_maker.staff_welcome(
                uncompleted_transfers
            ),
            reply_markup= await changer_kb.staff_welcome_button(
                uncompleted_transfers
            )
        )
        await state.update_data(mainMsg = alertMsg)



async def changer_notifier(changer_id: int):
    '''
    '''
    state: FSMContext = FSMContext(
        bot=bot,
        storage=dp.storage,
        key=StorageKey(
            chat_id=changer_id,
            user_id=changer_id,  
            bot_id=bot.id
        )
    )

    allowed_state = [
        FSMSteps.STAFF_WAITER,
        FSMSteps.STUFF_INIT_STATE,
        FSMSteps.STUFF_OFFERS_MENU
    ]

    data = await state.get_data()
    current_state = await state.get_state()

    mainMsg: Message = data.get('mainMsg')
    uncompleted_transfers = data.get('uncompleted_transfers')

    if uncompleted_transfers:

        if current_state == FSMSteps.STUFF_INIT_STATE:

            await bot.delete_message(
                mainMsg.chat.id,
                mainMsg.message_id
            )

            alertMsg = await bot.send_message(
                mainMsg.chat.id,
                text= await msg_maker.staff_welcome(
                    uncompleted_transfers
                ),
                reply_markup= await changer_kb.staff_welcome_button(
                    uncompleted_transfers
                )
            )
            await state.update_data(mainMsg = alertMsg)

    elif not uncompleted_transfers:

        notifier_id = data.get('notifier_id')
        scheduler.remove_job(notifier_id)





async def new_transfer_cheker(changer_id: int):
    '''
    '''
    state: FSMContext = FSMContext(
        bot=bot,
        storage=dp.storage,
        key=StorageKey(
            chat_id=changer_id,
            user_id=changer_id,
            bot_id=bot.id
        )
    )
    data: dict = await state.get_data()
    new_transfer: list = data.get('new_transfer')
    uncompleted_transfers: list = data.get('uncompleted_transfers')

    if new_transfer is not None and \
        len(new_transfer):

        for tr in new_transfer:
            if tr not in uncompleted_transfers:
                uncompleted_transfers.append(tr)
        
        notifier_id = f'notifier-{changer_id}'
        job_list = scheduler.get_jobs()
        job_id_list = [job.id for job in job_list]
        print(notifier_id)
        print(job_id_list)

        if notifier_id not in job_id_list:

            scheduler.add_job(
                changer_notifier,
                'interval',
                minutes = 5,
                id = notifier_id,
                kwargs = {
                    'changer_id': changer_id
                }
            )
            await state.update_data(notifier_id = notifier_id)

        await state.update_data(new_transfer = [])
        await state.update_data(
            uncompleted_transfers = uncompleted_transfers
        )



async def transfers_getter(changer_id):
    '''
    '''
    state: FSMContext = FSMContext(
        bot=bot,
        storage=dp.storage,
        key=StorageKey(
            chat_id=changer_id,
            user_id=changer_id,  
            bot_id=bot.id
        )
    )

    params = {
        'changer': changer_id,
        'claims': False,
        'isCompleted': False
    }
    response = await SimpleAPI.get(
        r.changerRoutes.transactions,
        params=params
    )

    new_user_transfers = response.json()
    data = await state.get_data()
    uncompleted_transfers = data.get('uncompleted_transfers')

    if uncompleted_transfers != new_user_transfers:

        await state.update_data(
            uncompleted_transfers = new_user_transfers
        )