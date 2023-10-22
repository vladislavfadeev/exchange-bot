import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram.fsm.context import FSMContext
from aiogram.types.callback_query import CallbackQuery
from aiogram.types import Message
from aiogram import F, Bot, Dispatcher
import pytz

from core.keyboards import home_kb, user_kb
from core.middlwares.routes import r  # Dataclass whith all api routes
from core.middlwares.settigns import appSettings
from core.api_actions.bot_api import SimpleAPI
from core.utils import msg_maker, msg_var
from core.utils.bot_fsm import FSMSteps
from core.utils import msg_var as msg
from core.utils.state_cleaner import user_state_cleaner
from core.utils.notifier import alert_message_sender, transfers_getter_user
from core.keyboards.callbackdata import (
    UserHomeData,
    UserExchangeData,
)
from core.middlwares.exceptions import (
    MaxLenError,
    MinAmountError,
    MaxAmountError,
)


async def start_change(
    call: CallbackQuery, state: FSMContext, api_gateway: SimpleAPI, bot: Bot
):
    """
    Handler is start user change currency process.
    """
    data: dict = await state.get_data()
    messageList: list = data.get("messageList")
    mainMsg: Message = data.get("mainMsg")
    await state.update_data(messageList=[])
    try:
        await bot.delete_message(mainMsg.chat.id, mainMsg.message_id)
    except:
        pass
    if messageList:
        for i in messageList:
            i: Message
            try:
                await bot.delete_message(i.chat.id, i.message_id)
            except:
                pass
    # send message with all currency for user choice
    mainMsg = await bot.send_message(
        call.from_user.id,
        text=msg.currency_choice_1,
        reply_markup=await user_kb.set_sell_currency_button(api_gateway),
    )
    await state.update_data(mainMsg=mainMsg)
    await state.set_state(FSMSteps.USER_CHANGE_STATE)


async def show_offer(
    call: CallbackQuery,
    state: FSMContext,
    callback_data: UserExchangeData,
    api_gateway: SimpleAPI,
    bot: Bot,
):
    """
    Show all available offers for the selected currency
    """
    type = "buy" if callback_data.action == "buy_currency" else "sell"
    # prepare filter params and get from backend all matching offers
    params = {
        "currency": callback_data.name,
        "type": type,
        "isActive": True,
        "isDeleted": False,
        "owner__online": True,
    }
    response: dict = await api_gateway.get(
        path=r.userRoutes.offer, params=params, exp_code=[200]
    )
    exception: bool = response.get("exception")
    if not exception:
        offers_list: list = response.get("response")
        if offers_list:
            # if response is not empty
            await state.update_data(selected_curr_id=callback_data.id)
            await state.update_data(offerList=offers_list)
            await call.message.delete()
            # create 'messageList' varible containing all offer messages,
            # and send all offers to user
            messageList = []
            for offer in offers_list:
                self_msg: Message = await bot.send_message(
                    call.from_user.id,
                    text=await msg_maker.offer_list_msg_maker(offer),
                    reply_markup=await user_kb.show_offer_list_kb(offer),
                )
                messageList.append(self_msg)
            # add back to main menu message
            sep_msg: Message = await bot.send_message(
                call.from_user.id,
                text=msg.separator,
                reply_markup=await home_kb.user_back_home_inline_button(),
            )
            messageList.append(sep_msg)
            await state.update_data(messageList=messageList)
        else:
            # if response is empty
            await call.message.edit_text(
                text=msg.zero_offer,
                reply_markup=await user_kb.user_cancel_buttons_offerslist(),
            )
    else:
        await alert_message_sender(bot, call.from_user.id)


async def set_amount(
    call: CallbackQuery, state: FSMContext, callback_data: UserExchangeData, bot: Bot
):
    """
    When user made a choice, he need set amount of transfer
    """
    if callback_data.action == "user_exchange_set_amount" and callback_data.is_returned:
        # if user was returned from next step and want
        # set new transfer amount
        data: dict = await state.get_data()
        offerData: dict = data.get("selectedOffer")
        await call.message.edit_text(
            text=await msg_maker.set_amount_returned_msg_maker(offerData),
            reply_markup=await home_kb.user_back_home_inline_button(),
        )
    else:
        tz: pytz = appSettings.botSetting.tz
        data: dict = await state.get_data()
        await state.update_data(user_start_change_time=tz.localize(datetime.now()))
        await state.update_data(messageList=[])
        # get selected offer info
        for i in data.get("offerList"):
            if i["id"] == callback_data.id:
                await state.update_data(selectedOffer=i)
                await state.update_data(offerList={})
                offerData = i
        # get all messages whith offers from previous step
        # and delete it
        msg_list: dict = data.get("messageList")
        for i in msg_list:
            i: Message
            await bot.delete_message(i.chat.id, i.message_id)
        mainMsg: Message = await bot.send_message(
            call.from_user.id,
            text=await msg_maker.set_amount_msg_maker(offerData),
            reply_markup=await home_kb.user_back_home_inline_button(),
        )
        await state.update_data(mainMsg=mainMsg)
    # set state for next step
    await state.set_state(FSMSteps.SET_AMOUNT_STATE)


async def set_amount_check(message: Message, state: FSMContext):
    """
    Handler accepts message from user and make validation
    """
    data: dict = await state.get_data()
    offerData: dict = data.get("selectedOffer")
    mainMsg: Message = data.get("mainMsg")
    await message.delete()
    # make validation
    try:
        value = message.text
        amount = float(value.replace(",", ".").replace(" ", ""))

        if offerData["minAmount"] != None:
            if amount < offerData["minAmount"]:
                raise MinAmountError()

        if offerData["maxAmount"] != None:
            if amount > offerData["maxAmount"]:
                raise MaxAmountError()
    except ValueError as e:
        await mainMsg.edit_text(
            text=msg_var.type_error_msg,
            reply_markup=await user_kb.user_return_to_offer_choice_button(offerData),
        )
    except MinAmountError as e:
        await mainMsg.edit_text(
            text=await msg_maker.min_amount_error_msg_maker(offerData),
            reply_markup=await user_kb.user_return_to_offer_choice_button(offerData),
        )
    except MaxAmountError as e:
        await mainMsg.edit_text(
            text=await msg_maker.max_amount_error_msg_maker(offerData),
            reply_markup=await user_kb.user_return_to_offer_choice_button(offerData),
        )
    else:
        # if value is valid
        await state.update_data(sellAmount=amount)
        await mainMsg.edit_text(
            text=await msg_maker.show_user_buy_amount(
                amount, offerData["rate"], offerData["currency"], offerData["type"]
            ),
            reply_markup=await user_kb.set_amount_check_inlkb(),
        )
        await state.set_state(FSMSteps.USER_CHANGE_STATE)


async def choose_changer_bank(
    call: CallbackQuery,
    state: FSMContext,
    callback_data: UserExchangeData,
    api_gateway: SimpleAPI,
    bot: Bot,
):
    """
    There user select changer bank wich it will be comfortable
    for him to make money transfer
    """
    data: dict = await state.get_data()
    offer_data: dict = data.get("selectedOffer")
    offer_type: str = offer_data.get("type")
    offer_id: int = offer_data.get("id")
    # get changer bank account depending of the offer type
    if offer_type == "buy":
        currency = offer_data.get("currency")
        params = {
            "owner": offer_data.get("owner"),
            "isActive": True,
            "currency__name": currency,
            "offers_curr__id": offer_id,
        }
    elif offer_type == "sell":
        currency = "MNT"
        params = {
            "owner": offer_data.get("owner"),
            "isActive": True,
            "currency__name": currency,
            "offers_ref__id": offer_id,
        }
    response: dict = await api_gateway.get(
        path=r.userRoutes.changerBanks, params=params, exp_code=[200]
    )
    exception: bool = response.get("exception")
    if not exception:
        banks: list = response.get("response")
        await call.message.edit_text(
            text=await msg_maker.set_changer_bank(currency),
            reply_markup=await user_kb.set_changer_bank(banks),
        )
    else:
        await alert_message_sender(bot, call.from_user.id)


async def choose_user_bank(
    call: CallbackQuery,
    state: FSMContext,
    callback_data: UserExchangeData,
    api_gateway: SimpleAPI,
    bot: Bot,
):
    """
    Bot chek availability of bank accounts. If it does
    not exists - bot suggest create new.
    """
    # await state.set_state(FSMSteps.SET_BUY_BANK_INIT)
    data: dict = await state.get_data()
    offer: dict = data.get("selectedOffer")
    offer_type: str = offer.get("type")
    # check user banks accounts depending of the offer type
    if offer_type == "buy":
        currency: str = "MNT"
        params = {
            "owner": call.from_user.id,
            "isActive": True,
            "currency__name": currency,
        }
    elif offer_type == "sell":
        currency: str = offer.get("currency")
        params = {
            "owner": call.from_user.id,
            "isActive": True,
            "currency__name": currency,
        }
    banks: dict = await api_gateway.get(
        path=r.userRoutes.userBanks, params=params, exp_code=[200]
    )
    b_exception: bool = banks.get("exception")
    if not b_exception:
        banks_data: list = banks.get("response")
        # if user have bank account for offer currency
        if banks_data and callback_data.name != "set_new":
            await state.update_data(changerBank=callback_data.id)
            await call.message.edit_text(
                text=await msg_maker.choose_user_bank_from_db(currency),
                reply_markup=await user_kb.choose_user_bank_from_db(banks_data),
            )
        # if accounts does not exists or user want create new
        else:
            if currency in ["RUB"]:
                if callback_data.name != "set_new":
                    await state.update_data(changerBank=callback_data.id)
                await call.message.edit_text(
                    text=await msg_maker.enter_user_bank_name(currency)
                )
                await state.set_state(FSMSteps.USER_ENTER_BANK_NAME)
            else:
                banksName: dict = await api_gateway.get(
                    path=r.userRoutes.banksNameList, exp_code=[200]
                )
                bn_exception: bool = banksName.get("exception")
                if not bn_exception:
                    banks_name_data: list = banksName.get("response")
                    if callback_data.name != "set_new":
                        await state.update_data(changerBank=callback_data.id)
                    await call.message.edit_text(
                        text=await msg_maker.set_user_bank_name(currency),
                        reply_markup=await user_kb.choose_bank_name_from_list(
                            banks_name_data
                        ),
                    )
                else:
                    await alert_message_sender(bot, call.from_user.id)
    else:
        await alert_message_sender(bot, call.from_user.id)


async def user_new_bank_name_setter(message: Message, state: FSMContext, bot: Bot):
    """
    If user need enter his bank account name manualy.
    """
    await message.delete()
    data: dict = await state.get_data()
    mainMsg: Message = data.get("mainMsg")
    offer: dict = data.get("selectedOffer")
    offer_type: str = offer.get('type')
    currency: str = offer.get("currency")

    try:
        value: str = message.text
        if len(value) > 20:
            raise MaxLenError
    except MaxLenError as e:
        await mainMsg.edit_text(
            text=await msg_maker.user_max_len_message(len(value)),
            reply_markup=await user_kb.user_cancel_button(),
        )
    else:
        await state.update_data(userBank=value)
        await mainMsg.edit_text(
            text=await msg_maker.set_buy_bank_account(value, currency, offer_type),
            reply_markup=await home_kb.user_back_home_inline_button(),
        )
        await state.set_state(FSMSteps.SET_BUY_BANK_ACCOUNT)


async def choose_new_user_bank_next(
    call: CallbackQuery, state: FSMContext, callback_data: UserExchangeData
):
    """
    This handler calling if user want create new bank account,
    when he set name of bank on previous step (choose_user_bank)
    """
    data: dict = await state.get_data()
    offer: dict = data.get("selectedOffer")
    offer_type: str = offer.get('type')
    currency: str = offer.get("currency")
    # set bank name to bot state
    await state.update_data(userBank=callback_data.name)
    # set FSM state for correctly work next handler
    await state.set_state(FSMSteps.SET_BUY_BANK_ACCOUNT)
    await call.message.edit_text(
        text=await msg_maker.set_buy_bank_account(callback_data.name, currency, offer_type),
        reply_markup=await home_kb.user_back_home_inline_button(),
    )


async def apply_new_user_bank(
    message: Message, state: FSMContext, api_gateway: SimpleAPI, bot: Bot
):
    """
    Handler get message value and make it valid. If all ok - try
    create new user bank account. Account number must be unique,
    if it's not - account will not be created.
    """
    await message.delete()
    data: dict = await state.get_data()
    bankName: str = data.get("userBank")
    offer: dict = data.get("selectedOffer")
    curr_id: int = data.get("selected_curr_id")
    mainMsg: Message = data.get("mainMsg")
    try:
        account = int(message.text)
    except ValueError as e:
        await mainMsg.edit_text(
            text=msg.account_value_error,
            reply_markup=await user_kb.final_transfer_stage(),
        )
    except Exception as e:
        await mainMsg.edit_text(
            text=msg.account_exception,
            reply_markup=await user_kb.final_transfer_stage(),
        )
    else:
        offer_type = offer.get("type")
        currency = curr_id if offer_type == "sell" else 3  # check id from db
        postData = {  # it is ID of MNT currency
            "name": bankName,
            "bankAccount": account,
            "owner": message.from_user.id,
            "currency": currency,
            "isActive": True,
        }
        response: dict = await api_gateway.post(
            path=r.userRoutes.userBanks, data=postData, exp_code=[201, 400]
        )
        status_code: int = response.get("status_code")
        if status_code == 201:
            user_account: dict = response.get("response")
            await mainMsg.edit_text(
                text=await msg_maker.complete_set_new_bank(data, api_gateway),
                reply_markup=await home_kb.user_back_home_inline_button(),
            )
            await state.update_data(userAccount=user_account.get("id"))
            await state.update_data(final_step=True)
            await state.set_state(FSMSteps.GET_USER_PROOF)
        elif status_code == 400:
            response_data: dict = response.get("response")
            await mainMsg.edit_text(
                text=await msg_maker.error_set_new_bank(account),
                reply_markup=await user_kb.final_transfer_stage(),
            )
            logging.warning(response_data)
        else:
            await alert_message_sender(bot, message.from_user.id)


async def use_old_user_bank(
    call: CallbackQuery,
    state: FSMContext,
    bot: Bot,
    api_gateway: SimpleAPI,
    callback_data: UserExchangeData,
):
    """
    Handler calling if user have available bank account
    """
    data = await state.get_data()
    accountId = callback_data.id
    # try to get full data of user bank account by account_id
    response: dict = await api_gateway.get_detail(
        path=r.userRoutes.userBanks, detailUrl=accountId, exp_code=[200]
    )
    exception: bool = response.get("exception")
    if not exception:
        user_account: dict = response.get("response")
        await state.update_data(userAccount=user_account.get("id"))
        await call.message.edit_text(
            text=await msg_maker.complete_set_new_bank(data, api_gateway),
            reply_markup=await home_kb.user_back_home_inline_button(),
        )
        await state.update_data(final_step=True)
        await state.set_state(FSMSteps.GET_USER_PROOF)
    else:
        await alert_message_sender(bot, call.from_user.id)


async def get_user_proof(
    message: Message,
    state: FSMContext,
    apscheduler: AsyncIOScheduler,
    api_gateway: SimpleAPI,
    bot: Bot,
):
    """
    This handler get file or foto whit user proof that
    he make money transfer and create transaction on backend
    """
    data: dict = await state.get_data()
    selected_offer: dict = data.get("selectedOffer")
    mainMsg: Message = data.get("mainMsg")
    changerId: int = selected_offer.get("owner")
    offerId: int = selected_offer.get("id")
    changerBank: int = data.get("changerBank")
    userBank: int = data.get("userAccount")
    sellCurrency: str = selected_offer.get("currency")
    sellAmount: float = data.get("sellAmount")
    rate: float = selected_offer.get("rate")
    type: str = selected_offer.get("type")
    buyAmount: float = round(sellAmount * rate)
    accountId: int = message.from_user.id
    # delete user proof message from screen
    await message.delete()
    # check message type, supported only image and other
    # files. For example -pdf
    try:
        if message.photo:
            fileId = message.photo[-1].file_id
            proofType = "photo"
        elif message.document:
            fileId = message.document.file_id
            proofType = "document"
        else:
            raise TypeError()
    except TypeError:
        # inform user about error and delete this message
        # after 3 seconds
        del_msg: Message = await bot.send_message(
            message.from_user.id, text=msg.type_error_message
        )
        await asyncio.sleep(3)
        try:
            await del_msg.delete()
        except:
            pass
    else:
        post_data = {
            "changer": changerId,
            "offer": offerId,
            "user": accountId,
            "changerBank_id": changerBank,
            "userBank_id": userBank,
            "offerCurrency": sellCurrency,
            "refCurrency": "MNT",
            "sellAmount": sellAmount,
            "buyAmount": buyAmount,
            "rate": rate,
            "userSendMoneyDate": datetime.now(),
            "userProofType": proofType,
            "userProof": fileId,
            "type": type,
            "isCompleted": False,
            "claims": False,
            "changerAccepted": False,
        }
        response: dict = await api_gateway.post(
            path=r.userRoutes.transactions, data=post_data, exp_code=[201]
        )
        exception: bool = response.get("exception")
        if not exception:
            curr: str = "MNT" if type == "buy" else sellCurrency
            amount: int = sellAmount if type == "sell" else buyAmount
            # if all checks were sucsessful bot create new
            # task that will track the exchanger's response
            await mainMsg.edit_text(
                text=await msg_maker.user_inform(amount, curr),
                reply_markup=await user_kb.final_transfer_stage(),
            )
            await user_state_cleaner(state)
            await state.set_state(FSMSteps.USER_WAIT_INCOME_TR)
            # check if the task is not in joblist add it in
            getter_id = f"user_getter-{message.from_user.id}"
            job_list: list = apscheduler.get_jobs()
            job_id_list: list = [job.id for job in job_list]
            if getter_id not in job_id_list:
                apscheduler.add_job(
                    transfers_getter_user,
                    "interval",
                    minutes=1,
                    id=getter_id,
                    kwargs={
                        "user_id": message.from_user.id,
                    },
                )
        else:
            await alert_message_sender(bot, message.from_user.id)


async def setup_exchande_handlers(dp: Dispatcher):
    """Registry message handlers there."""
    dp.message.register(set_amount_check, FSMSteps.SET_AMOUNT_STATE, F.text)
    dp.message.register(
        user_new_bank_name_setter, FSMSteps.USER_ENTER_BANK_NAME, F.text
    )
    dp.message.register(apply_new_user_bank, FSMSteps.SET_BUY_BANK_ACCOUNT, F.text)
    dp.message.register(
        get_user_proof,
        # F.content_type.in_({'photo', 'document'}),
        FSMSteps.GET_USER_PROOF,
    )
    dp.callback_query.register(
        start_change,
        UserHomeData.filter(F.action == "change"),
    )
    dp.callback_query.register(
        show_offer,
        UserExchangeData.filter(F.action.in_({"buy_currency", "sell_currency"})),
    )
    dp.callback_query.register(
        set_amount, UserExchangeData.filter(F.action == "user_exchange_set_amount")
    )
    dp.callback_query.register(
        choose_changer_bank, UserExchangeData.filter(F.action == "choose_changer_bank")
    )
    dp.callback_query.register(
        choose_user_bank,
        UserExchangeData.filter(
            F.action == "choose_user_bank",
        ),
    )
    dp.callback_query.register(
        choose_new_user_bank_next,
        UserExchangeData.filter(F.action == "choose_new_user_bank"),
    )
    dp.callback_query.register(
        use_old_user_bank, UserExchangeData.filter(F.action == "user_make_transfer")
    )
