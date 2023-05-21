import logging
from httpx import Response

from aiogram.fsm.context import FSMContext
from aiogram.types.callback_query import CallbackQuery
from aiogram.types import Message
from aiogram import F, Bot, Dispatcher

from core.middlwares.routes import r    # Dataclass whith all api routes
from core.utils import msg_maker
from core.api_actions.bot_api import SimpleAPI
from core.middlwares.settigns import appSettings
from core.utils.bot_fsm import FSMSteps
from core.utils import msg_var as msg
from core.middlwares.exceptions import MaxLenError, ResponseError
from core.keyboards import (
    changer_kb,
)
from core.keyboards.callbackdata import (
    StaffEditData,
)



async def stuff_create_new_offer_currency(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: StaffEditData
):
    '''
    Changer set rate for new offer
    '''
    if callback_data.action in ['new_buy_offer_currency',
                                'new_sell_offer_currency']:
        # get offer type from previous step
        u_type: str = callback_data.action
        type: str = 'sell' if u_type == 'new_sell_offer_currency' else 'buy'
        # save this values to bot state
        await state.update_data(new_offer_type = type)
        await state.update_data(new_currency = callback_data.value)
        await call.message.edit_text(
            text = msg.chr_enter_rate,
            reply_markup = await changer_kb.sfuff_cancel_button()
        )
        await state.set_state(FSMSteps.STUFF_OFFERS_RATE)
    # if user was returned from next step for change offer rate
    elif callback_data.action == 'new_offer_currency_returned':
        await call.message.edit_text(
            text = msg.chr_enter_rate,
            reply_markup = await changer_kb.sfuff_cancel_button()
        )
        await state.set_state(FSMSteps.STUFF_OFFERS_RATE)



async def stuff_create_new_offer_rate(message: Message, state: FSMContext):
    '''
    Handler make validation message value
    '''
    data: dict = await state.get_data()
    mainMsg: Message = data.get('mainMsg')
    currency: str = data.get('new_currency')
    await state.update_data(accounts = [])
    # delete user message from screnn
    await message.delete()
    # make validation
    try:
        value = message.text
        rate = float(value.replace(',', '.').replace(' ', ''))
    except (ValueError, AttributeError) as e:
        logging.error(e)
        await mainMsg.edit_text(
            text = msg.type_error_msg,
            reply_markup = await changer_kb.sfuff_cancel_button()
        )
    else:
        # if all ok
        await state.update_data(new_rate = rate)
        await mainMsg.edit_text(
            text= await msg_maker.stuff_show_rate(rate, currency),
            reply_markup= await changer_kb.staff_accept_new_rate()
        )
        await state.set_state(FSMSteps.STUFF_OFFERS_MENU)    



async def stuff_create_new_offer_banks(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: StaffEditData,
        bot: Bot
):
    '''
    Hanlder allows the user select banks accounts that
    will be add to new offer 
    '''
    data: dict = await state.get_data()
    currency: str = data.get('new_currency')        
    # prepare 'get' params separately
    params_curr = {
        'owner': call.from_user.id,
        'isActive': True,
        'currency__name': currency
    }
    params_ref = {
        'owner': call.from_user.id,
        'isActive': True,
        'currency__name': 'MNT'
    }
    # get info from backend
    try:
        response_curr: Response = await SimpleAPI.get(
            r.changerRoutes.banks,
            params = params_curr
        )
        response_ref: Response = await SimpleAPI.get(
            r.changerRoutes.banks, 
            params = params_ref
        )
        if response_curr.status_code != 200\
            or response_ref.status_code != 200:
            raise ResponseError()
    except ResponseError as e:
        await call.message.edit_text(
            text=msg.error_msg,
            reply_markup= await changer_kb.error_kb(),
        )
        await bot.send_message(
            appSettings.botSetting.devStaffId,
            text=(
                'handlers.changers.create_offer.py '
                '-> stuff_create_new_offer_banks\n'
                f'{repr(e)}\n'
                f'{response_curr.json()}'
                f'{response_ref.json()}'
            )
        )
        logging.exception(
            f'{e} - {response_ref.json()}'
            f'{e} - {response_curr.json()}'
        )
    except Exception as e:
        await call.message.edit_text(
            text=msg.error_msg,
            reply_markup= await changer_kb.error_kb(),
        )
        await bot.send_message(
            appSettings.botSetting.devStaffId,
            text=(
                'handlers.changers.create_offer.py '
                '-> stuff_create_new_offer_banks\n'
                f'{repr(e)}'
            )
        )
        logging.exception(e)
    else:
        banks: list = response_curr.json()
        banks.extend(response_ref.json())
        # if user is in the handler for first time
        if callback_data.action == 'create_new_offer_banks':
            await call.answer()
            if banks:
                # user have any accounts relevant for filter 
                await call.message.edit_text(
                    text=await msg_maker.stuff_create_new_offer_banks(
                        currency
                    ),
                    reply_markup=await changer_kb.stuff_new_offer_banks_w_next(
                        banks
                    )
                )
            else:
                # if banks list is empty
                await call.message.edit_text(
                    text = msg.staff_zero_banks,
                    reply_markup= await changer_kb.staff_zero_banks_buttons()
                )
        elif callback_data.action == 'staff_set_banks':
            await call.answer()
            account_id = callback_data.id
            accounts = data.get('accounts')
            # create accounts dict if it is not exists in bot state
            if not accounts:
                accounts = {}
                # create keys in dict
                for i in banks:
                    accounts[i['currency']['name']] = []
                    # accounts[currency] = []
            for i in banks:
                # checking the account for doubling
                if i['id'] == account_id:
                    if i not in accounts[currency] and\
                        i not in accounts['MNT']:
                            accounts[i['currency']['name']].append(i)
            # save accounts data to bot state storage
            await state.update_data(accounts = accounts)
            # show of the selected accounts to the user
            await call.message.edit_text(
                text=await msg_maker.stuff_create_new_offer_banks(
                    currency,
                    accounts
                ),
                reply_markup=await changer_kb.stuff_create_new_offer_banks(
                    banks
                )
            )
        elif callback_data.action == 'staff_will_set_amount':
            accounts: dict = data.get('accounts')
            # check users choice. He must set accounts for all currency.
            # check it for offer currency
            if not accounts.get(currency):
                await call.answer(
                    f'Вы не указали банк для {currency}',
                    show_alert=True
                )
            # check it for reference currency
            if not accounts.get('MNT'):
                await call.answer(
                    f'Вы не указали банк для MNT',
                    show_alert=True
                )
            # if all ok - switch to next step
            elif accounts.get(currency) and accounts.get('MNT'):
                await call.message.edit_text(
                    text = msg.staff_will_set_amount,
                    reply_markup= await changer_kb.staff_will_set_amount_kb()
                )



async def stuff_create_new_offer_amount(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: StaffEditData
):
    '''
    This handler will calling if user want set min amount
    for new offer. 
    '''
    data: dict = await state.get_data()
    currency: str = data.get('new_currency')
    await call.message.edit_text(
        text = await msg_maker.staff_set_min_amount(currency),
        reply_markup= await changer_kb.staff_set_min_amount()
    )
    await state.set_state(FSMSteps.STAFF_OFFERS_MINAMOUNT)



async def stuff_create_new_offer_min_amount(
        message: Message,
        state: FSMContext
    ):
    '''
    Min amount setter. Calling from previous step.
    Make validation of message value.
    '''
    # delete user message with min amount value
    await message.delete()
    data: dict = await state.get_data()
    mainMsg: Message = data.get('mainMsg')
    currency: str = data.get('new_currency')
    # make validation
    try:
        value = message.text
        amount = float(value.replace(',', '.').replace(' ', ''))
    except ValueError as e:
        await mainMsg.edit_text(
            text = msg.type_error_msg,
            reply_markup = await changer_kb.sfuff_cancel_button()
        )
    else:
        await state.update_data(new_min_amount = amount)
        await mainMsg.edit_text(
            text= await msg_maker.stuff_show_min_amount(amount, currency),
            reply_markup= await changer_kb.staff_accept_min_amount()
        )
        await state.set_state(FSMSteps.STUFF_OFFERS_MENU)    



async def stuff_create_new_offer_max_amount(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: StaffEditData
):
    '''
    This handler will calling if user want set max amount
    for new offer. 
    '''
    data = await state.get_data()
    currency = data.get('new_currency')

    if callback_data.action == 'staff_pass_min_amount':
        await state.update_data(new_min_amount = None)

    await call.message.edit_text(
        text = await msg_maker.stuff_set_max_amount(currency),
        reply_markup = await changer_kb.staff_set_max_amount()
    )
    await state.set_state(FSMSteps.STAFF_OFFERS_MAXAMOUNT)



async def stuff_create_new_offer_max_amount_setter(
        message: Message,
        state: FSMContext
    ):
    '''
    Max amount setter. Calling from previous step.
    Make validation of message value.
    '''
    # delete user message with max amount value
    await message.delete()
    data: dict = await state.get_data()
    mainMsg: Message = data.get('mainMsg')
    currency: str = data.get('new_currency')
    # make validation
    try:
        value = message.text
        amount = float(value.replace(',', '.'))
    except ValueError as e:
        logging.error(e)
        await mainMsg.edit_text(
            text = msg.type_error_msg,
            reply_markup = await changer_kb.sfuff_cancel_button()
        )
    else:
        await state.update_data(new_max_amount = amount)
        await mainMsg.edit_text(
            text= await msg_maker.stuff_show_max_amount(amount, currency),
            reply_markup= await changer_kb.staff_accept_max_amount()
        )
        await state.set_state(FSMSteps.STUFF_OFFERS_MENU)    
    


async def stuff_create_new_offer_name(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: StaffEditData
):
    '''
    Handler will calling if user want set comment
    for new offer. 
    '''
    actions = ['staff_pass_max_amount', 'staff_new_offer_name']
    if callback_data.action in actions:
        if callback_data.action == 'staff_pass_max_amount':
            await state.update_data(new_max_amount = None)
        await call.message.edit_text(
            text = msg.staff_will_set_name,
            reply_markup = await changer_kb.staff_will_set_name()
        )
    elif callback_data.action == 'staff_set_offer_name':
        await call.message.edit_text(
            text = msg.staff_set_offer_name,
            reply_markup = await changer_kb.sfuff_cancel_button()
        )
        await state.set_state(FSMSteps.STAFF_OFFERS_SETNAME)
        


async def stuff_create_new_offer_name_setter(
        message: Message,
        state: FSMContext
    ):
    '''
    Offer comment setter. Make validation for message value, 
    and if all ok - switch to next step
    '''
    await message.delete()
    data: dict = await state.get_data()
    mainMsg: Message = data.get('mainMsg')
    # make validation
    try:
        description = message.text
        if len(description) > 50:
            raise MaxLenError
    except MaxLenError:
        await mainMsg.edit_text(
            text = await msg_maker.staff_max_len_message(len(description)),
            reply_markup = await changer_kb.sfuff_cancel_button()
        )
    else:
        await state.update_data(offer_name = description)
        await mainMsg.edit_text(
            text= await msg_maker.staff_show_offer_name(description),
            reply_markup= await changer_kb.staff_accept_offer_name()
        )
        await state.set_state(FSMSteps.STUFF_OFFERS_MENU)    
    


async def stuff_create_new_offer_final(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: StaffEditData,
        bot: Bot
):
    '''
    This handler try to create new changer offer in backend.
    '''
    # get all values for prepare post data
    data: dict = await state.get_data()
    offer_name: str = data.get('offer_name')
    currency: str = data.get('new_currency')
    rate: float = data.get('new_rate')
    type: str = data.get('new_offer_type')
    accounts: dict = data.get('accounts')
    refBanks_id: list = [i['id'] for i in accounts.get('MNT')]
    currencyBanks_id: list = [i['id'] for i in accounts.get(currency)]
    min_amount: float = data.get('new_min_amount')
    max_amount: float = data.get('new_max_amount')
    # prepare post data
    post_data = {
        'owner': call.from_user.id,
        'bannerName': offer_name,
        'currency': currency,
        'rate': rate,
        'type': type,
        'refBanks_id': refBanks_id,
        'currencyBanks_id': currencyBanks_id,
        'minAmount': min_amount,
        'maxAmount': max_amount,
        'isActive': True,
    }
    # show to user all information about new offer for
    # he can check  all values
    if callback_data.action == 'staff_set_offer_final':
        await call.message.edit_text(
            text = await msg_maker.staff_create_offer_show_final_text(
                post_data,
                accounts
            ),
            reply_markup=await changer_kb.staff_create_offer_final_text_kb()
        )
    # if all offer values are correctly - he allow post offer
    else:
        if callback_data.action == 'staff_post_offet_non_active':
            # if user want save new offer as draft
            post_data['isActive'] = False
        try:
            new_offer: Response = await SimpleAPI.post(
                r.changerRoutes.myOffers,
                post_data
            )
            if new_offer.status_code != 201:
                raise ResponseError()
        except ResponseError as e:
            await call.message.edit_text(
                text=msg.error_msg,
                reply_markup= await changer_kb.error_kb(),
            )
            await bot.send_message(
                appSettings.botSetting.devStaffId,
                text=(
                    'handlers.changers.create_offer.py '
                    '-> stuff_create_new_offer_final\n'
                    f'{repr(e)}\n'
                    f'{new_offer.json()}'
                )
            )
            logging.exception(f'{e} - {new_offer.json()}')
        except Exception as e:
            await call.message.edit_text(
                text=msg.error_msg,
                reply_markup= await changer_kb.error_kb(),
            )
            await bot.send_message(
                appSettings.botSetting.devStaffId,
                text=(
                    'handlers.changers.create_offer.py '
                    '-> stuff_create_new_offer_final\n'
                    f'{repr(e)}'
                )
            )
            logging.exception(e)
        else:
            await call.message.edit_text(
                text=msg.staff_create_new_offer_succes_non_active,
                reply_markup=await changer_kb.staff_create_new_offer_succes()
            )



async def setup_create_offer_handlers(dp: Dispatcher):
    '''Register handlers there.
    '''
    dp.message.register(
    
        stuff_create_new_offer_rate,
        FSMSteps.STUFF_OFFERS_RATE,
        F.text
    
    )
    dp.message.register(
    
        stuff_create_new_offer_min_amount,
        FSMSteps.STAFF_OFFERS_MINAMOUNT,
        F.text
    
    )
    dp.message.register(
    
        stuff_create_new_offer_max_amount_setter,
        FSMSteps.STAFF_OFFERS_MAXAMOUNT,
        F.text
    
    )
    dp.message.register(
    
        stuff_create_new_offer_name_setter,
        FSMSteps.STAFF_OFFERS_SETNAME,
        F.text
    
    )
    dp.callback_query.register(

        stuff_create_new_offer_currency,
        StaffEditData.filter(
        
            F.action.in_({
                'new_sell_offer_currency',
                'new_buy_offer_currency',
                'new_offer_currency_returned'
            })
        )
    )
    dp.callback_query.register(
        
        stuff_create_new_offer_banks,
        StaffEditData.filter(
        
            F.action.in_({
                'create_new_offer_banks',
                'staff_set_banks',
                'staff_will_set_amount',
            })
        )
    )
    dp.callback_query.register(
        
        stuff_create_new_offer_amount,
        StaffEditData.filter(
        
            F.action.in_({
                'set_min&max_amount'
            })
        )
    )
    dp.callback_query.register(
        
        stuff_create_new_offer_max_amount,
        StaffEditData.filter(
        
            F.action.in_({
                'staff_set_max_amount',
                'staff_pass_min_amount'
            })
        )
    )
    dp.callback_query.register(
        
        stuff_create_new_offer_name,
        StaffEditData.filter(
        
            F.action.in_({   
                'staff_new_offer_name',
                'staff_set_offer_name',
                'staff_pass_max_amount'
            })
        )
    )
    dp.callback_query.register(

        stuff_create_new_offer_final,
        StaffEditData.filter(
            
            F.action.in_({
                'staff_set_offer_final',
                'staff_post_offer',
                'staff_post_offet_non_active',
            })
        )
    )
