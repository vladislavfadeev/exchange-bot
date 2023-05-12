import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.types.callback_query import CallbackQuery
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message
from aiogram import F, Bot, Dispatcher
from core.keyboards import admin_kb, home_kb
from core.middlwares.settigns import appSettings
from core.utils.notifier import transfers_getter_user
from core.middlwares.routes import r    # Dataclass whith all api routes
from core.utils import msg_maker, msg_var
from core.api_actions.bot_api import SimpleAPI
from core.utils.bot_fsm import FSMSteps
from core.utils import msg_var as msg
from core.keyboards import user_kb
from core.keyboards.callbackdata import (
    AmountData,
    CurrencyData,
    HomeData,
    OfferData,
    SetBuyBankData,
    SetSellBankData,
    UserProofActions,
)
from core.middlwares.exceptions import (
    MinAmountError,
    MaxAmountError,
)



async def new_user_event(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: UserProofActions,
        bot: Bot, 
        dp: Dispatcher
):
    '''User "main menu" were he can choose his actions.
    Exactly - 
    '''
    data: dict = await state.get_data()
    mainMsg: Message = data.get('mainMsg')
    user_event: list = data.get('user_events')

    if callback_data.action == 'user_new_events':

        if user_event:

            try:
                await bot.delete_message(
                    mainMsg.chat.id,
                    mainMsg.message_id
                )
            except:
                pass
            
            messageList = []

            for event in user_event:

                self_msg = await bot.send_message(
                    call.from_user.id,
                    text = await msg_maker.user_show_events(event),
                    reply_markup = await user_kb.user_show_event_kb(event)
                )
                messageList.append(self_msg)

            sep_msg = await bot.send_message(
                call.from_user.id,
                text = msg.separator,
                reply_markup = await home_kb.user_back_home_inline_button()
            )
            messageList.append(sep_msg)

            await state.update_data(messageList = messageList)

        else:

            await call.message.edit_text(
                text = msg.user_empty_event,
                reply_markup = await home_kb.user_back_home_inline_button()
            )

        await state.set_state(FSMSteps.GET_CHANGER_PROOF)
    
    elif callback_data.action == 'user_transfer_accepted':

        messageList = data.get('messageList')       
        transfer_id = callback_data.transferId

        patch_data = {
            'userAcceptDate': datetime.now(),
            'isCompleted': True
        }
        await SimpleAPI.patch(
            r.userRoutes.transactions,
            transfer_id,
            patch_data
        )
        new_event_list: list = [i for i in user_event if i['id'] != transfer_id]
        await state.update_data(user_events = new_event_list)

        if not new_event_list:

            for i in messageList:
                i: Message

                try:
                    await bot.delete_message(
                        i.chat.id,
                        i.message_id
                    )
                except:
                    pass
                #await call.answer(text=msg.user_transfer_claims_message, show_alert=True)

            mainMsg = await bot.send_message(
                call.from_user.id,
                text= await msg_maker.start_message(call.from_user.id, bot, dp), 
                reply_markup= await home_kb.user_home_inline_button(call.from_user.id, bot, dp)
            )
            await state.update_data(mainMsg = mainMsg)
            await state.set_state(FSMSteps.USER_INIT_STATE)

        else:

            await bot.delete_message(
                call.from_user.id,
                call.message.message_id
            )
            await call.answer('Done!', show_alert=True)


    elif callback_data.action == 'user_transfer_claims':

        transfer_id = callback_data.transferId

        transfer: dict = [i for i in user_event if i['id']==transfer_id][0]

        new_event_list: list = [i for i in user_event if i['id'] != transfer_id]
        await state.update_data(user_events = new_event_list)
        messageList = data.get('messageList')

        patch_data = {
            'claims': True
        }
        await SimpleAPI.patch(
            r.userRoutes.transactions,
            transfer_id,
            patch_data
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

        try:
            await bot.delete_message(
                call.message.chat.id,
                call.message.message_id
            )
        except:
            pass

        await call.answer(text=msg.user_transfer_claims_message, show_alert=True)

        # mainMsg = await bot.send_message(
        #     call.from_user.id,
        #     text = msg.user_transfer_claims_message,
        #     reply_markup= await home_kb.user_back_home_inline_button()
        # )
        await state.update_data(mainMsg = mainMsg)

        if not new_event_list:

            for i in messageList:
                i: Message

                try:
                    await bot.delete_message(
                        i.chat.id,
                        i.message_id
                    )
                except:
                    pass

            mainMsg = await bot.send_message(
                call.from_user.id,
                text= await msg_maker.start_message(call.from_user.id, bot, dp), 
                reply_markup= await home_kb.user_home_inline_button(call.from_user.id, bot, dp)
            )
            await state.update_data(mainMsg = mainMsg)
            await state.set_state(FSMSteps.USER_INIT_STATE)




async def start_change(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: HomeData,
        bot: Bot
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
        callback_data: CurrencyData,
        bot: Bot
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
        callback_data: OfferData,
        bot: Bot
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
            text=msg.enter_user_bank_name,
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
            "currency": "2",
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



async def get_user_proof(
        message: Message,
        state: FSMContext,
        apscheduler: AsyncIOScheduler
):
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
    buyAmount = round(sellAmount * rate)
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
            'isCompleted': False,
            'claims': False,
            'changerAccepted': False
        }

        response = await SimpleAPI.post(
            r.userRoutes.transactions,
            data=data
        )
        print(response.json())

        await message.delete()
        await mainMsg.edit_text(
            text= await msg_maker.user_inform(buyAmount),
            reply_markup = await user_kb.final_transfer_stage()
        )
        await state.set_state(FSMSteps.USER_INIT_STATE)

        getter_id = f'user_getter-{message.from_user.id}'
        job_list: list = apscheduler.get_jobs()
        job_id_list: list = [job.id for job in job_list]

        if getter_id not in job_id_list:
            apscheduler.add_job(
                transfers_getter_user,
                'interval',
                minutes=1,
                id=getter_id,
                kwargs = {
                    'user_id':message.from_user.id,
                }
            )




async def register_message_handlers_user(dp):
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


async def register_callback_handler_user(dp):
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

        new_user_event,
        UserProofActions.filter(
        
            F.action.in_({
                'user_new_events',
                'user_transfer_accepted',
                'user_transfer_claims'
            })
        )
    )
