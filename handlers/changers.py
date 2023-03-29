from aiogram import types, Dispatcher
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from create_bot import dp, bot
import variables.service_message as sm
import variables.msg_maker as mm
from api_actions import user_api
from keyboard import changer_kb, customer_kb
from handlers import exchange
from datetime import datetime


class FSMResponse(StatesGroup):
    set_rate = State()
    set_bank_account = State()
    get_proof = State()

    

async def send_user_request(request):
    message, request_id = await mm.request_msg_maker(request)
    inline_kb = await changer_kb.resp_answer_kb(request_id)
    changers = await user_api.get_changers_list()
    print(message)
    for changer in changers:
        await bot.send_message(changer['tg_id'], text = message,
                               reply_markup = inline_kb)
        

@dp.callback_query_handler(changer_kb.resp_answer_kb_cbd.filter(
                                        action=['rp_decline']))
async def decline_request_func(message: types.Message, callback_data: dict,
                                state: FSMContext):
    await bot.send_message(message.from_user.id, text=sm.decline_message)


@dp.callback_query_handler(changer_kb.resp_answer_kb_cbd.filter(
                                        action=['rp_answer'])) 
                                        # state= FSMRequest.set_amount)
async def answer_request_func(message: types.Message, callback_data: dict,
                                state: FSMContext):
    await FSMResponse.set_rate.set()
    async with state.proxy() as data:
        data['request_id'] = callback_data.get('req_id')
    await bot.send_message(message.from_user.id, text=sm.chr_enter_rate)
    await FSMResponse.next()


async def choose_bank_account(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['buy_rate'] = message.text
        data['changer_id'] = message.from_user.id
    inline_kb = await changer_kb.choose_bank_kb(message.from_user.id)
    await bot.send_message(message.from_user.id, text=sm.chr_choose_bank,
                           reply_markup=inline_kb)
    # await FSMResponse.next()


@dp.callback_query_handler(changer_kb.choose_bank_kb_cbd.filter(
                                        action=['set_bank']),
                                        state=FSMResponse.set_bank_account)
async def set_bank_account(message: types.Message, callback_data: dict,
                           state: FSMContext):
    async with state.proxy() as data:
        data['changer_bank'] = callback_data.get('bank_name')
    data_sr = await user_api.insert_response_todb(data._data)
    await exchange.send_chngr_response(data_sr, callback_data.get('account'))
    await bot.send_message(message.from_user.id, text=sm.chr_send_response)
    await state.finish()


async def send_user_transaction(data_sr):
    data = data_sr['post']
    inline_kb = await changer_kb.accept_user_trn_kb(
                         data['choice_id']['customer_bank_account'], 
                         data['choice_id']['customer_bank'],
                         data['id'])
    await bot.send_photo(data['choice_id']['changer_id'], 
                         data['customer_proof'], 
                         'Пользователь выполнил перевод',
                         reply_markup=inline_kb)


@dp.callback_query_handler(changer_kb.accept_changer_trn_kb_cbd.filter(
                                        action=['accept_chgr']))
async def accept_user_transaction(message:types.Message, callback_data: dict,
                                  state:FSMContext):
    await FSMResponse.get_proof.set()
    async with state.proxy() as data:
        data['transaction_id'] = callback_data.get('id')
        data['changer_accept'] = True
        data['changer_accept_date'] = datetime.now()
    bank = callback_data.get('bank')
    account = callback_data.get('user_account')
    msg = await mm.changer_transaction_msg_maker(bank, account)
    await bot.send_message(message.from_user.id, text=msg)


async def load_proof(message: types.Message, state : FSMContext):
    async with state.proxy() as data:
        data['changer_proof'] = message.photo[0].file_id
        id = data['transaction_id']
    data_sr = await user_api.APISimpleMethods.api_patch(f'/api/v1/transaction/{id}', data._data)
    await bot.send_message(message.from_user.id, text='Данные отправлены пользователю, спасибо!')
    await state.finish()
    await exchange.send_changer_transaction(data_sr)
    





def register_handlers_exchange(dp : Dispatcher):
    dp.register_message_handler(choose_bank_account, state=FSMResponse.set_bank_account)
    dp.register_message_handler(load_proof, content_types=['photo'], state=FSMResponse.get_proof)
    # dp.register_message_handler(set_user_rate,state=FSMRequest.set_rate)
    # dp.register_message_handler(open_request_func,state=FSMRequest.open_request)