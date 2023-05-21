from aiogram.fsm.context import FSMContext
from aiogram.types.callback_query import CallbackQuery
from aiogram import F, Bot, Dispatcher

from core.middlwares.routes import r    # Dataclass whith all api routes
from core.utils import msg_maker
from core.api_actions.bot_api import SimpleAPI
from core.utils.bot_fsm import FSMSteps
from core.utils import msg_var as msg
from core.keyboards import (
    changer_kb,
)
from core.keyboards.callbackdata import (
    StaffOfficeData,
)



async def staff_show_banks_account(                                # Доделать после проработки проверки!!!!!
        call: CallbackQuery,
        state: FSMContext,
        callback_data: StaffOfficeData,
        bot: Bot
):
    ''' 
    '''
    await state.set_state(FSMSteps.STUFF_ACCOUNTS)
    changer_id = call.from_user.id

    params = {
        'owner': changer_id,
        'isDeleted': False
    }

    response = await SimpleAPI.get(
        r.changerRoutes.banksCheker,
        params
    )
    banks_list = response.json()

    if len(banks_list):

        # accounts_list = [i['id'] for i in banks_list]
        
        # for i in banks_list:
        #     accounts_dict = 
        await call.message.delete()

        await state.update_data(staff_editable_banks = banks_list)
        messages = await msg_maker.staff_show_editable_banks(banks_list)

        messageList = []
        counter = 0
        for i in range(len(messages)):

            counter += 1
            isLatest = True if counter == len(messages) else False
            char = banks_list[i]
            isActive = char['isActive']

            self_msg = await bot.send_message(
                call.from_user.id,
                text = messages[i],
                reply_markup = await changer_kb.staff_edit_banks_accounts(
                    char['id'],
                    isActive,
                )
            )
            if isLatest:
                sep_msg = await bot.send_message(
                    call.from_user.id,
                    text = msg.separator,
                    reply_markup = await changer_kb.sfuff_cancel_button()
                )
                messageList.append(sep_msg)
            messageList.append(self_msg)

        await state.update_data(messageList = messageList)

    else:
        await call.message.edit_text(
            text = msg.staff_show_banks_account,
            reply_markup = await changer_kb.staff_zero_banks_buttons()
        )




    # elif callback_data.action in [                              # Доделать после проработки проверки!!!! 
    #     'staff_edit_banks_active',
    #     'staff_edit_banks_inactive',
    #     'staff_edit_banks_delete'
    #     ]:

    #     data: dict = await state.get_data()

    #     account_id = callback_data.id
    #     action = callback_data.action

    #     key = 'isActive' if action in [
    #                         'staff_edit_banks_active',
    #                         'staff_edit_banks_inactive'] else 'isDeleted'
        
    #     value = True if action in [
    #                         'staff_edit_banks_active',
    #                         'staff_edit_banks_delete'] else False

    #     patch_data = {
    #         key: value
    #     }
    #     await SimpleAPI.patch(
    #         r.changerRoutes.banks,
    #         f'{account_id}/status_setter',
    #         patch_data
    #     )

    #     await call.answer('Done!', show_alert=True)





async def setup_edit_banks_handlers(dp: Dispatcher):
    '''Register callback_querry handlers there.
    '''
    dp.callback_query.register(

        staff_show_banks_account,
        StaffOfficeData.filter(
            
            F.action == 'staff_show_accounts'
        )
    )


