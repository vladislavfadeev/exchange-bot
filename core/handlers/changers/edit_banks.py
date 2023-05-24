from types import NoneType
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types.callback_query import CallbackQuery
from aiogram import F, Bot, Dispatcher

from core.middlwares.routes import r    # Dataclass whith all api routes
from core.utils import msg_maker
from core.api_actions.bot_api import SimpleAPI
from core.utils.notifier import alert_message_sender
from core.utils.bot_fsm import FSMSteps
from core.utils import msg_var as msg
from core.keyboards import (
    changer_kb,
)
from core.keyboards.callbackdata import (
    StaffEditData,
    StaffOfficeData,
)



async def staff_show_banks_account(                                # Доделать после проработки проверки!!!!!
        call: CallbackQuery,
        state: FSMContext,
        callback_data: StaffOfficeData,
        api_gateway: SimpleAPI,
        bot: Bot
):
    ''' 
    '''
    await state.set_state(FSMSteps.STUFF_ACCOUNTS)
    data: dict = await state.get_data()
    message_list: list | NoneType = data.get('messageList')
    changer_id: int = call.from_user.id
    params = {
        'owner': changer_id,
        'isDeleted': False
    }
    response: dict = await api_gateway.get(
        path=r.changerRoutes.banksCheker,
        params=params,
        exp_code=[200]
    )
    exception: bool = response.get('exception')
    if not exception:
        if message_list:
            try:
                for i in message_list:
                    i: Message
                    await bot.delete_message(
                        i.chat.id,
                        i.message_id
                    )
            except:
                pass
        banks_list = response.get('response')
        if banks_list:
            try:
                await call.message.delete()
            except:
                pass
            await state.update_data(staff_editable_banks = banks_list)
            messageList = []
            for bank in banks_list:
                self_msg = await bot.send_message(
                    call.from_user.id,
                    text = await msg_maker.staff_show_editable_banks(
                        bank
                    ),
                    reply_markup = await changer_kb.staff_edit_banks_accounts(
                        bank['id'],
                        bank['isActive'],
                    )
                )
                messageList.append(self_msg)
            sep_msg = await bot.send_message(
                call.from_user.id,
                text = msg.separator,
                reply_markup = await changer_kb.sfuff_cancel_button()
            )
            messageList.append(sep_msg)
            await state.update_data(messageList = messageList)
        else:
            await call.message.edit_text(
                text = msg.staff_show_banks_account,
                reply_markup = await changer_kb.staff_zero_banks_buttons()
            )
    else:
         await alert_message_sender(bot, call.from_user.id)



async def staff_bank_account_setter(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: StaffOfficeData,
        api_gateway: SimpleAPI,
        bot: Bot  
):
        '''
        '''
        data: dict = await state.get_data()

        account_id = callback_data.id
        action = callback_data.action

        key = 'isActive' if action in [
                            'staff_edit_banks_active',
                            'staff_edit_banks_inactive'] else 'isDeleted'
        
        value = True if action in [
                            'staff_edit_banks_active',
                            'staff_edit_banks_delete'] else False

        patch_data = {
            key: value
        }
        response: dict = await api_gateway.patch(
            path=r.changerRoutes.banks,
            detailUrl=f'{account_id}/status_setter',
            data=patch_data,
            exp_code=[200]
        )
        exception: bool = response.get('exception')
        if not exception:
            await call.answer('Done!', show_alert=True)
            await staff_show_banks_account(                              # Доделать после проработки проверки!!!!!
                call,
                state,
                callback_data,
                api_gateway,
                bot
            )
        else:
             await call.answer(msg.error_msg, show_alert=True)




async def setup_edit_banks_handlers(dp: Dispatcher):
    '''Register callback_querry handlers there.
    '''
    dp.callback_query.register(

        staff_show_banks_account,
        StaffOfficeData.filter(
            
            F.action == 'staff_show_accounts'
        )
    )
    dp.callback_query.register(
        staff_bank_account_setter,
        StaffEditData.filter(
            F.action.in_({
                'staff_edit_banks_active',
                'staff_edit_banks_inactive',
                'staff_edit_banks_delete'
            })
        )
    )


