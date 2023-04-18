from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from core.api_actions.bot_api import SimpleAPI
from core.middlwares.routes import r    # Dataclass whith all api routes
from core.keyboards.callbackdata import (
    StuffEditData,
    StuffOfficeData,
    HomeData,
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
                action='home'
            )
        )


    builder.adjust(2, 1)

    return builder.as_markup()