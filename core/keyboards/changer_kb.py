from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from core.middlwares.settigns import appSettings
from core.api_actions.bot_api import SimpleAPI
from core.middlwares.routes import r    # Dataclass whith all api routes
from core.keyboards.callbackdata import (
    StuffEditData,
    StuffOfficeData,
    HomeData,
    TestData,
    UserProofActions,
)


async def accept_user_transfer(transfer_id):
    '''
    '''
    builder = InlineKeyboardBuilder()
    actions = {
        'accept': '🤝 Подтвердить получение',
        'decline': '👎 Перевод не получил',
        'admin': '⚠️ Связаться с админом'
    
    }

    for action in actions.keys():
        builder.button(
            text=actions[action],
            callback_data=UserProofActions(
                action= action,
                transferId=transfer_id
            )
        )
    builder.adjust(1)

    return builder.as_markup()



async def staff_welcome_button(transfers):

    value = len(transfers) if transfers else None
    button_text = f'💰 Входящие переводы ({value})' if value else '💰 Входящие переводы'

    builder = InlineKeyboardBuilder()
    actions = {
        'offers': '📊 Мои предложения',
        'accounts': '💳 Мои счета',
        'transfers': button_text
    }
    for action in actions.keys():
        builder.button(
            text=actions[action],
            callback_data=StuffOfficeData(
                action=action
            )
        )
    builder.adjust(2)

    return builder.as_markup()


async def stuff_offer_menu_buttons():

    builder = InlineKeyboardBuilder()
    actions = {
        'create_new': '📝 Создать новое',
        'edit_offers': '⚙️ Редактировать',
        'inactive': '🗄 Архив предложений'
    }
    for action in actions.keys():
        builder.button(
            text=actions[action],
            callback_data=StuffOfficeData(
                action=action
            )
        )
    builder.adjust(2)

    return builder.as_markup()



async def stuff_edit_offer_list_buttons(offer_id, isLatest):

    builder = InlineKeyboardBuilder()
    actions = {
        'edit': '⚙️ Редактировать',
        'delete': '🗑️ Удалить',
        'archive': '🗄 Убрать с публикации'
        
    }

    for action in actions.keys():

        builder.button(
            text= actions[action],
            callback_data=StuffEditData(
                id= offer_id,
                action= action,
                value= ''
            )
        )
    if isLatest:

        builder.button(
            text='↩ Вернуться на главную',
            callback_data=HomeData(
                action='cancel'
            )
        )


    builder.adjust(2, 1)

    return builder.as_markup()



async def stuff_edit_inactive_offers_buttons(offer_id, isLatest):

    builder = InlineKeyboardBuilder()
    actions = {
        'edit': '⚙️ Редактировать',
        'delete': '🗑️ Удалить из архива',
        'setActive': '📢 Опубликовать'
        
    }

    for action in actions.keys():

        builder.button(
            text= actions[action],
            callback_data=StuffEditData(
                id= offer_id,
                action= action,
                value= ''
            )
        )
    if isLatest:

        builder.button(
            text='↩ Вернуться на главную',
            callback_data=HomeData(
                action='cancel'
            )
        )


    builder.adjust(2, 1)

    return builder.as_markup()


async def sfuff_cancel_button():
    '''.
    '''
    builder = InlineKeyboardBuilder()
    builder.button(
        text='↩ Вернуться на главную',
        callback_data=HomeData(
            action='cancel'
        )
    )
    builder.adjust(1)

    return builder.as_markup() 


async def set_sell_currency_button():
    '''
    '''
    currency = await SimpleAPI.get(r.keysRoutes.currencyList)
    builder = InlineKeyboardBuilder()

    for curr in currency.json():
        builder.button(
            text=curr["name"],
            callback_data=StuffEditData(
                id=curr['id'],
                value=curr['name'],
                action='new_offer_currency'
            )
        )
    builder.button(
        text='↩ Отменить',
        callback_data= HomeData(
            action='cancel'
        )
    )
    builder.adjust(3)

    return builder.as_markup()


async def staff_accept_new_rate():
    '''
    '''
    builder = InlineKeyboardBuilder()
    builder.button(
        text='⤵️ Согласен, продолжить',
        callback_data=StuffEditData(
            id=0,
            action='create_new_offer_banks',
            value=''
        )
    )
    builder.button(
        text='⤴️ Вернуться, ввести другую сумму',
        callback_data=StuffEditData(
            id=0,
            action='new_offer_currency_returned',
            value=''
        )
    )

    return builder.as_markup()


async def stuff_create_new_offer_banks(banks):

    builder = InlineKeyboardBuilder()

    for bank in banks:
        builder.button(
            text = f"💳 {bank.get('name')} {bank.get('bankAccount')}",
            callback_data=StuffEditData(
                id=bank.get('id'),
                action='staff_set_banks',
                value=''
            )
        )
    builder.button(
        text='👌 Продолжить',
        callback_data=HomeData(
            action='cancel'
        )
    )
    builder.button(
        text='↩ Вернуться на главную',
        callback_data=HomeData(
            action='cancel'
        )
    )
    builder.adjust(1)

    return builder.as_markup()


async def staff_zero_banks_buttons():

    contact = appSettings.botSetting.troubleStaffId
    builder = InlineKeyboardBuilder()

    builder.button(
        text='👮🏻 Связаться с админом',
        url= f'tg://user?id={contact}',
        callback_data=TestData(
            url= ''
        )
    )
    builder.button(
        text='↩ Вернуться на главную',
        callback_data= HomeData(
            action='cancel'
        )
    )
    builder.adjust(1)

    return builder.as_markup()
    

