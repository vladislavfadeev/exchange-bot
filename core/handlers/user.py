from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message
from aiogram import F
from create_bot import bot, dp
from core.middlwares.routes import r
from core.api_actions.bot_api import SimpleAPI
from core.utils.bot_fsm import FSMSteps
from core.utils import msg_var as msg
from core.keyboards import user_kb


async def start_change(message: Message, state: FSMContext):
    '''
    Handler is start user change currency process.
    React on "Обменять валюту" in "FSMSteps.INIT_STATE"
    '''    
    await message.answer(
        text=msg.set_sell_currency,
        reply_markup= user_kb.user_cancel_button()
    )
    await bot.send_message(
        message.from_user.id,
        text=msg.currency_choice_1, 
        reply_markup= await user_kb.set_sell_currency_button()
    )
    await state.set_state(FSMSteps.INIT_CHANGE_STATE)






async def register_handlers_user():
    '''
    Registry handlers there.
    '''
    dp.message.register(
        start_change,
        F.text == 'Обменять валюту',
        FSMSteps.INIT_STATE
    )
    # dp.message.register(
    #     command_help,
    #     Command(commands=['help']),
    #     FSMSteps.INIT_STATE
    # )
    # dp.message.register(
    #     work_time,
    #     Command(commands=['work_time']),
    #     FSMSteps.INIT_STATE
    # )





















# from aiogram import types, Dispatcher
# from aiogram.dispatcher.filters.state import State, StatesGroup
# from aiogram.dispatcher import FSMContext
# from aiogram.dispatcher.filters import Text
# from create_bot import dp, bot
# from keyboard import customer_kb, main_kb
# import variables.service_message as sm
# import variables.msg_maker as msg_maker
# from api_actions import user_api
# from handlers import changers
# from datetime import datetime



# class FSMRequest(StatesGroup):
#     set_currency = State()
#     set_amount = State()
#     set_rate = State()
#     open_request = State()
#     wait_response = State()
#     response = State()
#     set_choice = State()
#     get_proof = State()
#     transaction = State()



# ### Выбор валютной пары.
# async def set_currency_pair(message : types.Message, state: FSMContext):
#     await FSMRequest.set_currency.set()
#     await bot.send_message(message.from_user.id, text=sm.start_currency_choice, 
#                             reply_markup = customer_kb.exchange_cancel_kb)
#     await bot.send_message(message.from_user.id, text=sm.currency_choice, 
#                             reply_markup = await customer_kb.curr_pair_kb())
#     await FSMRequest.next()
    

# @dp.callback_query_handler(customer_kb.curr_pair_kb_cbd.filter(
#                                         action=['set_pair']), 
#                                         state= FSMRequest.set_amount)
# async def set_amount_func(message: types.Message, callback_data: dict,
#                           state: FSMContext):
#     async with state.proxy() as data:
#         data['currency_pair_id'] = callback_data.get('pair')
#     await bot.send_message(message.from_user.id, text=sm.enter_amount)
#     await FSMRequest.next()


# async def set_user_rate(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['amount'] = message.text
#     await bot.send_message(message.from_user.id, text=sm.enter_rate)
#     await FSMRequest.next()


# async def open_request_func(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['customer_id'] = message.from_user.id
#         data['sell_rate'] = message.text
#         data['customer_bank'] = 'Sber'
#     request = await user_api.insert_request_todb(data._data)
#     await changers.send_user_request(request)
#     await bot.send_message(message.from_user.id, text=sm.request_is_open)
#     await state.finish()


# async def send_chngr_response(data_sr, account):
#     await bot.send_message(
#                     data_sr['post']['customer_id'], 
#                     text= await msg_maker.response_msg_maker(data_sr),
#                     reply_markup= await customer_kb.cust_choise_kb(data_sr, account))
    

# @dp.callback_query_handler(customer_kb.cust_choise_kb_cbd.filter(
#                                         action=['set_choice']))
# async def user_choise(message: types.Message, callback_data: dict,
#                       state: FSMContext):
#     await FSMRequest.set_choice.set()
#     async with state.proxy() as data:
#         data['response_id'] = callback_data.get('resp_id'),
#         data['changer_account'] = callback_data.get('account')
#     await bot.send_message(message.from_user.id, text=sm.enter_bank_account)


# async def enter_user_account(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['cust_bank_account'] = message.text
#     data_sr = await user_api.APISimpleMethods.api_post('/api/v1/customer-choice', data._data)
#     msg = await msg_maker.choice_msg_maker(data_sr)
#     await bot.send_message(message.from_user.id, text=msg)
#     async with state.proxy() as data:
#         data['choice_id'] = data_sr['post']['id']
#     await FSMRequest.next()


# async def load_proof(message: types.Message, state : FSMContext):
#     async with state.proxy() as data:
#         post_data = {
#             "post_choice_id": data['choice_id'],
#             "user_proof": message.photo[0].file_id
#         }
#     print(post_data)
#     data_sr = await user_api.APISimpleMethods.api_post('/api/v1/transaction', post_data)
#     await changers.send_user_transaction(data_sr)
#     await bot.send_message(message.from_user.id, text='Данные отправлены обменнику, ожидайте перевод')
#     await state.finish()


# async def send_changer_transaction(data_sr):
#     await FSMRequest.transaction.set()
#     inline_kb = await customer_kb.user_accept_kb(data_sr['id'])
#     await bot.send_photo(data_sr['choice_id']['customer_id'], 
#                          data_sr['changer_proof'], 
#                          'Обменник выполнил перевод',
#                          reply_markup=inline_kb)


# @dp.callback_query_handler(customer_kb.accept_user_trn_kb_cbd.filter(
#                                         action=['accept_usr']))
# async def accept_transaction(message: types.Message, callback_data: dict,
#                              state: FSMContext):
#     async with state.proxy() as data:
#         id = callback_data.get('tr_id')
#         data['customer_accept'] = True
#         data['customer_accept_date'] = datetime.now()
#     await user_api.APISimpleMethods.api_patch(f'/api/v1/transaction/{id}', data=data._data)
#     await bot.send_message(message.from_user.id, sm.end_message, 
#                            reply_markup=main_kb.customer_start_key)
#     await state.finish()
    

    
    








#     # for changer in changers:
#     #     await bot.send_message(changer, f'Здарова, заебал - {amount}, {chtoto}')

# ''' Блок ответа на иформационные кнопки вне состояния '''
# ### Вывод информации о истории заказов.
# ### Функтия не имеет соответсвующей кнопки в блоке кнопок! Для вывода потребуется команда "История заказов", либо установка кнопки на панель.
# # async def start_request(message: types.Message):
# #     value = await sqlite_db.sql_show_order_history(message.from_user.id)
# #     op = ''
# #     summ = 0
# #     for i in value:
# #         for r in i:
# #             char = f'Заказ № {i[2]} | Дата: {i[3]} | Сумма {i[5]} руб.\nАдрес самовывоза: {i[4]}\n\n'
# #         op += char
# #         summ += float(i[5])
# #     await bot.send_message(message.from_user.id, text=f'История ваших заказов:\n\n{op}\n\nОбщая сумма ваших заказов: {summ} руб.')


# ### Регистрируем хендлеры.
# def register_handlers_exchange(dp : Dispatcher):
#     dp.register_message_handler(set_currency_pair, Text(equals= 'Заявка на обмен', ignore_case=True), state=None)
#     dp.register_message_handler(set_user_rate,state=FSMRequest.set_rate)
#     dp.register_message_handler(open_request_func,state=FSMRequest.open_request)
#     dp.register_message_handler(enter_user_account,state=FSMRequest.set_choice)
#     dp.register_message_handler(load_proof, content_types=['photo'], state=FSMRequest.get_proof)