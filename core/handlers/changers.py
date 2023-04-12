from datetime import datetime
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.types.callback_query import CallbackQuery
from aiogram.types import Message
from aiogram import F
from create_bot import bot, dp
from core.middlwares.routes import r    # Dataclass whith all api routes
from core.utils import msg_maker, msg_var
from core.api_actions.bot_api import SimpleAPI
from core.utils.bot_fsm import FSMSteps
from core.utils import msg_var as msg
from core.keyboards import changer_kb
from core.keyboards import user_kb
from core.keyboards.callbackdata import (
    UserProofActions,
)


async def accept_or_decline_user_transfer(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: UserProofActions):
    '''
    '''
    response = await SimpleAPI.getDetails(
        r.changerRoutes.transactions,
        callback_data.transferId
    )
    transfer = response.json()
    await state.update_data(transfer = transfer)

    if callback_data.action == 'accept':

        patchData = {
            'changerAcceptDate': datetime.now()
        }

        await bot.send_message(
            transfer['user'],
            text= await msg_maker.accept_user_transfer2()
        )
        await bot.send_message(
            call.from_user.id,
            text= await msg_maker.accept_changer_transfer(transfer),
        )
        await SimpleAPI.patch(
            r.changerRoutes.transactions,
            transfer['id'],
            data=patchData
        )
        await state.set_state(FSMSteps.GET_CHANGER_PROOF)

    elif callback_data.action == 'decline':
        
        await bot.send_message(
            transfer['user'],
            text= await msg_maker.decline_user_transfer()

        )


    elif callback_data.action == 'admin':
        await bot.send_message(
            call.from_user.id,
            text= await msg_maker.contact_to_admin()
        )






async def register_message_handlers_user():
    '''Registry message handlers there.
    '''
    ...


async def register_callback_handler_user():
    '''Register callback_querry handlers there.
    '''
    dp.callback_query.register(
        accept_or_decline_user_transfer,
        UserProofActions.filter(),
        FSMSteps.CHANGER_INIT_STATE
    )

