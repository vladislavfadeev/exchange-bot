from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from core.keyboards.callbackdata import UserHomeData



async def get_claim_contacts_toadmin(user_id, changer_id):

    builder = InlineKeyboardBuilder()

    builder.button(
        text='Чат с пользователем',
        url=f'tg://user?id={user_id}',
        callback_data=UserHomeData(
            action='',
            id=0
        )
    )
    builder.button(
        text='Чат с обменником',
        url=f'tg://user?id={changer_id}',
        callback_data=UserHomeData(
            action='',
            id=0
        )
    )
    builder.adjust(1)
    return builder.as_markup()