import logging
from types import NoneType

from aiogram.fsm.context import FSMContext
from aiogram.types.callback_query import CallbackQuery
from aiogram.types import Message
from aiogram import F, Bot, Dispatcher

from core.middlwares.routes import r  # Dataclass whith all api routes
from core.utils import msg_maker
from core.api_actions.bot_api import SimpleAPI
from core.middlwares.settigns import appSettings
from core.utils.bot_fsm import FSMSteps
from core.utils import msg_var as msg
from core.middlwares.exceptions import MaxLenError
from core.keyboards import (
    changer_kb,
)
from core.keyboards.callbackdata import (
    StaffEditData,
)
from core.utils.notifier import alert_message_sender


async def staff_edit_offer(
    call: CallbackQuery,
    state: FSMContext,
    callback_data: StaffEditData,
    api_gateway: SimpleAPI,
    bot: Bot,
):
    """ """
    offer_id = callback_data.id
    response: dict = await api_gateway.get_detail(
        path=r.changerRoutes.myOffers, detailUrl=offer_id, exp_code=[200]
    )
    exception: bool = response.get("exception")
    if not exception:
        offer: dict = response.get("response")
        offer_currency: str = offer.get("currency")
        data: dict = await state.get_data()
        msg_list: list = data.get("messageList")
        await state.update_data(editable_offer_id=offer_id)
        await state.update_data(offer_currency=offer_currency)
        for i in msg_list:
            i: Message
            try:
                await bot.delete_message(i.chat.id, i.message_id)
            except:
                pass
        mainMsg = await bot.send_message(
            call.from_user.id,
            text=await msg_maker.staff_edit_offer_show(offer),
            reply_markup=await changer_kb.staff_edit_offer_show_kb(offer),
        )
        await state.update_data(mainMsg=mainMsg)
    else:
        await alert_message_sender(bot, call.from_user.id)


async def staff_edit_offer_steps(
    call: CallbackQuery, state: FSMContext, callback_data: StaffEditData
):
    """ """
    data: dict = await state.get_data()
    currency: str = data.get("offer_currency")

    if callback_data.action == "staff_edit_offer_name":
        await call.message.edit_text(
            text=msg.staff_set_offer_name,
            reply_markup=await changer_kb.staff_back_to_offer_menu(),
        )
        await state.update_data(editable_key="bannerName")
        await state.set_state(FSMSteps.STAFF_EDIT_VALUES)

    elif callback_data.action == "staff_edit_offer_rate":
        await call.message.edit_text(
            text=msg.staff_edit_offer_new_rate,
            reply_markup=await changer_kb.staff_back_to_offer_menu(),
        )
        await state.update_data(editable_key="rate")
        await state.set_state(FSMSteps.STAFF_EDIT_VALUES)

    elif callback_data.action == "staff_edit_offer_min_amount":
        await call.message.edit_text(
            text=await msg_maker.staff_set_min_amount(currency),
            reply_markup=await changer_kb.staff_back_to_offer_menu(),
        )
        await state.update_data(editable_key="minAmount")
        await state.set_state(FSMSteps.STAFF_EDIT_VALUES)

    elif callback_data.action == "staff_edit_offer_max_amount":
        await call.message.edit_text(
            text=await msg_maker.stuff_set_max_amount(currency),
            reply_markup=await changer_kb.staff_back_to_offer_menu(),
        )
        await state.update_data(editable_key="maxAmount")
        await state.set_state(FSMSteps.STAFF_EDIT_VALUES)


async def staff_edit_offer_values_checker(message: Message, state: FSMContext):
    """ """
    await message.delete()
    data: dict = await state.get_data()
    editable_key: str = data.get("editable_key")
    mainMsg: Message = data.get("mainMsg")
    currency: str = data.get("offer_currency")
    if editable_key == "bannerName":
        try:
            description: str = message.text
            if len(description) > 50:
                raise MaxLenError
        except MaxLenError:
            await mainMsg.edit_text(
                text=await msg_maker.staff_max_len_message(len(description)),
                reply_markup=await changer_kb.sfuff_cancel_button(),
            )
        else:
            await state.update_data(editable_field=description)
            decline_edit_name = "staff_edit_offer_name"
            await mainMsg.edit_text(
                text=await msg_maker.staff_show_offer_name(description),
                reply_markup=await changer_kb.staff_edit_offer_values(
                    decline_edit_name
                ),
            )

    elif editable_key == "rate":
        try:
            value: str = message.text
            rate: float = float(value.replace(",", ".").replace(" ", ""))
        except (ValueError, AttributeError) as e:
            await mainMsg.edit_text(
                text=msg.staff_edit_offer_new_rate_error,
                reply_markup=await changer_kb.sfuff_cancel_button(),
            )
        else:
            await state.update_data(editable_field=rate)
            decline_edit_rate = "staff_edit_offer_rate"
            await mainMsg.edit_text(
                text=await msg_maker.stuff_show_rate(rate, currency),
                reply_markup=await changer_kb.staff_edit_offer_values(
                    decline_edit_rate
                ),
            )

    elif editable_key in ["minAmount", "maxAmount"]:
        try:
            value: str = message.text
            amount: float = float(value.replace(",", ".").replace(" ", ""))
        except ValueError as e:
            logging.error(e)
            await mainMsg.edit_text(
                text=msg.type_error_msg,
                reply_markup=await changer_kb.sfuff_cancel_button(),
            )
        else:
            await state.update_data(editable_field=amount)
            if editable_key == "minAmount":
                decline_edit_min_sum = "staff_edit_offer_min_amount"
                await mainMsg.edit_text(
                    text=await msg_maker.stuff_show_min_amount(amount, currency),
                    reply_markup=await changer_kb.staff_edit_offer_values(
                        decline_edit_min_sum
                    ),
                )
            elif editable_key == "maxAmount":
                decline_edit_max_sum = "staff_edit_offer_max_amount"
                await mainMsg.edit_text(
                    text=await msg_maker.stuff_show_max_amount(amount, currency),
                    reply_markup=await changer_kb.staff_edit_offer_values(
                        decline_edit_max_sum
                    ),
                )
    await state.set_state(FSMSteps.STUFF_OFFERS_MENU)


async def staff_edit_offer_banks(
    call: CallbackQuery,
    state: FSMContext,
    callback_data: StaffEditData,
    api_gateway: SimpleAPI,
    bot: Bot,
):
    """ """
    data: dict = await state.get_data()
    currency: str = data.get("offer_currency")
    params_curr = {
        "owner": call.from_user.id,
        "isActive": True,
        "currency__name": currency,
    }
    params_ref = {"owner": call.from_user.id, "isActive": True, "currency__name": "MNT"}
    response_curr: dict = await api_gateway.get(
        path=r.changerRoutes.banks, params=params_curr, exp_code=[200]
    )
    response_ref: dict = await api_gateway.get(
        path=r.changerRoutes.banks, params=params_ref, exp_code=[200]
    )
    exception_curr: bool = response_curr.get("exception")
    exception_ref: bool = response_ref.get("exception")
    if not exception_curr and not exception_ref:
        banks: list = response_curr.get("response")
        banks.extend(response_ref.get("response"))
        if callback_data.action == "staff_edit_offer_banks":
            offer_id: int = callback_data.id
            await state.update_data(editable_offer_id=offer_id)
            if banks:
                await call.message.edit_text(
                    text=await msg_maker.stuff_create_new_offer_banks(currency),
                    reply_markup=await changer_kb.stuff_edit_offer_banks_dis_next(
                        banks
                    ),
                )
            else:
                await call.message.edit_text(
                    text=msg.staff_zero_banks,
                    reply_markup=await changer_kb.staff_zero_banks_buttons(),
                )

        elif callback_data.action == "staff_edit_offer_banks_set":
            await call.answer()
            account_id: int = callback_data.id
            accounts: dict | NoneType = data.get("editable_accounts")
            if not accounts:
                accounts = {}
                for i in banks:
                    accounts[i["currency"]["name"]] = []
            for i in banks:
                if i["id"] == account_id:
                    if i not in accounts[currency] and i not in accounts["MNT"]:
                        accounts[i["currency"]["name"]].append(i)

            await state.update_data(editable_accounts=accounts)

            await call.message.edit_text(
                text=await msg_maker.stuff_create_new_offer_banks(currency, accounts),
                reply_markup=await changer_kb.stuff_edit_offer_banks(banks),
            )
        elif callback_data.action == "staff_edit_offer_banks_patch":
            accounts: dict = data.get("editable_accounts")

            if not accounts.get(currency):
                await call.answer(f"Вы не указали банк для {currency}", show_alert=True)

            if not accounts.get("MNT"):
                await call.answer(f"Вы не указали банк для MNT", show_alert=True)

            elif accounts.get(currency) and accounts.get("MNT"):
                currency_banks = [i["id"] for i in accounts[currency]]
                ref_banks = [i["id"] for i in accounts["MNT"]]
                offer_id = data.get("editable_offer_id")

                patch_data = {
                    "refBanks_id": ref_banks,
                    "currencyBanks_id": currency_banks,
                }
                response: dict = await api_gateway.patch(
                    path=r.changerRoutes.myOffers,
                    detailUrl=offer_id,
                    data=patch_data,
                    exp_code=[200],
                )
                exception: bool = response.get("exception")
                if not exception:
                    await call.message.edit_text(
                        text=msg.staff_edit_offer_banks_success,
                        reply_markup=await changer_kb.staff_edit_offer_succes_kb(),
                    )
                    await state.update_data()  # What is a fuck ?!
                else:
                    await alert_message_sender(bot, call.from_user.id)
    else:
        await alert_message_sender(bot, call.from_user.id)


async def staff_edit_offer_values_setter(
    call: CallbackQuery,
    state: FSMContext,
    callback_data: StaffEditData,
    api_gateway: SimpleAPI,
    bot: Bot,
):
    """ """
    data: dict = await state.get_data()
    message_list: list = data.get("messageList")
    offer_id: int = callback_data.id

    if callback_data.action == "staff_edit_accept":
        key: str = data.get("editable_key")
        value: str = data.get("editable_field")
        offer_id: int = data.get("editable_offer_id")

        patch_data = {key: value}
        response: dict = await api_gateway.patch(
            path=r.changerRoutes.myOffers,
            detailUrl=offer_id,
            data=patch_data,
            exp_code=[200],
        )
        exception: bool = response.get("exception")
        if not exception:
            await call.message.edit_text(
                text=msg.staff_edit_offer_success,
                reply_markup=await changer_kb.staff_edit_offer_succes_kb(),
            )
        else:
            await alert_message_sender(bot, call.from_user.id)

    elif callback_data.action == "staff_delete_offer":
        patch_data = {"isDeleted": True}
        response: dict = await api_gateway.patch(
            path=r.changerRoutes.myOffers,
            detailUrl=offer_id,
            data=patch_data,
            exp_code=[200],
        )
        exception: bool = response.get("exception")
        if not exception:
            await call.answer("Выполнено!", show_alert=True)
            if len(message_list) > 1:
                await call.message.delete()

            elif len(message_list) == 1:
                await call.message.edit_text(
                    text=await msg_maker.stuff_offer_menu(),
                    reply_markup=await changer_kb.stuff_offer_menu_buttons(),
                )
            await state.set_state(FSMSteps.STAFF_HOME_STATE)
        else:
            await call.answer(msg.error_msg, show_alert=True)

    elif callback_data.action == "staff_publish_offer":
        value: bool = True
        data: dict = await state.get_data()
        offer_data: dict = [i for i in data["offerList"] if i["id"] == offer_id][0]
        ref_banks: list = offer_data.get("refBanks")
        curr_banks: list = offer_data.get("currencyBanks")

        if ref_banks and curr_banks:
            patch_data = {"isActive": value}
            response: dict = await api_gateway.patch(
                path=r.changerRoutes.myOffers,
                detailUrl=offer_id,
                data=patch_data,
                exp_code=[200],
            )
            exception: bool = response.get("exception")
            if not exception:
                await call.answer("Выполнено!", show_alert=True)
                if len(message_list) > 1:
                    await call.message.delete()
                elif len(message_list) == 1:
                    await call.message.edit_text(
                        text=await msg_maker.stuff_offer_menu(),
                        reply_markup=await changer_kb.stuff_offer_menu_buttons(),
                    )
                await state.set_state(FSMSteps.STAFF_HOME_STATE)
            else:
                await call.answer(msg.error_msg, show_alert=True)
        else:
            await call.answer("Не указан банк для одной из валют!", show_alert=True)

    elif callback_data.action == "staff_unpublish_offer":
        value: bool = False

        patch_data = {"isActive": value}
        response: dict = await api_gateway.patch(
            path=r.changerRoutes.myOffers,
            detailUrl=offer_id,
            data=patch_data,
            exp_code=[200],
        )
        exception: bool = response.get("exception")
        if not exception:
            await call.answer("Выполнено!", show_alert=True)
            if len(message_list) > 1:
                await call.message.delete()
            elif len(message_list) == 1:
                await call.message.edit_text(
                    text=await msg_maker.stuff_offer_menu(),
                    reply_markup=await changer_kb.stuff_offer_menu_buttons(),
                )
            await state.set_state(FSMSteps.STAFF_HOME_STATE)
        else:
            await call.answer(msg.error_msg, show_alert=True)


async def setup_edit_offers_handlers(dp: Dispatcher):
    """Register callback_querry handlers there."""
    dp.message.register(
        staff_edit_offer_values_checker, FSMSteps.STAFF_EDIT_VALUES, F.text
    )
    dp.callback_query.register(
        staff_edit_offer, StaffEditData.filter(F.action == "staff_edit_offer")
    )
    dp.callback_query.register(
        staff_edit_offer_steps,
        StaffEditData.filter(
            F.action.in_(
                {
                    "staff_edit_offer_name",
                    "staff_edit_offer_rate",
                    "staff_edit_offer_min_amount",
                    "staff_edit_offer_max_amount",
                }
            )
        ),
    )
    dp.callback_query.register(
        staff_edit_offer_values_setter,
        StaffEditData.filter(
            F.action.in_(
                {
                    "staff_edit_accept",
                    "staff_delete_offer",
                    "staff_publish_offer",
                    "staff_unpublish_offer",
                    "staff_edit_banks_active",
                    "staff_edit_banks_inactive",
                    "staff_edit_banks_delete",
                }
            )
        ),
    )
    dp.callback_query.register(
        staff_edit_offer_banks,
        StaffEditData.filter(
            F.action.in_(
                {
                    "staff_edit_offer_banks",
                    "staff_edit_offer_banks_set",
                    "staff_edit_offer_banks_patch",
                }
            )
        ),
    )
