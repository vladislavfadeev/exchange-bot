from typing import Callable
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.types.callback_query import CallbackQuery
from aiogram.types import Message
from aiogram import F
from create_bot import bot, dp
from core.middlwares.routes import r    # Dataclass whith all api routes
from core.utils import msg_maker, msg_var
from core.api_actions.bot_api import SimpleAPI
from core.utils.bot_fsm import FSMSteps
from core.utils import msg_var as msg
from core.keyboards import user_kb
from core.keyboards.callbackdata import (
    AmountData,
    CurrencyData,
    OfferData,
    SetBuyBankData,
    SetSellBankData,
)
from core.middlwares.exceptions import (
    MinAmountError,
    MaxAmountError,
)



async def start_change(message: Message, state: FSMContext):
    '''Handler is start user change currency process.
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


async def show_offer(
        call: CallbackQuery, 
        state: FSMContext,
        callback_data: CurrencyData
    ):
    '''Show all available offers for the selected currency
    '''
    if callback_data.isReturned:
        await state.set_state(FSMSteps.INIT_CHANGE_STATE)

    value = callback_data.name
    filter_data = f'?currency={value}&isActive=True'
    
    offers = await SimpleAPI.get(
        r.userRoutes.offer,
        filter_data
    )
    await state.update_data(offerList = offers.json())
    messages = await msg_maker.offer_list_msg_maker(offers.json())

    for i in range(len(messages)):

        value = offers.json()[i]
        builder = InlineKeyboardBuilder()
        builder.button(
            text=f'🔥 Обменять {value["currency"]} тут 🔥',
            callback_data=OfferData(
                id=value['id'],
                isReturned=False
            )
        )

        await bot.send_message(
            call.from_user.id,
            text=messages[i],
            reply_markup=builder.as_markup()
        )


async def set_amount(
        call: CallbackQuery,
        state:FSMContext,
        callback_data: OfferData
    ):
    '''
    '''
    if callback_data.isReturned:

        data = await state.get_data()
        offerData = data['selectedOffer']
        
        await bot.send_message(
            call.from_user.id,
            text = await msg_maker.set_amount_returned_msg_maker(offerData)
        )

    else:

        offerData = await state.get_data()

        for i in offerData['offerList']:
            if i['id'] == callback_data.id:
            
                await state.update_data(selectedOffer = i)
                await state.update_data(offerList = {})
                offerData = i

        await bot.send_message(
            call.from_user.id,
            text = await msg_maker.set_amount_msg_maker(offerData)
        )

        await state.set_state(FSMSteps.SET_AMOUNT_STATE)
    

async def set_amount_check(message: Message, state: FSMContext):
    '''
    '''
    data = await state.get_data()
    offerData = data['selectedOffer']
    
    try:

        amount = float(message.text.replace(',', '.'))

        if offerData['minAmount'] != None:
            if amount < offerData['minAmount']:
                raise MinAmountError()
            
        if offerData['maxAmount'] != None:
            if amount > offerData['maxAmount']:
                raise MaxAmountError()
            
    except ValueError:
        await message.answer(text=msg_var.type_error_msg)

    except MinAmountError:
        await message.answer(
            text = await msg_maker.min_amount_error_msg_maker(offerData),
            reply_markup = await user_kb.user_return_to_offer_choice_button(offerData)
        )

    except MaxAmountError:
        await message.answer(
            text = await msg_maker.max_amount_error_msg_maker(offerData),
            reply_markup = await user_kb.user_return_to_offer_choice_button(offerData)
        )

    else:
        await state.update_data(sellAmount = amount)
        await message.answer(
            text= await msg_maker.show_user_buy_amount(
                amount,
                offerData['rate'],
                offerData['currency']
            ),
            reply_markup= await user_kb.set_amount_check_inlkb()
        )


async def choose_sell_bank(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: AmountData   
    ):
    '''
    '''
    await state.set_state(FSMSteps.SET_SELL_BANK)
    data = await state.get_data()
    offerData = data['selectedOffer']

    filter_data = f'?owner={offerData["owner"]}&isActive=True&search={offerData["currency"]}'
    banks = await SimpleAPI.get(
        r.userRoutes.changerBanks,
        filter_data
    )

    await bot.send_message(
        call.from_user.id,
        text= await msg_maker.set_sell_bank(offerData['currency']),
        reply_markup= await user_kb.set_sell_bank(banks)
    )
    

async def choose_buy_bank(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: SetSellBankData
    ):
    '''
    '''
    await state.update_data(sellBank = callback_data.id)
    await state.set_state(FSMSteps.SET_BUY_BANK_INIT)

    filter_data = f'?owner={call.from_user.id}&isActive=True&search=MNT'
    banks = await SimpleAPI.get(r.userRoutes.userBanks, filter_data)

    if len(banks.json()) and not callback_data.setNew:

        await bot.send_message(
            call.from_user.id,
            text = await msg_maker.choose_user_bank_from_db(),
            reply_markup= await user_kb.choose_user_bank_from_db(banks)
        )

    else:

        banksName = await SimpleAPI.get(r.userRoutes.banksNameList)

        await bot.send_message(
            call.from_user.id,
            text='Выберите банк из списка:',
            reply_markup= await user_kb.choose_bank_name_from_list(banksName)
        )


async def choose_buy_bank_next(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: SetBuyBankData
    ):
    '''
    '''
    await state.update_data(buyBank = callback_data)




async def register_message_handlers_user():
    '''Registry message handlers there.
    '''
    dp.message.register(
        start_change,
        F.text == 'Обменять валюту',
        FSMSteps.INIT_STATE
    )
    dp.message.register(
        set_amount_check,
        F.text,
        FSMSteps.SET_AMOUNT_STATE
    )
    dp.message.register(
        choose_sell_bank,
        F.text,
        FSMSteps.SET_SELL_BANK
    )



async def register_callback_handler_user():
    '''Register callback_querry handlers there.
    '''
    dp.callback_query.register(
        show_offer,
        CurrencyData.filter()
    )
    dp.callback_query.register(
        set_amount,
        OfferData.filter()
    )
    dp.callback_query.register(
        choose_sell_bank,
        AmountData.filter()
    )
    dp.callback_query.register(
        choose_buy_bank,
        SetSellBankData.filter()
    )
    dp.callback_query.register(
        choose_buy_bank_next,
        SetBuyBankData.filter()
    )
















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