from core.keyboards import changer_kb
from core.utils import msg_maker
from core.utils.bot_fsm import FSMSteps
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message
from core.middlwares.routes import r    # Dataclass whith all api routes
from core.api_actions.bot_api import SimpleAPI
from core.utils import msg_var as msg
from core.keyboards import home_kb
from create_bot import bot, dp, scheduler
import logging




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

    data: dict = await state.get_data()
    current_state = await state.get_state()

    mainMsg: Message = data.get('mainMsg')
    uncompleted_transfers: dict = data.get('uncompleted_transfers')

    if uncompleted_transfers and \
        current_state == FSMSteps.STUFF_INIT_STATE:

        try:
            await bot.delete_message(
                mainMsg.chat.id,
                mainMsg.message_id
            )
        except:
            pass

        alertMsg: Message = await bot.send_message(
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

        changer_notifier_id = f'changer_notifier-{changer_id}'
        scheduler.remove_job(changer_notifier_id)



async def transfers_getter_changer(changer_id: int):
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
        'isCompleted': False,
        'changerAccepted': False
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
        changer_notifier_id = f'changer_notifier-{changer_id}'
        job_list: list = scheduler.get_jobs()
        job_id_list: list = [job.id for job in job_list]

        if changer_notifier_id not in job_id_list:

            scheduler.add_job(
                changer_notifier,
                'interval',
                minutes = 2,
                id = changer_notifier_id,
                kwargs={
                    'changer_id': changer_id,
                }
            )



# async def user_notifier(user_id: int):
#     '''
#     '''
#     state: FSMContext = FSMContext(
#         bot=bot,
#         storage=dp.storage,
#         key=StorageKey(
#             chat_id=user_id,
#             user_id=user_id,  
#             bot_id=bot.id
#         )
#     )

#     data: dict = await state.get_data()
#     current_state = await state.get_state()

#     mainMsg: Message = data.get('mainMsg')
#     user_events: dict = data.get('user_events')

#     if user_events and \
#         current_state == FSMSteps.USER_INIT_STATE:

#         try:
#             await bot.delete_message(
#                 mainMsg.chat.id,
#                 mainMsg.message_id
#             )
#         except:
#             pass

#         alertMsg: Message = await bot.send_message(
#             mainMsg.chat.id,
#             text= await msg_maker.start_message(user_id),
#             reply_markup= await home_kb.user_home_inline_button(user_id)
#         )
#         await state.update_data(mainMsg = alertMsg)
        # scheduler.remove_job(f'user_notifier-{user_id}')



async def transfers_getter_user(user_id: int):
    '''
    '''
    state: FSMContext = FSMContext(
        bot=bot,
        storage=dp.storage,
        key=StorageKey(
            chat_id=user_id,
            user_id=user_id,  
            bot_id=bot.id
        )
    )
    params = {
        'user': user_id,
        'claims': False,
        'isCompleted': False,
        'changerAccepted': True
    }
    response = await SimpleAPI.get(
        r.userRoutes.transactions,
        params=params
    )
    new_events: dict = response.json()
    data: dict = await state.get_data()
    user_events: dict = data.get('user_events')
    current_state = await state.get_state()
    mainMsg: Message = data.get('mainMsg')

    if user_events != new_events and\
        new_events:

        await state.update_data(
            user_events = new_events
        )

        if current_state == FSMSteps.USER_INIT_STATE:
            try:
                await bot.delete_message(
                    mainMsg.chat.id,
                    mainMsg.message_id
                )
            except:
                pass

            alertMsg: Message = await bot.send_message(
                mainMsg.chat.id,
                text= await msg_maker.start_message(user_id),
                reply_markup= await home_kb.user_home_inline_button(user_id)
            )
            await state.update_data(mainMsg = alertMsg)

    elif not new_events:

        params = {
            'user': user_id,
            'claims': False,
            'isCompleted': False,
            'changerAccepted': False
        }
        response = await SimpleAPI.get(
            r.userRoutes.transactions,
            params=params
        )

        if not response.json():

            scheduler.remove_job(f'user_getter-{user_id}')

        # notifier_id = f'user_notifier-{user_id}'

        # scheduler.add_job(
        #     user_notifier,
        #     'interval',
        #     minutes=1,
        #     id = notifier_id,
        #     kwargs = {
        #         'user_id': user_id
        #     }
        # )












async def user_notifier_old(user_id: int):
    '''
    '''
    state: FSMContext = FSMContext(
        bot=bot,
        storage=dp.storage,
        key=StorageKey(
            chat_id=user_id,
            user_id=user_id,  
            bot_id=bot.id
        )
    )
    data: dict = await state.get_data()
    user_event: list = data.get('user_event')
    new_user_event: list = data.get('new_user_event')
    mainMsg: Message = data.get('mainMsg')

    if new_user_event is not None and\
        len(new_user_event):

        current_state: FSMSteps = await state.get_state()

        for event in new_user_event:
            if event not in user_event:
                user_event.append(event)

        await state.update_data(user_event = user_event)

        if current_state == FSMSteps.USER_INIT_STATE:

            await bot.delete_message(
                mainMsg.chat.id,
                mainMsg.message_id
            )
            alertMsg = bot.send_message(
                user_id,
                text = msg.start_message,
                reply_markup = await home_kb.user_home_inline_button(user_id)
            )
            await state.update_data(mainMsg = alertMsg)



async def changer_notifier_old(changer_id: int):
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




async def changer_transfer_cheker(changer_id: int):
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