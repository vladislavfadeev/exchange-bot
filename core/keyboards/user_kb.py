from aiogram.utils.keyboard import InlineKeyboardBuilder
from core.api_actions.bot_api import SimpleAPI
from core.middlwares.routes import r  # Dataclass whith all api routes
from core.middlwares.settigns import appSettings
from core.keyboards.callbackdata import URLData, UserHomeData, UserExchangeData


async def set_sell_currency_button(api_gateway: SimpleAPI):
    """Build InlineKeyboardButton with currency for "start_change" handler."""
    response: dict = await api_gateway.get(path=r.keysRoutes.currencyList)
    exception: bool = response.get("exception")
    if not exception:
        currency: list = response.get("response")
        builder = InlineKeyboardBuilder()

        for curr in currency:
            if curr["name"] == "MNT":
                pass
            else:
                builder.button(
                    text=f'Купить {curr["name"]}',
                    callback_data=UserExchangeData(
                        id=curr["id"],
                        action="sell_currency",
                        name=curr["name"],
                        is_returned=False,
                    ),
                )
                builder.button(
                    text=f'Продать {curr["name"]}',
                    callback_data=UserExchangeData(
                        id=curr["id"],
                        action="buy_currency",
                        name=curr["name"],
                        is_returned=False,
                    ),
                )
        builder.button(
            text="↩ Отменить", callback_data=UserHomeData(action="cancel", id=0)
        )
        builder.adjust(2)

        return builder.as_markup()


async def show_offer_list_kb(offer):
    """
    Build button for offer list
    """
    builder = InlineKeyboardBuilder()
    builder.button(
        text="✅ Обменять здесь",
        callback_data=UserExchangeData(
            id=offer["id"],
            name="",
            action="user_exchange_set_amount",
            is_returned=False,
        ),
    )
    return builder.as_markup()


async def user_cancel_buttons_offerslist():
    """Build RelyKeyboardButton for cancel all process and retun to INIT_STATE."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="↩ Вернуться к выбору валюты",
        callback_data=UserHomeData(action="change", id=0),
    )
    builder.button(
        text="↩ Вернуться на главную", callback_data=UserHomeData(action="cancel", id=0)
    )
    builder.adjust(1)

    return builder.as_markup()


async def user_return_to_offer_choice_button(offerData):
    """Build InlineKeyboardButton with offer id for user choice"""

    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"↩ Вернуться к выбору предложений",
        callback_data=UserExchangeData(
            id=0,
            name=offerData["currency"],
            action=f'{offerData["type"]}_currency',
            is_returned=True,
        ),
    )

    return builder.as_markup()


async def set_amount_check_inlkb():
    """ """
    builder = InlineKeyboardBuilder()
    builder.button(
        text="⤵️ Согласен, продолжить",
        callback_data=UserExchangeData(
            id=0, name="", action="choose_changer_bank", is_returned=False
        ),
    )
    builder.button(
        text="⤴️ Вернуться, ввести другую сумму",
        callback_data=UserExchangeData(
            id=0, name="", action="user_exchange_set_amount", is_returned=True
        ),
    )
    builder.adjust(1)

    return builder.as_markup()


async def set_changer_bank(banks):
    builder = InlineKeyboardBuilder()

    for bank in banks:
        builder.button(
            text=bank["name"],
            callback_data=UserExchangeData(
                id=bank["id"], name="", action="choose_user_bank", is_returned=False
            ),
        )
    builder.adjust(1)

    return builder.as_markup()


async def choose_user_bank_from_db(banks):
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"💰 Указать новый счет",
        callback_data=UserExchangeData(
            id=0, name="set_new", action="choose_user_bank", is_returned=False
        ),
    )

    for bank in banks:
        builder.button(
            text=f'🏦 {bank["name"]}\n💳 {bank["bankAccount"]}',
            callback_data=UserExchangeData(
                id=bank["id"], name="", action="user_make_transfer", is_returned=False
            ),
        )
    builder.adjust(1)

    return builder.as_markup()


async def choose_bank_name_from_list(banksName):
    builder = InlineKeyboardBuilder()

    for bank in banksName:
        builder.button(
            text=f'{bank["name"]}',
            callback_data=UserExchangeData(
                id=0,
                name=bank["name"],
                action="choose_new_user_bank",
                is_returned=False,
            ),
        )
    builder.button(
        text="↩ Вернуться на главную", callback_data=UserHomeData(action="cancel", id=0)
    )
    builder.adjust(2, 2, 2, 2, 2, 2, 1, 1)

    return builder.as_markup()


async def accept_changer_transfer(transfer_id):
    """ """
    builder = InlineKeyboardBuilder()
    actions = {
        "accept": "🤝 Подтвердить получение",
        "decline": "👎 Перевод не получен",
        "admin": "⚠️ Связаться с админом",
    }

    for action in actions.keys():
        builder.button(
            text=actions[action],
            callback_data=UserExchangeData(
                id=transfer_id, name="", action=action, is_returned=False
            ),
        )
    builder.adjust(1)

    return builder.as_markup()


async def get_trouble_staff_contact():
    contact = appSettings.botSetting.troubleStaffId
    builder = InlineKeyboardBuilder()

    builder.button(
        text="👮🏻 Связаться с админом",
        url=f"tg://user?id={contact}",
        callback_data=URLData(),
    )

    return builder.as_markup()


async def final_step_timeout_kb():
    builder = InlineKeyboardBuilder()
    contact = appSettings.botSetting.troubleStaffId

    builder.button(
        text="👮🏻 Я перевел деньги",
        callback_data=UserExchangeData(
            id=0, name="", action="send_money_on_expired_offer", is_returned=False
        ),
    )
    builder.button(
        text="Давай сначала", callback_data=UserHomeData(action="cancel", id=0)
    )
    builder.adjust(1)
    return builder.as_markup()


async def timeout_kb():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Начать сначала", callback_data=UserHomeData(action="cancel", id=0)
    )
    return builder.as_markup()


async def user_show_event_kb(event: dict):
    event_id = event.get("id")
    builder = InlineKeyboardBuilder()

    actions = {
        "user_transfer_accepted": "🤝 Подтвердить перевод",
        "user_transfer_claims": "⚠️ Перевод не получен",
    }

    for key, value in actions.items():
        builder.button(text=value, callback_data=UserHomeData(action=key, id=event_id))
    builder.adjust(1)

    return builder.as_markup()


async def final_transfer_stage():
    contact = appSettings.botSetting.troubleStaffId
    builder = InlineKeyboardBuilder()

    builder.button(
        text="👮🏻 Связаться с админом",
        url=f"tg://user?id={contact}",
        callback_data=URLData(),
    )
    builder.button(
        text="↩ Вернуться на главную", callback_data=UserHomeData(action="cancel", id=0)
    )
    builder.adjust(1)

    return builder.as_markup()


async def user_cancel_button():
    contact = appSettings.botSetting.troubleStaffId
    builder = InlineKeyboardBuilder()
    builder.button(
        text="↩ Вернуться на главную", callback_data=UserHomeData(action="cancel", id=0)
    )
    builder.adjust(1)

    return builder.as_markup()
