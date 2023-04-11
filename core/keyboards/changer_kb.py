from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from core.api_actions.bot_api import SimpleAPI
from core.middlwares.routes import r    # Dataclass whith all api routes
from core.keyboards.callbackdata import (
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