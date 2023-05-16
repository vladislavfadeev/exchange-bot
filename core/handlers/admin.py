from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.callback_data import CallbackData
from aiogram.dispatcher.filters import Text
from aiogram import types, Dispatcher
from create_storage import dp, bot
# from data_base import sqlite_db
# from keyboard import admin_kb, client_kb
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton





ID = None
char_cb = CallbackData('del_item', 'product_id', 'action')
edit_item_admin_cb = CallbackData('edit_item', 'product_id', 'column', 'action')




class FSMAdmin(StatesGroup):
    category_set = State()
    photo = State()
    name = State()
    description = State()
    price = State()
    edit_item = State()
    edit_photo = State()
    edit_name = State()
    edit_description = State()
    edit_price = State()
    edit_choice = State()
    del_state = State()

    
''' Вход в режим администратора '''
### Получаем ID текущего модератора
# @dp.message_handler(commands=['login'], is_chat_admin=True)
async def make_changes_command(message: types.Message):
    admin_id = str(message.from_user.id)
    # if admin_id in admins:
    #     await bot.send_message(message.from_user.id, 'Здравствуй хозяин!') # reply_markup= admin_kb.button_case_admin)
    #     await message.delete()




def register_handlers_admin(dp : Dispatcher):
    dp.register_message_handler(make_changes_command, commands=['login'])