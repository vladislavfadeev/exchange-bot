from aiogram.fsm.context import FSMContext
from aiogram.types.callback_query import CallbackQuery
from aiogram.types import Message
from aiogram import F, Bot, Dispatcher

from core.middlwares.routes import r    # Dataclass whith all api routes
from core.utils import msg_maker
from core.api_actions.bot_api import SimpleAPI
from core.middlwares.settigns import appSettings
from core.utils.bot_fsm import FSMSteps
from core.utils import msg_var as msg
from core.keyboards import (
    changer_kb,
)
from core.keyboards.callbackdata import (
    StuffOfficeData,
)



async def offer_menu(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: StuffOfficeData,
        bot: Bot
):
    '''
    '''
    await state.set_state(FSMSteps.STUFF_OFFERS_MENU)
    data: dict = await state.get_data()
    mainMsg: Message = data.get('mainMsg')
    messageList: list = data.get('messageList')

    try:
        await mainMsg.delete()
    except:
        pass

    if messageList:

        for i in messageList:
            i: Message

            try:
                await bot.delete_message(
                    i.chat.id,
                    i.message_id
                )
            except:
                pass

    mainMsg: Message = await bot.send_message(
        call.from_user.id,
        text = await msg_maker.stuff_offer_menu(),
        reply_markup = await changer_kb.stuff_offer_menu_buttons()
    )
    await state.update_data(mainMsg = mainMsg)
    await state.update_data(editable_accounts = {})
    await state.update_data(accounts = {})



async def offer_menu_give_result(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: StuffOfficeData,
        bot: Bot
):
    '''
    '''
    data = await state.get_data()

    if callback_data.action == 'create_new':

        await call.message.edit_text(
            text= await msg_maker.stuff_set_currency(),
            reply_markup= await changer_kb.set_sell_currency_button()
        )

    elif callback_data.action == 'edit_offers':

        params = {
            'owner': call.from_user.id,
            'isActive': True,
            'isDeleted': False
        }
        response = await SimpleAPI.get(
            r.changerRoutes.myOffers,
            params=params
        )
        offer_list = response.json()

        if len(offer_list):

            await state.update_data(offerList = offer_list)
            messages = await msg_maker.offer_list_msg_maker(offer_list)

            await call.message.delete()

            messageList = []
            counter = 0
            for i in range(len(messages)):
                
                counter += 1
                isLatest = True if counter == len(messages) else False
                value = offer_list[i]

                self_msg = await bot.send_message(
                    call.from_user.id,
                    text = messages[i],
                    reply_markup= await changer_kb.stuff_edit_offer_list_buttons(
                        value['id'],
                    )
                )
                if isLatest:
                    sep_msg = await bot.send_message(
                        call.from_user.id,
                        text = msg.separator,
                        reply_markup = await changer_kb.staff_back_to_offer_menu()
                    )
                    messageList.append(sep_msg)

                messageList.append(self_msg)

            await state.update_data(messageList = messageList)

        else:
            await call.message.edit_text(
                text = msg.stuff_zero_offer,
                reply_markup = await changer_kb.sfuff_cancel_button()
            )

    elif callback_data.action == 'inactive':
        
        params = {
            'owner': call.from_user.id,
            'isActive': False,
            'isDeleted': False
        }

        response = await SimpleAPI.get(
            r.changerRoutes.myOffers,
            params = params
        )
        inactive_offers = response.json(

        )
        if len(inactive_offers):

            await state.update_data(offerList = inactive_offers)
            messages = await msg_maker.offer_list_msg_maker(inactive_offers)

            await call.message.delete()

            messageList = []
            counter = 0
            for i in range(len(messages)):
                
                counter += 1
                isLatest = True if counter == len(messages) else False
                char = inactive_offers[i]

                self_msg = await bot.send_message(
                    call.from_user.id,
                    text = messages[i],
                    reply_markup= await changer_kb.stuff_edit_inactive_offers_buttons(
                        char['id']
                    )
                )
                if isLatest:
                    sep_msg = await bot.send_message(
                        call.from_user.id,
                        text = msg.separator,
                        reply_markup = await changer_kb.staff_back_to_offer_menu()
                    )
                    messageList.append(sep_msg)

                messageList.append(self_msg)

            await state.update_data(messageList = messageList)

        else:
            await call.message.edit_text(
                text = msg.stuff_zero_offer,
                reply_markup = await changer_kb.sfuff_cancel_button()
            )




async def setup_menu_handlers(dp: Dispatcher):
    '''Register callback_querry handlers there.
    '''

    dp.callback_query.register(

        offer_menu,
        StuffOfficeData.filter(F.action == 'offers'),
    
    )
    dp.callback_query.register(
        
        offer_menu_give_result,
        StuffOfficeData.filter(
        
            F.action.in_({
                'create_new',
                'edit_offers',
                'inactive'
            })
        )
    )