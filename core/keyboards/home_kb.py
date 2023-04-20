from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from core.keyboards.callbackdata import HomeData


async def user_home_button():
    '''Build RelyKeyboardButton for "/start" function.
    '''
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='Режим работы'))
    builder.add(KeyboardButton(text='Справка'))
    builder.add(KeyboardButton(text='Обменять валюту'))
    builder.adjust(2, 1)

    return builder.as_markup(
        resize_keyboard=True,
        input_field_placeholder='Выбери нужное тебе действие'
    ) 


async def user_home_inline_button():
    '''Build InlineKeyboardButton for "/start" function.
    '''
    builder = InlineKeyboardBuilder()

    data = {
        'info': 'Справка',
        'time': 'Режим работы',
        'change': 'Обменять валюту',
    }

    for i in data.keys():
        builder.button(
            text=data[i],
            callback_data=HomeData(
                action=i
            )
        )
    builder.adjust(2)

    return builder.as_markup()

async def user_back_home_inline_button():
    '''
    '''
    builder = InlineKeyboardBuilder()

    builder.button(
        text='↩ Вернуться на главную',
        callback_data=HomeData(
            action='cancel'
        )
    )

    return builder.as_markup()