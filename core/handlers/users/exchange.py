import asyncio
import logging
from datetime import datetime
from httpx import Response
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram.fsm.context import FSMContext
from aiogram.types.callback_query import CallbackQuery
from aiogram.types import Message
from aiogram import F, Bot, Dispatcher

from core.keyboards import home_kb
from core.utils.notifier import transfers_getter_user
from core.middlwares.routes import r    # Dataclass whith all api routes
from core.middlwares.settigns import appSettings
from core.utils import msg_maker, msg_var
from core.api_actions.bot_api import SimpleAPI
from core.utils.bot_fsm import FSMSteps
from core.utils import msg_var as msg
from core.keyboards import user_kb
from core.keyboards.callbackdata import (
    UserHomeData,
    UserExchangeData,
)
from core.middlwares.exceptions import (
    MinAmountError,
    MaxAmountError,
    ResponseError,
)



async def start_change(
        call: CallbackQuery,
        state: FSMContext,
        bot: Bot
):
    '''
    Handler is start user change currency process.
    ''' 
    data: dict = await state.get_data()
    messageList: list = data.get('messageList')
    mainMsg: Message = data.get('mainMsg')
    await state.update_data(messageList=[])
    try:
        await bot.delete_message(
            mainMsg.chat.id,
            mainMsg.message_id
        )
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
    # send message with all currency for user choice
    mainMsg = await bot.send_message(
        call.from_user.id,
        text=msg.currency_choice_1,
        reply_markup=await user_kb.set_sell_currency_button()
    )
    await state.update_data(mainMsg = mainMsg)



async def show_offer(
        call: CallbackQuery, 
        state: FSMContext,
        callback_data: UserExchangeData,
        bot: Bot
):
    '''
    Show all available offers for the selected currency
    '''
    type = 'buy' if callback_data.action == 'buy_currency' else 'sell'
    # prepare filter params and get from backend all matching offers
    params = {
        'currency': callback_data.name,
        'type': type,
        'isActive': True,
        'isDeleted': False,
        'owner__online': True
    }
    try:
        offers: Response = await SimpleAPI.get(
            r.userRoutes.offer,
            params
        )
        if offers.status_code != 200:
            raise ResponseError()
        
    except ResponseError as e:
        await call.message.edit_text(
            text=msg.error_msg,
            reply_markup= await user_kb.final_transfer_stage(),
        )
        await bot.send_message(
            appSettings.botSetting.devStaffId,
            text=(
                'handlers.users.exchange.py - show-offer\n'
                f'{repr(e)}\n'
                f'{offers.json()}'
            )
        )
        logging.exception(f'{e} - {offers.json()}')

    except Exception as e:
        await call.message.edit_text(
            text=msg.error_msg,
            reply_markup= await user_kb.final_transfer_stage(),
        )
        await bot.send_message(
            appSettings.botSetting.devStaffId,
            text=(
                'handlers.users.exchange.py - show-offer\n'
                f'{repr(e)}'
            )
        )
        logging.exception(e)
    else:
        offers_list: list = offers.json()
        if offers_list:
            # if response is not empty
            await state.update_data(selected_curr_id = callback_data.id)
            await state.update_data(offerList = offers_list)
            await call.message.delete()
            # create 'messageList' varible containing all offer messages, 
            # and send all offers to user
            messageList = []
            for offer in offers_list:
                self_msg: Message = await bot.send_message(
                    call.from_user.id,
                    text= await msg_maker.offer_list_msg_maker(offer),
                    reply_markup= await user_kb.show_offer_list_kb(offer)
                )
                messageList.append(self_msg)
            # add back to main menu message
            sep_msg: Message = await bot.send_message(
                call.from_user.id,
                text = msg.separator,
                reply_markup = await home_kb.user_back_home_inline_button()
            )
            messageList.append(sep_msg)
            await state.update_data(messageList = messageList)
        else:
            # if response is empty
            await call.message.edit_text(
                text=msg.zero_offer, 
                reply_markup= await user_kb.user_cancel_buttons_offerslist()
            )



async def set_amount(
        call: CallbackQuery,
        state:FSMContext,
        callback_data: UserExchangeData,
        bot: Bot
    ):
    '''
    When user made a choice, he need set amount of transfer
    '''
    if callback_data.action == 'user_exchange_set_amount'\
        and callback_data.is_returned:
        # if user was returned from next step and want 
        # set new transfer amount
        data: dict = await state.get_data()
        offerData: dict = data.get('selectedOffer')
        await call.message.edit_text(
            text = await msg_maker.set_amount_returned_msg_maker(offerData),
            reply_markup= await home_kb.user_back_home_inline_button()
        )
    else:
        data: dict = await state.get_data()
        await state.update_data(messageList=[])
        # get selected offer info
        for i in data.get('offerList'):
            if i['id'] == callback_data.id:
                await state.update_data(selectedOffer = i)
                await state.update_data(offerList = {})
                offerData = i
        # get all messages whith offers from previous step
        # and delete it
        msg_list: dict = data.get('messageList')
        for i in msg_list:
            i: Message
            await bot.delete_message(
                i.chat.id,
                i.message_id
            )
        mainMsg: Message = await bot.send_message(
            call.from_user.id,
            text = await msg_maker.set_amount_msg_maker(offerData),
            reply_markup= await home_kb.user_back_home_inline_button()
        )
        await state.update_data(mainMsg = mainMsg)
    # set state for next step
    await state.set_state(FSMSteps.SET_AMOUNT_STATE)
    


async def set_amount_check(message: Message, state: FSMContext):
    '''
    Handler accepts message from user and make validation
    '''
    data: dict = await state.get_data()
    offerData: dict = data.get('selectedOffer')
    mainMsg: Message = data.get('mainMsg')
    await message.delete()
    # make validation
    try:
        value = message.text
        amount = float(value.replace(',', '.').replace(' ', ''))

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
            reply_markup = await user_kb.user_return_to_offer_choice_button(
                offerData
            )
        )
    except MinAmountError as e:
        logging.error(e)
        await mainMsg.edit_text(
            text = await msg_maker.min_amount_error_msg_maker(offerData),
            reply_markup = await user_kb.user_return_to_offer_choice_button(
                offerData
            )
        )
    except MaxAmountError as e:
        logging.error(e)
        await mainMsg.edit_text(
            text = await msg_maker.max_amount_error_msg_maker(offerData),
            reply_markup = await user_kb.user_return_to_offer_choice_button(
                offerData
            )
        )
    else:
        # if value is valid 
        await state.update_data(sellAmount = amount)
        await mainMsg.edit_text(
            text= await msg_maker.show_user_buy_amount(
                amount,
                offerData['rate'],
                offerData['currency']
            ),
            reply_markup= await user_kb.set_amount_check_inlkb()
        )
        await state.set_state(FSMSteps.USER_INIT_STATE)



async def choose_changer_bank(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: UserExchangeData,
        bot: Bot 
    ):
    '''
    There user select changer bank wich it will be comfortable
    for him to make money transfer 
    '''
    data: dict = await state.get_data()
    offer_data: dict = data.get('selectedOffer')
    offer_type: str = offer_data.get('type')
    # get changer bank account depending of the offer type
    if offer_type == 'buy':
        currency = offer_data.get('currency')
        params = {
            'owner': offer_data.get("owner"),
            'isActive': True,
            'currency__name': currency
        }
    elif offer_type == 'sell':
        currency = 'MNT'
        params = {
            'owner': offer_data("owner"),
            'isActive': True,
            'currency__name': currency
        }
    try:
        banks: Response = await SimpleAPI.get(
            r.userRoutes.changerBanks,
            params
        )
        if banks.status_code != 200:
            raise ResponseError()
    except ResponseError as e:
        await call.message.edit_text(
            text=msg.error_msg,
            reply_markup= await user_kb.final_transfer_stage(),
        )
        await bot.send_message(
            appSettings.botSetting.devStaffId,
            text=(
                'handlers.users.exchange.py - choose_changer_bank\n'
                f'{repr(e)}\n'
                f'{banks.json()}'
            )
        )
        logging.exception(f'{e} - {banks.json()}')
    except Exception as e:
        await call.message.edit_text(
            text=msg.error_msg,
            reply_markup= await user_kb.final_transfer_stage(),
        )
        await bot.send_message(
            appSettings.botSetting.devStaffId,
            text=(
                'handlers.users.exchange.py - choose_changer_bank\n'
                f'{repr(e)}'
            )
        )
        logging.exception(e)
    else:
        await call.message.edit_text(
            text= await msg_maker.set_changer_bank(currency),
            reply_markup= await user_kb.set_changer_bank(banks)
        )
    


async def choose_user_bank(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: UserExchangeData,
        bot: Bot
    ):
    '''
    Bot chek availability of bank accounts. If it does
    not exists - bot suggest create new.
     '''
    await state.set_state(FSMSteps.SET_BUY_BANK_INIT)
    data: dict = await state.get_data()
    offer: dict = data.get('selectedOffer')
    offer_type: str = offer.get('type')
    # check user banks accounts depending of the offer type
    if offer_type == 'buy':
        currency: str = 'MNT'
        params = {
            'owner': call.from_user.id,
            'isActive': True,
            'currency__name': currency
        }
    elif offer_type == 'sell':
        currency: str = offer.get('currency')
        params = {
            'owner': call.from_user.id,
            'isActive': True,
            'currency__name': currency
        }
    try:
        banksName: Response = await SimpleAPI.get(
            r.userRoutes.banksNameList
        )
        banks: Response = await SimpleAPI.get(
            r.userRoutes.userBanks,
            params
        )
        if banks.status_code != 200 \
            or banksName.status_code != 200:
            raise ResponseError()
    except ResponseError as e:
        await call.message.edit_text(
            text=msg.error_msg,
            reply_markup= await user_kb.final_transfer_stage(),
        )
        await bot.send_message(
            appSettings.botSetting.devStaffId,
            text=(
                'handlers.users.exchange.py -> choose_user_bank\n'
                f'{repr(e)}\n'
                f'{banks.json()}'
            )
        )
        logging.exception(f'{e} - {banks.json()}')
    except Exception as e:
        await call.message.edit_text(
            text=msg.error_msg,
            reply_markup= await user_kb.final_transfer_stage(),
        )
        await bot.send_message(
            appSettings.botSetting.devStaffId,
            text=(
                'handlers.users.exchange.py - choose_user_bank\n'
                f'{repr(e)}'
            )
        )
        logging.exception(e)
    else:
        # if user have bank account for offer currency
        if banks.json() and callback_data.name != 'set_new':
            await state.update_data(changerBank = callback_data.id)        
            await call.message.edit_text(
                text = await msg_maker.choose_user_bank_from_db(),
                reply_markup= await user_kb.choose_user_bank_from_db(banks)
            )
        # if accounts does not exists or user want create new
        else:
            if callback_data.name != 'set_new':
                await state.update_data(changerBank = callback_data.id)
            await call.message.edit_text(
                text=msg.enter_user_bank_name,
                reply_markup= await user_kb.choose_bank_name_from_list(
                    banksName
                )
            )



async def choose_new_user_bank_next(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: UserExchangeData
    ):
    '''
    This handler calling if user want create new bank account,
    when he set name of bank on previous step (choose_user_bank)
    '''
    # set bank name to bot state
    await state.update_data(userBank = callback_data.name)
    # set FSM state for correctly work next handler
    await state.set_state(FSMSteps.SET_BUY_BANK_ACCOUNT)
    await call.message.edit_text(
        text= await msg_maker.set_buy_bank_account(
            callback_data.name
        ),
        reply_markup= await home_kb.user_back_home_inline_button()
    )



async def apply_new_user_bank(
        message: Message,
        state: FSMContext,
        bot: Bot
    ):
    '''
    Handler get message value and make it valid. If all ok - try
    create new user bank account. Account number must be unique, 
    if it's not - account will not be created.
    '''
    await message.delete()
    data: dict = await state.get_data()
    bankName: str = data.get('userBank')
    offer: dict = data.get('selectedOffer')
    curr_id: int = data.get('selected_curr_id')
    mainMsg: Message = data.get('mainMsg')
    try:
        account = int(message.text)
    except ValueError as e:
        logging.exception(e)
        await mainMsg.edit_text(
            text=msg.account_value_error,
            reply_markup = await user_kb.final_transfer_stage()
        )
    except Exception as e:
        logging.exception(e)
        await mainMsg.edit_text(
            text=msg.account_exception,
            reply_markup = await user_kb.final_transfer_stage()
        )
    else:
        offer_type = offer.get('type')
        currency = curr_id if offer_type == 'sell' else 2
        postData = {
            "name": bankName,
            "bankAccount": account,
            "owner": message.from_user.id,
            "currency": currency,
            "isActive": True
        }
        try:
            response: Response = await SimpleAPI.post(
                r.userRoutes.userBanks,
                postData
            )
            if response.status_code != 201:
                raise ResponseError()
        except ResponseError as e:
            await mainMsg.edit_text(
                text=msg.create_account_error,
                reply_markup= await user_kb.final_transfer_stage(),
            )
            await bot.send_message(
                appSettings.botSetting.devStaffId,
                text=(
                    'handlers.users.exchange.py -> apply_new_user_bank\n'
                    f'{repr(e)}\n'
                    f'{response.json()}'
                )
            )
            logging.exception(f'{e} - {response.json()}')
        except Exception as e:
            await mainMsg.edit_text(
                text=msg.error_msg,
                reply_markup= await user_kb.final_transfer_stage(),
            )
            await bot.send_message(
                appSettings.botSetting.devStaffId,
                text=(
                    'handlers.users.exchange.py - apply_new_user_bank\n'
                    f'{repr(e)}'
                )
            )
            logging.exception(e)
        else:
            await mainMsg.edit_text( 
                text= await msg_maker.complete_set_new_bank(data),
                reply_markup= await home_kb.user_back_home_inline_button()
            )
            await state.update_data(userAccount = response.json())
            await state.set_state(FSMSteps.GET_USER_PROOF)




async def use_old_user_bank(
        call: CallbackQuery,
        state: FSMContext,
        bot: Bot,
        callback_data: UserExchangeData
    ):
    '''
    Handler calling if user have avalible bank account
    '''
    data = await state.get_data()
    accountId = callback_data.id
    # try to get full data of user bank account by account_id
    try:
        userAccount: Response = await SimpleAPI.getDetails(
            r.userRoutes.userBanks,
            accountId
        )
        if userAccount.status_code != 200:
            raise ResponseError()
    except ResponseError as e:
        await call.message.edit_text(
            text=msg.error_msg,
            reply_markup= await user_kb.final_transfer_stage(),
        )
        await bot.send_message(
            appSettings.botSetting.devStaffId,
            text=(
                'handlers.users.exchange.py -> use_old_user_bank\n'
                f'{repr(e)}\n'
                f'{userAccount.json()}'
            )
        )
        logging.exception(f'{e} - {userAccount.json()}')
    except Exception as e:
        await call.message.edit_text(
            text=msg.error_msg,
            reply_markup= await user_kb.final_transfer_stage(),
        )
        await bot.send_message(
            appSettings.botSetting.devStaffId,
            text=(
                'handlers.users.exchange.py -> use_old_user_bank\n'
                f'{repr(e)}'
            )
        )
        logging.exception(e)
    else:
        await state.update_data(userAccount = userAccount.json())
        await call.message.edit_text(
            text= await msg_maker.complete_set_new_bank(data),
            reply_markup= await home_kb.user_back_home_inline_button()
        )
        await state.set_state(FSMSteps.GET_USER_PROOF)



async def get_user_proof(
        message: Message,
        state: FSMContext,
        apscheduler: AsyncIOScheduler,
        bot: Bot
):
    '''
    This handler get file or foto whit user proof that
    he make money transfer and create transaction on backend
    '''
    data: dict = await state.get_data()
    selected_offer: dict = data.get('selectedOffer')
    mainMsg: Message = data.get('mainMsg')
    changerId: int = selected_offer.get('owner')
    offerId: int = selected_offer.get('id')
    changerBank: int = data.get('changerBank')
    userBank: int = data.get('userBank')
    sellCurrency: str = selected_offer.get('currency')
    sellAmount: float = data.get('sellAmount')
    rate: float = selected_offer.get('rate')
    buyAmount: float = round(sellAmount * rate)
    accountId: int = message.from_user.id
    # delete user proof message from screen
    await message.delete()
    # check message type, supported only image and other
    # files. For example -pdf 
    try:
        if message.photo:
            fileId = message.photo[-1].file_id
            proofType = 'photo'
        elif message.document:
            fileId = message.document.file_id
            proofType = 'document'
        else:
            raise TypeError()
    except TypeError:
        # inform user about error and delete this message
        # after 3 seconds 
        del_msg: Message = await bot.send_message(
            text=msg.type_error_message
        )
        await asyncio.sleep(3)
        try:
            await del_msg.delete()
        except:
            pass
    else:
        post_data = {
            'changer': changerId,
            'offer': offerId,
            'user': accountId,
            'changerBank_id': changerBank,
            'userBank_id': userBank,
            'offerCurrency': sellCurrency,
            'refCurrency': 'MNT',
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
        try:
            transaction: Response = await SimpleAPI.post(
                r.userRoutes.transactions,
                post_data
            )
            if transaction.status_code != 201:
                raise ResponseError()
        except ResponseError as e:
            await mainMsg.edit_text(
                text=msg.error_msg,
                reply_markup= await user_kb.final_transfer_stage(),
            )
            await bot.send_message(
                appSettings.botSetting.devStaffId,
                text=(
                    'handlers.users.exchange.py -> use_old_user_bank\n'
                    f'{repr(e)}\n'
                    f'{transaction.json()}'
                )
            )
            logging.exception(f'{e} - {transaction.json()}')
        except Exception as e:
            await mainMsg.edit_text(
                text=msg.error_msg,
                reply_markup= await user_kb.final_transfer_stage(),
            )
            await bot.send_message(
                appSettings.botSetting.devStaffId,
                text=(
                    'handlers.users.exchange.py -> use_old_user_bank\n'
                    f'{repr(e)}'
                )
            )
            logging.exception(e)
        else:
            # if all checks were sucsessful bot create new
            # task that will track the exchanger's response
            await mainMsg.edit_text(
                text= await msg_maker.user_inform(buyAmount),
                reply_markup = await user_kb.final_transfer_stage()
            )
            await state.set_state(FSMSteps.USER_INIT_STATE)
            # check if the task is not in joblist add it in
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




async def setup_exchande_handlers(dp: Dispatcher):
    '''Registry message handlers there.
    '''
    dp.message.register(
        set_amount_check,
        FSMSteps.SET_AMOUNT_STATE,
        F.text
    )
    # dp.message.register(
    #     choose_sell_bank,
    #     FSMSteps.SET_SELL_BANK,
    #     F.text
    # )
    dp.message.register(
        apply_new_user_bank,
        FSMSteps.SET_BUY_BANK_ACCOUNT,
        F.text
    )
    dp.message.register(
        get_user_proof,
        # F.content_type.in_({'photo', 'document'}),
        FSMSteps.GET_USER_PROOF
    )
    dp.callback_query.register(
        start_change,
        UserHomeData.filter(F.action == 'change'),
    )
    dp.callback_query.register(
        show_offer,
        UserExchangeData.filter(
            F.action.in_({
                'buy_currency',
                'sell_currency'
            })
        )
    )
    dp.callback_query.register(
        set_amount,
        UserExchangeData.filter(
            F.action == 'user_exchange_set_amount'
        )
    )
    dp.callback_query.register(
        choose_changer_bank,
        UserExchangeData.filter(
            F.action == 'choose_changer_bank'
        )
    )
    dp.callback_query.register(
        choose_user_bank,
        UserExchangeData.filter(
            F.action == 'choose_user_bank',
        )
    )
    dp.callback_query.register(
        choose_new_user_bank_next,
        UserExchangeData.filter(
            F.action == 'choose_new_user_bank'
        )
    )
    dp.callback_query.register(
        use_old_user_bank,
        UserExchangeData.filter(
            F.action == 'user_make_transfer'
        )
    )