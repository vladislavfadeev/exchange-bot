from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData



b1 = KeyboardButton('Заявка на обмен')
b2 = KeyboardButton('Режим работы')
b3 = KeyboardButton('Справка')

customer_start_key = ReplyKeyboardMarkup(resize_keyboard=True).add(b1).add(b2).insert(b3)