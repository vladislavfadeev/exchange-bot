from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from api_actions import kb_api


cancel_button = KeyboardButton('Отменить заявку')
exchange_cancel_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(cancel_button)


curr_pair_kb_cbd = CallbackData("curr_pair", "pair", "action")
async def curr_pair_kb():
    data = await kb_api.get_curr_pair()
    inline_kb = InlineKeyboardMarkup(row_width = 1)
    inline_kb.add(*[InlineKeyboardButton(button['name'], 
                     callback_data=
                     curr_pair_kb_cbd.new(pair = button['id'],
                     action = "set_pair")) for button in data])
    
    return inline_kb
    

cust_choise_kb_cbd = CallbackData("choice", "resp_id", "account", "action")
async def cust_choise_kb(data_sr, account):
    data = data_sr['post']
    inline_kb = InlineKeyboardMarkup(row_width = 2)
    inline_kb.add(InlineKeyboardButton('Принять', 
                     callback_data=
                     cust_choise_kb_cbd.new(resp_id = data['id'],
                                            account = account,
                                            action = "set_choice")))
    
    return inline_kb


accept_user_trn_kb_cbd = CallbackData("accept_user", "tr_id", "action")
async def user_accept_kb(id):
    inline_kb = InlineKeyboardMarkup(row_width = 1)
    inline_kb.add(InlineKeyboardButton('Подтвердить получение', 
                    callback_data=accept_user_trn_kb_cbd.new(
                    tr_id = id,
                    action = "accept_usr")))
    return inline_kb







# exchchange_currency_pair_cd = CallbackData("curr_pair", "pair", "action")
# inline_kb_set_category_order = InlineKeyboardMarkup().add(
#         InlineKeyboardButton(f'MNT | RUB', callback_data=exchchange_currency_pair_cd.new(pair = "1", action = "set_pair")))#.insert(
#         # InlineKeyboardButton(f