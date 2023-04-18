from core.keyboards import changer_kb
from core.utils import msg_maker
from core.utils.bot_fsm import FSMSteps
from create_bot import bot, dp, scheduler
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from core.middlwares.routes import r    # Dataclass whith all api routes
from core.api_actions.bot_api import SimpleAPI
import logging



async def changer_notifier(
        state: FSMContext
):
    '''
    '''
    data = await state.get_data()
    current_state = await state.get_state()
    mainMsg = data.get('mainMsg')
    user_transfers = data.get('user_transfers')

    if user_transfers and current_state == FSMSteps.STUFF_INIT_STATE:

        await mainMsg.delete()
        alertMsg = await bot.send_message(
            mainMsg.chat.id,
            text= await msg_maker.staff_welcome(
                user_transfers
            ),
            reply_markup= await changer_kb.staff_welcome_button(
                user_transfers
            )
        )
        await state.update_data(mainMsg = alertMsg)



async def get_new_transfers(
    changer_id,
    state: FSMContext
):
    '''
    '''
    params = {
        'changer': changer_id,
        'changerSendMoneyDate': None,
        'claims': False,
        'isCompleted': False
    }
    response = await SimpleAPI.get(
        r.changerRoutes.transactions,
        params=params
    )

    new_user_transfers = response.json()
    data = await state.get_data()
    user_transfers = data.get('user_transfers')

    if user_transfers != new_user_transfers:

        await state.update_data(
            user_transfers = new_user_transfers
        )