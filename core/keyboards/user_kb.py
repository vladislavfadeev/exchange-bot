from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types.inline_keyboard_markup import InlineKeyboardMarkup
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from core.api_actions.bot_api import SimpleAPI
from core.middlwares.routes import r    # Dataclass whith all api routes
from core.keyboards.callbackdata import (
    CurrencyData,
    OfferData,
)


async def set_sell_currency_button():
    '''Build InlineKeyboardButton with currensy for "start_change" handler.
    '''
    currency = await SimpleAPI.get(r.keysRoutes.currencyList)
    builder = InlineKeyboardBuilder()

    for curr in currency.json():
        builder.button(
            text=curr["name"],
            callback_data=CurrencyData(
                id=curr['id'],
                name=curr['name'],
                isReturned=False
            )
        )
    builder.adjust(3)

    return builder.as_markup()


def user_cancel_button():
    '''Build RelyKeyboardButton for cancel all process and retun to INIT_STATE.
    '''
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text='Отменить'))

    return builder.as_markup(
        resize_keyboard=True,
    ) 


async def user_return_to_offer_choice_button(offerData):
    '''Build InlineKeyboardButton with offer id for user choice
    '''

    builder = InlineKeyboardBuilder()
    builder.button(
        text=f'↩ Вернуться к выбору предложений',
        callback_data=CurrencyData(
            id=1,
            name=offerData['currency'],
            isReturned=True
        )
    )
    
    return builder.as_markup()



# from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# from aiogram.utils.callback_data import CallbackData
# from api_actions import kb_api


# cancel_button = KeyboardButton('Отменить заявку')
# exchange_cancel_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(cancel_button)


# curr_pair_kb_cbd = CallbackData("curr_pair", "pair", "action")
# async def curr_pair_kb():
#     data = await kb_api.get_curr_pair()
#     inline_kb = InlineKeyboardMarkup(row_width = 1)
#     inline_kb.add(*[InlineKeyboardButton(button['name'], 
#                      callback_data=
#                      curr_pair_kb_cbd.new(pair = button['id'],
#                      action = "set_pair")) for button in data])
    
#     return inline_kb
    

# cust_choise_kb_cbd = CallbackData("choice", "resp_id", "account", "action")
# async def cust_choise_kb(data_sr, account):
#     data = data_sr['post']
#     inline_kb = InlineKeyboardMarkup(row_width = 2)
#     inline_kb.add(InlineKeyboardButton('Принять', 
#                      callback_data=
#                      cust_choise_kb_cbd.new(resp_id = data['id'],
#                                             account = account,
#                                             action = "set_choice")))
    
#     return inline_kb


# accept_user_trn_kb_cbd = CallbackData("accept_user", "tr_id", "action")
# async def user_accept_kb(id):
#     inline_kb = InlineKeyboardMarkup(row_width = 1)
#     inline_kb.add(InlineKeyboardButton('Подтвердить получение', 
#                     callback_data=accept_user_trn_kb_cbd.new(
#                     tr_id = id,
#                     action = "accept_usr")))
#     return inline_kb







# exchchange_currency_pair_cd = CallbackData("curr_pair", "pair", "action")
# inline_kb_set_category_order = InlineKeyboardMarkup().add(
#         InlineKeyboardButton(f'MNT | RUB', callback_data=exchchange_currency_pair_cd.new(pair = "1", action = "set_pair")))#.insert(
#         # InlineKeyboardButton(f