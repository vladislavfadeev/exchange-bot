from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from api_actions import kb_api


cancel_button = KeyboardButton('Отменить заявку')
exchange_cancel_kb = ReplyKeyboardMarkup(
                        resize_keyboard=True).add(cancel_button)


resp_answer_kb_cbd = CallbackData("resp_answer", 
                                  "req_id", 
                                  "action")
async def resp_answer_kb(request_id):
    inline_kb = InlineKeyboardMarkup(row_width = 2)
    inline_kb.add(InlineKeyboardButton('Ответить', callback_data= 
                        resp_answer_kb_cbd.new(
                        req_id = request_id,
                        action = "rp_answer"))
                ).add(InlineKeyboardButton('Отклонить', callback_data= 
                        resp_answer_kb_cbd.new(
                        req_id = request_id,
                        action = "rp_decline"))
                )
    return inline_kb


choose_bank_kb_cbd = CallbackData('resp_answer', 'bank_name' ,
                                  "account" , "action")
async def choose_bank_kb(changer_id):
    data = await kb_api.get_bank_account(changer_id)
    inline_kb = InlineKeyboardMarkup(row_width = 1)
    inline_kb.add(*[InlineKeyboardButton(button['name'], 
                     callback_data=choose_bank_kb_cbd.new(
                        bank_name = button['name'],
                        account = button['bank_account'],
                        action = "set_bank")) for button in data['accounts']]
                )
    return inline_kb


accept_changer_trn_kb_cbd = CallbackData('accept_changer', "user_account",
                                        "bank" , "id", "action")
async def accept_user_trn_kb(account, bank, id):
    inline_kb = InlineKeyboardMarkup(row_width = 1)
    inline_kb.add(InlineKeyboardButton('Подтвердить получение', 
                        callback_data=accept_changer_trn_kb_cbd.new(
                        user_account = account,
                        bank = bank,
                        id = id,
                        action = "accept_chgr"))
                )
    return inline_kb