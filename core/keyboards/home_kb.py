from aiogram.types import KeyboardButton
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder


def user_home_button():
    '''
    Build RelyKeyboardButton for "/start" function.
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


def user_home_inline_button():
    '''
    Build InlineKeyboardButton for "/start" function.
    
    '''
    ...
