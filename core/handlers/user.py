import asyncio
import logging
from datetime import datetime
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.types.callback_query import CallbackQuery
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message
from aiogram import F
from core.keyboards import admin_kb, home_kb
from core.middlwares.settigns import appSettings
from create_bot import bot, dp
from core.middlwares.routes import r    # Dataclass whith all api routes
from core.utils import msg_maker, msg_var
from core.api_actions.bot_api import SimpleAPI
from core.utils.bot_fsm import FSMSteps
from core.utils import msg_var as msg
from core.keyboards import user_kb
from core.keyboards.callbackdata import (
    AmountData,
    ChangerProofActions,
    CurrencyData,
    HomeData,
    OfferData,
    SetBuyBankData,
    SetSellBankData,
)
from core.middlwares.exceptions import (
    MinAmountError,
    MaxAmountError,
)




async def start_change(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: HomeData
):
    '''Handler is start user change currency process.
    React on "Обменять валюту" in "FSMSteps.INIT_STATE"
    ''' 
    data = await state.get_data()
    messageList = data.get('messageList')
    mainMsg = data.get('mainMsg')
    await state.update_data(messageList=[])
    
    try:
        await mainMsg.delete()
    except:
        pass

    if messageList:

        for i in messageList:
            try:
                await i.delete()
            except:
                pass

    mainMsg = await bot.send_message(
        call.from_user.id,
        text=msg.currency_choice_1,
        reply_markup=await user_kb.set_sell_currency_button()
    )
    await state.update_data(mainMsg = mainMsg)



async def show_offer(
        call: CallbackQuery, 
        state: FSMContext,
        callback_data: CurrencyData
):
    '''Show all available offers for the selected currency
    '''

    params = {
        'currency': callback_data.name,
        'isActive': True,
        'isDeleted': False,
        'owner__online': True
    }
    
    offers = await SimpleAPI.get(
        r.userRoutes.offer,
        params
    )
    offers = offers.json()
    if len(offers):

        await state.update_data(offerList = offers)
        messages = await msg_maker.offer_list_msg_maker(offers)

        await call.message.delete()
        
        messageList = []
        counter = 0
        for i in range(len(messages)):

            counter += 1
            value = offers[i]
            builder = InlineKeyboardBuilder()
            builder.button(
                text=f'🔥 Обменять {value["currency"]} тут 🔥',
                callback_data=OfferData(
                    id=value['id'],
                    isReturned=False
                )
            )
            if counter == len(messages):
                builder.button(
                    text='↩ Вернуться на главную',
                    callback_data=HomeData(
                        action='cancel'
                    )
                )
                builder.adjust(1)

            self_msg = await bot.send_message(
                call.from_user.id,
                text=messages[i],
                reply_markup=builder.as_markup()
            )
            messageList.append(self_msg)
        await state.update_data(messageList = messageList)

    else:
        await call.message.edit_text(
            text=msg.zero_offer, 
            reply_markup= await user_kb.user_cancel_buttons_offerslist()           
        )



async def set_amount(
        call: CallbackQuery,
        state:FSMContext,
        callback_data: OfferData
    ):
    '''
    '''
    if callback_data.isReturned:

        data = await state.get_data()
        offerData = data['selectedOffer']
        
        await call.message.edit_text(
            text = await msg_maker.set_amount_returned_msg_maker(offerData),
            reply_markup= await home_kb.user_back_home_inline_button()
        )

    else:
        
        data = await state.get_data()
        await state.update_data(messageList=[])

        for i in data['offerList']:
            if i['id'] == callback_data.id:
            
                await state.update_data(selectedOffer = i)
                await state.update_data(offerList = {})
                offerData = i
        
        try:
            msg_list = data['messageList']

            for i in range(len(msg_list)):
                await msg_list[i].delete()
            
            lastMsg = await bot.send_message(
                call.from_user.id,
                text = await msg_maker.set_amount_msg_maker(offerData),
                reply_markup= await home_kb.user_back_home_inline_button()
            )
        except Exception as e:
            logging.exception(e)
            lastMsg = await bot.send_message(
                call.from_user.id,
                text = await msg_maker.set_amount_msg_maker(offerData),
                reply_markup= await home_kb.user_back_home_inline_button()
            )
        await state.update_data(mainMsg = lastMsg)

    await state.set_state(FSMSteps.SET_AMOUNT_STATE)
    


async def set_amount_check(message: Message, state: FSMContext):
    '''
    '''
    data = await state.get_data()
    offerData = data['selectedOffer']
    mainMsg = data['mainMsg']
    await message.delete()
    
    try:

        value = message.text
        amount = float(value.replace(',', '.'))
        
        if offerData['minAmount'] != None:
            if amount < offerData['minAmount']:
                raise MinAmountError()
            
        if offerData['maxAmount'] != None:
            if amount > offerData['maxAmount']:
                raise MaxAmountError()
            
    except ValueError as e:
        logging.error(e)
        await mainMsg.edit_text(
            text=msg_var.type_error_msg,
            reply_markup = await user_kb.user_return_to_offer_choice_button(offerData)
        )

    except MinAmountError as e:
        logging.error(e)
        await mainMsg.edit_text(
            text = await msg_maker.min_amount_error_msg_maker(offerData),
            reply_markup = await user_kb.user_return_to_offer_choice_button(offerData)
        )

    except MaxAmountError as e:
        logging.error(e)
        await mainMsg.edit_text(
            text = await msg_maker.max_amount_error_msg_maker(offerData),
            reply_markup = await user_kb.user_return_to_offer_choice_button(offerData)
        )

    else:
        await state.update_data(sellAmount = amount)
        await mainMsg.edit_text(
            text= await msg_maker.show_user_buy_amount(
                amount,
                offerData['rate'],
                offerData['currency']
            ),
            reply_markup= await user_kb.set_amount_check_inlkb()
        )
        await state.set_state(None)



async def choose_sell_bank(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: AmountData   
    ):
    '''
    '''
    # await state.set_state(FSMSteps.SET_SELL_BANK)
    data = await state.get_data()
    offerData = data['selectedOffer']

    params = {
        'owner': offerData["owner"],
        'isActive': True,
        'currency__name': offerData["currency"]
    }

    banks = await SimpleAPI.get(
        r.userRoutes.changerBanks,
        params
    )

    await call.message.edit_text(
        text= await msg_maker.set_sell_bank(offerData['currency']),
        reply_markup= await user_kb.set_sell_bank(banks)
    )
    


async def choose_buy_bank(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: SetSellBankData
    ):
    '''
    '''
    await state.set_state(FSMSteps.SET_BUY_BANK_INIT)

    params = {
        'owner': call.from_user.id,
        'isActive': True
    }
    banks = await SimpleAPI.get(r.userRoutes.userBanks, params)

    if len(banks.json()) and not callback_data.setNew:

        await state.update_data(sellBank = callback_data.id)        
        await call.message.edit_text(
            text = await msg_maker.choose_user_bank_from_db(),
            reply_markup= await user_kb.choose_user_bank_from_db(banks)
        )

    else:
        if not callback_data.setNew:
            await state.update_data(sellBank = callback_data.id)

        banksName = await SimpleAPI.get(r.userRoutes.banksNameList)

        await call.message.edit_text(
            text='Выберите банк из списка:',
            reply_markup= await user_kb.choose_bank_name_from_list(banksName)
        )



async def choose_new_buy_bank_next(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: SetBuyBankData
    ):
    '''
    '''
    await state.update_data(buyBank = callback_data.bankName)
    await state.set_state(FSMSteps.SET_BUY_BANK_ACCOUNT)
    await call.message.edit_text(
        text= await msg_maker.set_buy_bank_account(
            callback_data.bankName
        ),
        reply_markup= await home_kb.user_back_home_inline_button()
    )



async def apply_new_buy_bank(message: Message, state: FSMContext):
    '''
    '''
    await message.delete()
    allData = await state.get_data()
    bankName = allData['buyBank']
    changerId = allData['selectedOffer']['owner']
    mainMsg = allData['mainMsg']
    
    try:
        account = int(message.text)

        postData = {
            "name": bankName,
            "bankAccount": account,
            "owner": message.from_user.id,
            "currency": "3",
            "isActive": True        
        }

        account = await SimpleAPI.post(r.userRoutes.userBanks, postData)

        await mainMsg.edit_text( 
            text= await msg_maker.complete_set_new_bank(allData),
            reply_markup= await home_kb.user_back_home_inline_button()
        )
        await state.update_data(userAccount = account.json())
        await state.set_state(FSMSteps.GET_USER_PROOF)

    except ValueError as e:
        logging.exception(e)
        await mainMsg.edit_text(
            text='only digits without any symbol, try again',
            reply_markup = await user_kb.get_trouble_staff_contact()
        )

    except Exception as e:
        logging.exception(e)
        await mainMsg.edit_text(
            text='data type is not provided, try again',
            reply_markup = await user_kb.get_trouble_staff_contact()
        )



async def use_old_buy_bank(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: SetBuyBankData
    ):
    '''
    '''
    allData = await state.get_data()
    accountId = callback_data.id
    
    userAccount = await SimpleAPI.getDetails(
        r.userRoutes.userBanks,
        accountId
    )
    await state.update_data(userAccount = userAccount.json())

    await call.message.edit_text(
        text= await msg_maker.complete_set_new_bank(allData),
        reply_markup= await home_kb.user_back_home_inline_button()
    )
    await state.set_state(FSMSteps.GET_USER_PROOF)



async def get_user_proof(message: Message, state: FSMContext):
    '''
    '''

    allData = await state.get_data()
    mainMsg: Message = allData['mainMsg']
    changerId = allData['selectedOffer']['owner']
    offerId = allData['selectedOffer']['id']
    changerBank = allData['sellBank']
    userBank = allData['userAccount']['id']
    sellCurrency = allData['selectedOffer']['currency']
    sellAmount = allData['sellAmount']
    rate = allData['selectedOffer']['rate']
    buyAmount = sellAmount * rate
    accountId = message.from_user.id

    try:
        if message.photo:

            fileId = message.photo[-1].file_id
            proofType = 'photo'

        elif message.document:

            fileId = message.document.file_id
            proofType = 'document'

    except Exception as e:

        logging.exception(e)

        await message.delete()
        await mainMsg.edit_text(
            text='⚠️ Data type is not provided, try again ⚠️',
            reply_markup = await user_kb.get_trouble_staff_contact()
        )
    else:
        data = {
            'changer': changerId,
            'offer': offerId,
            'user': accountId,
            'changerBank_id': changerBank,
            'userBank_id': userBank,
            'sellCurrency': sellCurrency,
            'buyCurrency': 'MNT',
            'sellAmount': sellAmount,
            'buyAmount': buyAmount,
            'rate': rate,
            'userSendMoneyDate': datetime.now(),
            'userProofType': proofType,
            'userProof': fileId,
        }

        response = await SimpleAPI.post(
            r.userRoutes.transactions,
            data=data
        )

        changer_state: FSMContext = FSMContext(
            bot=bot,
            storage=dp.storage,
            key=StorageKey(
                chat_id=changerId,
                user_id=changerId,  
                bot_id=bot.id
            )
        )
        ch_data: dict = await changer_state.get_data()
        current_tr_list: list = ch_data.get('new_transfer')

        current_tr_list.append(response.json())

        await changer_state.update_data(
            new_transfer = current_tr_list
        )

        await message.delete()
        await mainMsg.edit_text(
            text= await msg_maker.user_inform(buyAmount),
            reply_markup = await user_kb.get_trouble_staff_contact()
        )
        await state.set_state(FSMSteps.WAIT_CHANGER_PROOF)





async def accept_or_decline_changer_transfer(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: ChangerProofActions
    ):
    '''
    '''
    response = await SimpleAPI.getDetails(
        r.changerRoutes.transactions,
        callback_data.transferId
    )
    transfer = response.json()
    await state.update_data(transfer = transfer)
    data = await state.get_data()
    mainMsg = data['mainMsg']

    if callback_data.action == 'accept':

        await call.message.delete()
        await bot.send_message(
            transfer['changer'],
            text= await msg_maker.accept_changer_transfer2(transfer['id'])
        )
        await mainMsg.edit_text(
            text=msg.start_message, 
            reply_markup= await home_kb.user_home_inline_button()
        )
        del_msg = await call.message.answer(
            text= await msg_maker.accept_changer_transfer3(transfer['id']),
        )
        await asyncio.sleep(3)
        try:
            await del_msg.delete()
        except:
            pass

        patchData = {
            'userAcceptDate': datetime.now(),
            'isCompleted': True
        }
        await SimpleAPI.patch(
            r.userRoutes.transactions,
            transfer['id'],
            data=patchData
        )
        await state.set_state(None)

    elif callback_data.action == 'decline':
        
        del_msg = await bot.send_message(
            transfer['changer'],
            text= await msg_maker.decline_changer_transfer(transfer['id'])
        )
        del_msg2 = await bot.send_message(
            call.from_user.id,
            text= await msg_maker.decline_changer_transfer2(transfer['id'])
        )
        await bot.send_message(
            appSettings.botSetting.troubleStaffId,
            text=f'Пользователь не принял перевод обменника, Заявка {transfer["id"]}',
            reply_markup= await admin_kb.get_claim_contacts_toadmin(
                call.from_user.id,
                transfer['changer']
            )
        )
        if transfer['userProofType'] == 'photo':
            await bot.send_photo(
                appSettings.botSetting.troubleStaffId,
                photo= transfer['userProof'],
                caption= f'Подтверждение пользователя. Заявка {transfer["id"]}'
            )
        elif transfer['userProofType'] == 'document':
            await bot.send_document(
                appSettings.botSetting.troubleStaffId,
                document= transfer['userProof'],
                caption= f'Подтверждение пользователя. Заявка {transfer["id"]}'
            )

        if transfer['changerProofType'] == 'photo':
            await bot.send_photo(
                appSettings.botSetting.troubleStaffId,
                photo= transfer['changerProof'],
                caption= f'Подтверждение обменника. Заявка {transfer["id"]}'
            )
        elif transfer['changerProofType'] == 'document':
            await bot.send_document(
                appSettings.botSetting.troubleStaffId,
                document= transfer['changerProof'],
                caption= f'Подтверждение обменника. Заявка {transfer["id"]}'
            )

        await asyncio.sleep(10)
        try:
            await call.message.delete()
            await del_msg.delete()
            await del_msg2.delete()
            await mainMsg.edit_text(
                text=msg.start_message, 
                reply_markup= await home_kb.user_home_inline_button()
            )
        except:
            pass

    elif callback_data.action == 'admin':
        await bot.send_message(
            call.from_user.id,
            text= await msg_maker.contact_to_admin()
        )







async def register_message_handlers_user():
    '''Registry message handlers there.
    '''
    dp.message.register(
        set_amount_check,
        FSMSteps.SET_AMOUNT_STATE,
        F.text
    )
    dp.message.register(
        choose_sell_bank,
        FSMSteps.SET_SELL_BANK,
        F.text
    )
    dp.message.register(
        apply_new_buy_bank,
        FSMSteps.SET_BUY_BANK_ACCOUNT,
        F.text
    )
    dp.message.register(
        get_user_proof,
        # F.content_type.in_({'photo', 'document'}),
        FSMSteps.GET_USER_PROOF
    )


async def register_callback_handler_user():
    '''Register callback_querry handlers there.
    '''
    dp.callback_query.register(
        start_change,
        HomeData.filter(F.action == 'change'),
        # FSMSteps.USER_INIT_STATE
    )

    dp.callback_query.register(
        show_offer,
        CurrencyData.filter()
    )
    dp.callback_query.register(
        set_amount,
        OfferData.filter()
    )
    dp.callback_query.register(
        choose_sell_bank,
        AmountData.filter()
    )
    dp.callback_query.register(
        choose_buy_bank,
        SetSellBankData.filter()
    )
    dp.callback_query.register(
        choose_new_buy_bank_next,
        SetBuyBankData.filter(F.setNew == True)
    )
    dp.callback_query.register(
        use_old_buy_bank,
        SetBuyBankData.filter((F.setNew == False) & (F.id != 0))
    )
    dp.callback_query.register(
        accept_or_decline_changer_transfer,
        ChangerProofActions.filter()
    )
