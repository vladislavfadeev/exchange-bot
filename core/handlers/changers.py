from datetime import datetime
import logging
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.types.callback_query import CallbackQuery
from aiogram.types import Message
from aiogram import F
from create_bot import bot, dp
from core.middlwares.routes import r    # Dataclass whith all api routes
from core.utils import msg_maker
from core.api_actions.bot_api import SimpleAPI
from core.utils.bot_fsm import FSMSteps
from core.utils import msg_var as msg
from core.keyboards import changer_kb
from core.keyboards import user_kb
from core.keyboards.callbackdata import (
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
            reply_markup= await`` user_kb.set_sell_currency_button()
        )

    elif callback_data.action == 'edit_offers':

        params = {
            'owner': call.from_user.id,
            'isActive': True
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
                text = msg.zero_offer,
                reply_markup = await user_kb.user_cancel_buttons_offerslist()
            )




    elif callback_data.action == 'inactive':
        ...

    else:
        unknown_data = callback_data.action
        user = call.from_user.id
        logging.ERROR(f'Handler resieved unknown callback data = {unknown_data}. User id = {user}')

    





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
    await state.set_state(FSMSteps.CHANGER_INIT_STATE)









async def register_message_handlers_changer():
    '''Registry message handlers there.
    '''
    dp.message.register(
        get_changer_proof,
        FSMSteps.GET_CHANGER_PROOF        
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
        StuffOfficeData.filter()
    )




    dp.callback_query.register(
        accept_or_decline_user_transfer,
        UserProofActions.filter(),
        FSMSteps.STUFF_INIT_STATE
    )

