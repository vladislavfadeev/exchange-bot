from datetime import datetime
import logging
from sqlite3 import paramstyle
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.types.callback_query import CallbackQuery
from aiogram.types import Message
from aiogram import F
from pydantic import create_model_from_namedtuple
from create_bot import bot, dp
from core.middlwares.routes import r    # Dataclass whith all api routes
from core.utils import msg_maker
from core.api_actions.bot_api import SimpleAPI
from core.utils.bot_fsm import FSMSteps
from core.utils import msg_var as msg
from core.keyboards import changer_kb
from core.keyboards import user_kb
from core.keyboards.callbackdata import (
    CurrencyData,
    StuffEditData,
    StuffOfficeData,
    UserProofActions,
)


async def offer_menu(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: StuffOfficeData
):
    '''
    '''
    await state.set_state(FSMSteps.STUFF_OFFERS)
    data = await state.get_data()
    mainMsg = data.get('mainMsg')
    await mainMsg.edit_text(
        text = await msg_maker.stuff_offer_menu(),
        reply_markup = await changer_kb.stuff_offer_menu_buttons()
    )



async def offer_menu_give_result(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: StuffOfficeData
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
                        isLatest
                    )
                )
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
                value = offer_list[i]

                self_msg = await bot.send_message(
                    call.from_user.id,
                    text = messages[i],
                    reply_markup= await changer_kb.stuff_edit_inactive_offers_buttons(
                        value['id'],
                        isLatest
                    )
                )
                messageList.append(self_msg)

            await state.update_data(messageList = messageList)

        else:
            await call.message.edit_text(
                text = msg.stuff_zero_offer,
                reply_markup = await changer_kb.sfuff_cancel_button()
            )



async def stuff_create_new_offer_currency(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: StuffEditData
):
    '''
    '''
    if callback_data.action == 'new_offer_currency':

        await state.update_data(new_currency = callback_data.value)
        await call.message.edit_text(
            text = msg.chr_enter_rate,
            reply_markup= await changer_kb.sfuff_cancel_button()
        )
        await state.set_state(FSMSteps.STUFF_OFFERS_RATE)

    elif callback_data.action == 'new_offer_currency_returned':

        await call.message.edit_text(
            text = msg.chr_enter_rate,
            reply_markup= await changer_kb.sfuff_cancel_button()
        )
        await state.set_state(FSMSteps.STUFF_OFFERS_RATE)



async def stuff_create_new_offer_rate(message: Message, state: FSMContext):
    '''
    '''
    await message.delete()
    data = await state.get_data()
    mainMsg = data.get('mainMsg')
    currency = data.get('new_currency')
    await state.update_data(accounts = [])
    
    try:

        value = message.text
        rate = float(value.replace(',', '.'))
            
    except ValueError as e:
        logging.error(e)
        await mainMsg.edit_text(
            text = msg.type_error_msg,
            reply_markup = await changer_kb.sfuff_cancel_button()
        )

    else:
        await state.update_data(new_rate = rate)
        await mainMsg.edit_text(
            text= await msg_maker.stuff_show_amount(rate, currency),
            reply_markup= await changer_kb.staff_accept_new_rate()
        )
        await state.set_state(FSMSteps.STUFF_OFFERS)    



async def stuff_create_new_offer_banks(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: StuffEditData
):
    '''
    '''
    data = await state.get_data()
    currency = data.get('new_currency')        

    params = {
        'owner': call.from_user.id,
        'isActive': True,
        'search': currency
    }

    response = await SimpleAPI.get(r.changerRoutes.banks, params = params)    
    banks = response.json()

    if callback_data.action == 'create_new_offer_banks':

        if len(banks):
            await call.message.edit_text(
                text = await msg_maker.stuff_create_new_offer_banks(currency),
                reply_markup= await changer_kb.stuff_create_new_offer_banks(banks)
            )

        else:
            await call.message.edit_text(
                text = msg.staff_zero_banks,
                reply_markup= await changer_kb.staff_zero_banks_buttons()
            )
        
    elif callback_data.action == 'staff_set_banks':

        account_id = callback_data.id
        accounts = data.get('accounts')

        for i in banks:
            if i['id'] == account_id:
                accounts.append(i)
                
        await state.update_data(accounts = accounts)

        await call.message.edit_text(
            text = await msg_maker.stuff_create_new_offer_banks(currency, accounts),
            reply_markup= await changer_kb.stuff_create_new_offer_banks(banks)
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

        tmpMessage = await bot.send_message(
            transfer['user'],
            text= await msg_maker.accept_user_transfer2()
        )
        await state.update_data(tmpMessage = tmpMessage)
        await bot.send_message(
            call.from_user.id,
            text= await msg_maker.accept_changer_transfer(transfer),
        )

        patchData = {
            'changerAcceptDate': datetime.now()
        }
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


async def get_changer_proof(message: Message, state: FSMContext):
    '''
    '''

    allData = await state.get_data()
    transferId = allData['transfer']['id']
    userId = allData['transfer']['user']
    buyAmount = allData['transfer']['buyAmount']
    tmpMessage = allData['tmpMessage']
    await message.delete()


    if message.photo:

        fileId = message.photo[-1].file_id
        proofType = 'photo'

    elif message.document:

        fileId = message.document.file_id
        proofType = 'document'

    data = {
        'changerSendMoneyDate': datetime.now(),
        'changerProofType': proofType,
        'changerProof': fileId,
    }

    response = await SimpleAPI.patch(
        r.changerRoutes.transactions,
        transferId,
        data=data
    )

    if proofType == 'photo':

        await tmpMessage.delete()
        await bot.send_photo(
            userId,
            photo = fileId,
            caption= await msg_maker.accept_changer_proof(transferId),
            reply_markup= await user_kb.accept_changer_transfer(response.json()['id'])
        )

    if proofType == 'document':

        await bot.send_document(
            userId, 
            document= fileId,
            caption= await msg_maker.accept_changer_proof(),
            reply_markup= await user_kb.accept_changer_transfer(response.json()['id'])
        )

    await bot.send_message(
        message.from_user.id,
        text= await msg_maker.changer_inform2(transferId)
        )
    await state.set_state(FSMSteps.STUFF_INIT_STATE)









async def register_message_handlers_changer():
    '''Registry message handlers there.
    '''
    dp.message.register(
        get_changer_proof,
        FSMSteps.GET_CHANGER_PROOF        
    ),
    dp.message.register(
        stuff_create_new_offer_rate,
        FSMSteps.STUFF_OFFERS_RATE
    )



async def register_callback_handler_changer():
    '''Register callback_querry handlers there.
    '''
    dp.callback_query.register(
        offer_menu,
        StuffOfficeData.filter(F.action == 'offers'),
        FSMSteps.STUFF_INIT_STATE
    ),
    dp.callback_query.register(
        offer_menu_give_result,
        StuffOfficeData.filter(F.action.in_({'create_new', 'edit_offers', 'inactive'}))
    ),
    dp.callback_query.register(
        stuff_create_new_offer_currency,
        StuffEditData.filter(F.action.in_({'new_offer_currency', 'new_offer_currency_returned'}))
    ),
    dp.callback_query.register(
        stuff_create_new_offer_banks,
        StuffEditData.filter(F.action.in_({'create_new_offer_banks', 'staff_set_banks'}))
    )




    dp.callback_query.register(
        accept_or_decline_user_transfer,
        UserProofActions.filter(),
        FSMSteps.STUFF_INIT_STATE
    )

