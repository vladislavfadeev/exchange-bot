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


async def start_change_crypto(
    call: CallbackQuery, state: FSMContext, api_gateway: SimpleAPI, bot: Bot
):
    """
    Handler is start user change crypto currency process.
    """
    data: dict = await state.get_data()
    messageList: list = data.get("messageList")
    mainMsg: Message = data.get("mainMsg")

    # get all crypto pairs and
    # send message with all pairs for user choice
    params = {
        "is_active": True,
        "owner__online": True,
    }
    response: dict = await api_gateway.get(
        path=r.keysRoutes.cr_currency_list, params=params, exp_code=[200]
    )
    exception: bool = response.get("exception")
    if not exception:
        crypto_rate_list: list = response.get("response")
        # print(crypto_rate_list)
        if crypto_rate_list:
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
            await state.update_data(crypto_rate_list=crypto_rate_list)
            messageList = []
            for offer in crypto_rate_list:
                self_msg = await bot.send_message(
                    call.from_user.id,
                    text=await msg_maker.crypto_offer_list_msg_maker(offer),
                    reply_markup=await user_kb.crypto_offer_list_kb_maker(offer),
                )
                messageList.append(self_msg)
            sep_msg: Message = await bot.send_message(
                call.from_user.id,
                text=msg.separator,
                reply_markup=await home_kb.user_back_home_inline_button(),
            )
            messageList.append(sep_msg)
            await state.update_data(messageList=messageList)
            await state.set_state(
                FSMSteps.USER_CR_CHANGE_STATE  ###!!!!!!!!!!!!!!!!!!!!!!!!!!
            )  # проверить соответствие состояния!!!!!!!!!
        else:
            # if response is empty
            await call.message.edit_text(
                text="На данный момент предложения отсутствуют, либо нет обменников онлайн",
                reply_markup=await user_kb.user_cancel_button(),
            )
    else:
        await alert_message_sender(bot, call.from_user.id)


async def set_crypto_amount(
    call: CallbackQuery, state: FSMContext, callback_data: UserExchangeData, bot: Bot
):
    """
    When user made a choice, he need set amount of transfer
    """
    if callback_data.is_returned:
        # if user was returned from next step and want
        # set new transfer amount
        data: dict = await state.get_data()
        offerData: dict = data.get("selectedOffer")
        await call.message.edit_text(
            text=await msg_maker.set_cr_amount_returned_msg_maker(offerData),
            reply_markup=await home_kb.user_back_home_inline_button(),
        )
    else:
        tz: pytz = appSettings.botSetting.tz
        data: dict = await state.get_data()
        await state.update_data(user_start_change_time=tz.localize(datetime.now()))
        # get selected offer info
        cr_exch_type = "sell" if "sell" in callback_data.action else "buy"
        # print(cr_exch_type)
        await state.update_data(offerList={})
        crypto_rate_list = data.get("crypto_rate_list")
        choosen_pair = [x for x in crypto_rate_list if x["id"] == callback_data.id][0]
        await state.update_data(selectedOffer=choosen_pair)
        # print(choosen_pair)
        # get all messages whith offers from previous step
        # and delete it
        msg_list: dict = data.get("messageList")
        for i in msg_list:
            i: Message
            await bot.delete_message(i.chat.id, i.message_id)
        await state.update_data(messageList=[])
        mainMsg: Message = await bot.send_message(
            call.from_user.id,
            text=await msg_maker.set_cr_amount_msg_maker(choosen_pair),
            reply_markup=await home_kb.user_back_home_inline_button(),
        )
        await state.update_data(mainMsg=mainMsg)
        await state.update_data(cr_exch_type=cr_exch_type)
    # set state for next step
    await state.set_state(FSMSteps.SET_CR_AMOUNT_STATE)


async def set_cr_amount_check(message: Message, state: FSMContext):
    """
    Handler accepts message from user and make validation
    """
    data: dict = await state.get_data()
    offer_data: dict = data.get("selectedOffer")
    cr_exch_type: dict = data.get("cr_exch_type")
    mainMsg: Message = data.get("mainMsg")
    await message.delete()
    # make validation
    try:
        value = message.text
        amount = float(value.replace(",", ".").replace(" ", ""))

        if offer_data["min_amount"] != None:
            if amount < offer_data["min_amount"]:
                raise MinAmountError()

        # if offerData["maxAmount"] != None:
        #     if amount > offerData["maxAmount"]:
        #         raise MaxAmountError()
    except ValueError as e:
        await mainMsg.edit_text(
            text=msg_var.type_error_msg,
            reply_markup=await user_kb.user_return_to_cr_offer_choice_button(),
        )
    except MinAmountError as e:
        await mainMsg.edit_text(
            text=await msg_maker.min_cr_amount_error_msg_maker(offer_data),
            reply_markup=await user_kb.user_return_to_cr_offer_choice_button(),
        )
    else:
        # if value is valid
        await state.update_data(sellAmount=amount)
        await mainMsg.edit_text(
            text=await msg_maker.show_user_buy_cr_amount(
                amount, cr_exch_type, offer_data
            ),
            reply_markup=await user_kb.set_cr_amount_check_inlkb(cr_exch_type),
        )
        await state.set_state(FSMSteps.USER_CR_CHANGE_STATE)


async def create_new_crypto_order(
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
    offer_data: dict = data.get("selectedOffer")
    order_type = data.get("cr_exch_type")
    _type = f"{order_type}_rate"

    user = call.from_user.id
    changer = offer_data['owner']
    pair_name = offer_data['pair_name']
    rate = offer_data[_type]
    sell_amount = data.get('sellAmount')
    buy_amount = round(sell_amount * rate)

    post_data = {
        "user": user,
        "changer": changer,
        "pair_name": pair_name,
        "rate": rate,
        "sell_amount": sell_amount,
        "buy_amount": buy_amount,
        "order_type": order_type
    }

    response: dict = await api_gateway.post(
        path=r.userRoutes.crypto_orders, data=post_data, exp_code=[201]
    )
    exception: bool = response.get("exception")
    if not exception:
        response_data: dict = response.get("response")
        # await state.update_data(userAccount=user_account.get("id"))
        await call.message.edit_text(
            text=await msg_maker.create_new_crypto_order_success(response_data),
            reply_markup=await home_kb.user_back_home_inline_button(),
        )
        # await state.update_data(final_step=True)
        await state.set_state(FSMSteps.USER_CR_FINAL_CHANGE_STATE)
    else:
        await alert_message_sender(bot, call.from_user.id)



async def setup_crypto_exchande_handlers(dp: Dispatcher):
    """Registry message handlers there."""
    dp.message.register(set_cr_amount_check, FSMSteps.SET_CR_AMOUNT_STATE, F.text)
    
    dp.callback_query.register(
        start_change_crypto,
        UserHomeData.filter(F.action == "change_crypto"),
    )
    dp.callback_query.register(
        set_crypto_amount,
        UserExchangeData.filter(
            F.action.in_({"user_cr_ch_set_sell_amount", "user_cr_ch_set_buy_amount"})
        ),
    )
    dp.callback_query.register(
        create_new_crypto_order, UserExchangeData.filter(F.action == "create_crypto_order")
    )
