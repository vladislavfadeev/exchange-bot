from aiogram.fsm.context import FSMContext
from aiogram.types.callback_query import CallbackQuery
from aiogram.types import Message
from aiogram import F, Bot, Dispatcher

from core.middlwares.routes import r  # Dataclass whith all api routes
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
from core.utils.notifier import alert_message_sender


async def offer_menu(call: CallbackQuery, state: FSMContext, bot: Bot):
    """ """
    await state.set_state(FSMSteps.STUFF_OFFERS_MENU)
    data: dict = await state.get_data()
    mainMsg: Message = data.get("mainMsg")
    messageList: list = data.get("messageList")

    try:
        await mainMsg.delete()
    except:
        pass

    if messageList:
        for i in messageList:
            i: Message

            try:
                await bot.delete_message(i.chat.id, i.message_id)
            except:
                pass

    mainMsg: Message = await bot.send_message(
        call.from_user.id,
        text=await msg_maker.stuff_offer_menu(),
        reply_markup=await changer_kb.stuff_offer_menu_buttons(),
    )
    await state.update_data(mainMsg=mainMsg)
    await state.update_data(editable_accounts={})
    await state.update_data(accounts={})


async def offer_menu_give_result(
    call: CallbackQuery,
    state: FSMContext,
    callback_data: StaffOfficeData,
    api_gateway: SimpleAPI,
    bot: Bot,
):
    """ """
    if callback_data.action == "create_new":
        # start to create new offer
        await call.message.edit_text(
            text=await msg_maker.stuff_set_currency(),
            reply_markup=await changer_kb.set_sell_currency_button(api_gateway),
        )
    else:
        # if user want see or chage alailable offers.
        # prepare filter params depends of user choice
        if callback_data.action == "edit_offers":
            params = {"owner": call.from_user.id, "isActive": True, "isDeleted": False}
            draft: bool = False
        elif callback_data.action == "inactive":
            params = {"owner": call.from_user.id, "isActive": False, "isDeleted": False}
            draft: bool = True
        # try to get data from backend
        response: dict = await api_gateway.get(
            path=r.changerRoutes.myOffers, params=params, exp_code=[200]
        )
        exception: bool = response.get("exception")
        if not exception:
            offer_list: list = response.get("response")
            if offer_list:
                # if response is not empty
                await call.message.delete()
                await state.update_data(offerList=offer_list)
                # create 'messageList' varible containing all offer messages,
                # and send all offers to user
                messageList = []
                for offer in offer_list:
                    self_msg: Message = await bot.send_message(
                        call.from_user.id,
                        text=await msg_maker.offer_list_msg_maker(offer),
                        reply_markup=await changer_kb.stuff_edit_offer_list_buttons(
                            offer["id"], draft
                        ),
                    )
                    messageList.append(self_msg)
                # add back to main menu message
                sep_msg: Message = await bot.send_message(
                    call.from_user.id,
                    text=msg.separator,
                    reply_markup=await changer_kb.staff_back_to_offer_menu(),
                )
                messageList.append(sep_msg)
                await state.update_data(messageList=messageList)
            else:
                # if response is empty
                await call.message.edit_text(
                    text=msg.stuff_zero_offer,
                    reply_markup=await changer_kb.sfuff_cancel_button(),
                )
        else:
            await alert_message_sender(bot, call.from_user.id)


async def setup_menu_handlers(dp: Dispatcher):
    """Register callback_querry handlers there."""
    dp.callback_query.register(
        offer_menu,
        StaffOfficeData.filter(F.action == "offers"),
    )
    dp.callback_query.register(
        offer_menu_give_result,
        StaffOfficeData.filter(F.action.in_({"create_new", "edit_offers", "inactive"})),
    )
