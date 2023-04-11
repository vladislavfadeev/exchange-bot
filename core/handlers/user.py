from datetime import date
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
from core.keyboards import changer_kb
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

    params = {
        'currency': callback_data.name,
        'isActive': True
    }
    
    offers = await SimpleAPI.get(
        r.userRoutes.offer,
        params
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

    params = {
        'owner': offerData["owner"],
        'isActive': True,
        'search': offerData["currency"]
    }

    banks = await SimpleAPI.get(
        r.userRoutes.changerBanks,
        params
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
    await state.set_state(FSMSteps.SET_BUY_BANK_INIT)

    params = {
        'owner': call.from_user.id,
        'isActive': True
    }
    banks = await SimpleAPI.get(r.userRoutes.userBanks, params)

    if len(banks.json()) and not callback_data.setNew:

        await state.update_data(sellBank = callback_data.id)        
        await bot.send_message(
            call.from_user.id,
            text = await msg_maker.choose_user_bank_from_db(),
            reply_markup= await user_kb.choose_user_bank_from_db(banks)
        )

    else:
        if not callback_data.setNew:
            await state.update_data(sellBank = callback_data.id)

        banksName = await SimpleAPI.get(r.userRoutes.banksNameList)

        await bot.send_message(
            call.from_user.id,
            text='Выберите банк из списка:',
            reply_markup= await user_kb.choose_bank_name_from_list(banksName)
        )


async def choose_new_buy_bank_next(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: SetBuyBankData
    ):
    '''
    '''
    await state.update_data(buyBank = callback_data.bankName)
    await state.set_state(FSMSteps.SET_BUY_BANK_ACCOUNT)
    await bot.send_message(
        call.from_user.id,
        text= await msg_maker.set_buy_bank_account(
            callback_data.bankName
        )
    )


async def apply_new_buy_bank(message: Message, state: FSMContext):
    '''
    '''
    account = message.text
    allData = await state.get_data()
    bankName = allData['buyBank']
    changerId = allData['selectedOffer']['owner']
    
    postData = {
        "name": bankName,
        "bankAccount": account,
        "owner": message.from_user.id,
        "currency": "3",
        "isActive": True        
    }

    account = await SimpleAPI.post(r.userRoutes.userBanks, postData)
    await bot.send_message(
        changerId,
        text= await msg_maker.changer_inform(changerId, allData)
    )
    await message.answer( 
        text= await msg_maker.complete_set_new_bank(allData)
    )
    await state.update_data(userAccount = account.json())
    await state.set_state(FSMSteps.GET_USER_PROOF)


async def use_old_buy_bank(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: SetBuyBankData):
    '''
    '''
    allData = await state.get_data()
    changerId = allData['selectedOffer']['owner']
    accountId = callback_data.id
    
    userAccount = await SimpleAPI.getDetails(r.userRoutes.userBanks, accountId)
    await state.update_data(userAccount = userAccount.json())

    await bot.send_message(
        call.from_user.id,
        text= await msg_maker.complete_set_new_bank(allData)
    )

    await bot.send_message(
        changerId,
        text= await msg_maker.changer_inform(changerId, allData)
    )
    await state.set_state(FSMSteps.GET_USER_PROOF)


async def get_user_proof(message: Message, state: FSMContext):
    '''
    '''

    allData = await state.get_data()
    changerId = allData['selectedOffer']['owner']
    offerId = allData['selectedOffer']['id']
    changerBank = allData['sellBank']
    userBank = allData['userAccount']['id']
    sellCurrency = allData['selectedOffer']['currency']
    sellAmount = allData['sellAmount']
    rate = allData['selectedOffer']['rate']
    buyAmount = sellAmount * rate
    accountId = message.from_user.id

    if message.photo:

        fileId = message.photo[-1].file_id
        proofType = 'photo'

    elif message.document:

        fileId = message.document.file_id
        proofType = 'document'

    data = {
        'changer': changerId,
        'offer': offerId,
        'user': accountId,
        'changerBank': changerBank,
        'userBank': userBank,
        'sellCurrency': sellCurrency,
        'buyCurrency': 'MNT',
        'sellAmount': sellAmount,
        'buyAmount': buyAmount,
        'rate': rate,
        'userSendMoneyDate': date.today(),
        'userProofType': proofType,
        'userProof': fileId,
    }

    response = await SimpleAPI.post(r.userRoutes.transactions, data=data)


    if proofType == 'photo':

        await bot.send_photo(
            changerId,
            photo = fileId,
            caption= await msg_maker.accept_user_transfer(),
            reply_markup= await changer_kb.accept_user_transfer(response.json()['id'])
        )

    if proofType == 'document':

        await bot.send_document(
            changerId, 
            document= fileId,
            caption= await msg_maker.accept_user_transfer(),
            reply_markup= await changer_kb.accept_user_transfer(response.json()['id'])
        )

    await bot.send_message(
        message.from_user.id,
        text= await msg_maker.user_inform(buyAmount)
        )







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
    dp.message.register(
        apply_new_buy_bank,
        F.text,
        FSMSteps.SET_BUY_BANK_ACCOUNT
    )
    dp.message.register(
        get_user_proof,
        F.content_type.in_({'photo', 'document'}),
        FSMSteps.GET_USER_PROOF
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
        choose_new_buy_bank_next,
        SetBuyBankData.filter(F.setNew == True)
    )
    dp.callback_query.register(
        use_old_buy_bank,
        SetBuyBankData.filter((F.setNew == False) & (F.id != 0))
    )

