import logging

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
from core.middlwares.exceptions import MaxLenError
from core.keyboards import (
    changer_kb,
)
from core.keyboards.callbackdata import (
    StuffEditData,
)




async def stuff_create_new_offer_currency(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: StuffEditData
):
    '''
    '''
    if callback_data.action == 'new_offer_currency':

        await state.update_data(new_currency = callback_data.value)
        await call.message.edit_text(
            text = msg.chr_enter_rate,
            reply_markup= await changer_kb.sfuff_cancel_button()
        )
        await state.set_state(FSMSteps.STUFF_OFFERS_RATE)

    elif callback_data.action == 'new_offer_currency_returned':

        await call.message.edit_text(
            text = msg.chr_enter_rate,
            reply_markup= await changer_kb.sfuff_cancel_button()
        )
        await state.set_state(FSMSteps.STUFF_OFFERS_RATE)



async def stuff_create_new_offer_rate(message: Message, state: FSMContext):
    '''
    '''
    await message.delete()
    data = await state.get_data()
    mainMsg = data.get('mainMsg')
    currency = data.get('new_currency')
    await state.update_data(accounts = [])
    
    try:

        value = message.text
        rate = float(value.replace(',', '.'))
            
    except (ValueError, AttributeError) as e:
        logging.error(e)
        await mainMsg.edit_text(
            text = msg.type_error_msg,
            reply_markup = await changer_kb.sfuff_cancel_button()
        )

    else:
        await state.update_data(new_rate = rate)
        await mainMsg.edit_text(
            text= await msg_maker.stuff_show_rate(rate, currency),
            reply_markup= await changer_kb.staff_accept_new_rate()
        )
        await state.set_state(FSMSteps.STUFF_OFFERS_MENU)    



async def stuff_create_new_offer_banks(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: StuffEditData
):
    '''
    '''
    data = await state.get_data()
    currency = data.get('new_currency')        

    params_usd = {
        'owner': call.from_user.id,
        'isActive': True,
        'currency__name': currency
    }
    params_mnt = {
        'owner': call.from_user.id,
        'isActive': True,
        'currency__name': 'MNT'
    }

    response = await SimpleAPI.get(
        r.changerRoutes.banks,
        params = params_usd
    )
    response_mnt = await SimpleAPI.get(
        r.changerRoutes.banks, 
        params = params_mnt
    )  
    banks = response.json()
    banks.extend(response_mnt.json())

    if callback_data.action == 'create_new_offer_banks':

        if len(banks):
            await call.message.edit_text(
                text = await msg_maker.stuff_create_new_offer_banks(currency),
                reply_markup= await changer_kb.stuff_create_new_offer_banks_dis_next(
                    banks
                )
            )

        else:
            await call.message.edit_text(
                text = msg.staff_zero_banks,
                reply_markup= await changer_kb.staff_zero_banks_buttons()
            )
        
    elif callback_data.action == 'staff_set_banks':

        account_id = callback_data.id
        accounts = data.get('accounts')

        if not accounts:
            accounts = {}

            for i in banks:
                accounts[i['currency']['name']] = []
                accounts[currency] = []
        
        await call.answer()

        for i in banks:
            if i['id'] == account_id and (i not in accounts[currency] or accounts['MNT']):
                accounts[i['currency']['name']].append(i)
                
        await state.update_data(accounts = accounts)

        await call.message.edit_text(
            text = await msg_maker.stuff_create_new_offer_banks(currency, accounts),
            reply_markup= await changer_kb.stuff_create_new_offer_banks(banks)
        )

    elif callback_data.action == 'staff_will_set_amount':

        accounts = data.get('accounts')

        if not accounts.get(currency):
            await call.answer(f'Вы не указали банк для {currency}', show_alert=True)

        if not accounts.get('MNT'):
            await call.answer(f'Вы не указали банк для MNT', show_alert=True)

        elif accounts.get(currency) and accounts.get('MNT'):
            await call.message.edit_text(
                text = msg.staff_will_set_amount,
                reply_markup= await changer_kb.staff_will_set_amount_kb()
            )



async def stuff_create_new_offer_amount(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: StuffEditData
):
    '''
    '''
    data = await state.get_data()
    currency = data.get('new_currency')

    await call.message.edit_text(
        text = await msg_maker.staff_set_min_amount(currency),
        reply_markup= await changer_kb.staff_set_min_amount()
    )
    await state.set_state(FSMSteps.STAFF_OFFERS_MINAMOUNT)



async def stuff_create_new_offer_min_amount(message: Message, state: FSMContext):
    '''
    '''
    await message.delete()
    data = await state.get_data()
    mainMsg = data.get('mainMsg')
    currency = data.get('new_currency')
    
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
        await state.update_data(new_min_amount = amount)
        await mainMsg.edit_text(
            text= await msg_maker.stuff_show_min_amount(amount, currency),
            reply_markup= await changer_kb.staff_accept_min_amount()
        )
        await state.set_state(FSMSteps.STUFF_OFFERS_MENU)    



async def stuff_create_new_offer_max_amount(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: StuffEditData
):
    '''
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



async def stuff_create_new_offer_max_amount_setter(message: Message, state: FSMContext):
    '''
    '''
    await message.delete()
    data = await state.get_data()
    mainMsg = data.get('mainMsg')
    currency = data.get('new_currency')
    
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
        callback_data: StuffEditData
):
    '''
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
        


async def stuff_create_new_offer_name_setter(message: Message, state: FSMContext):
    '''
    '''
    await message.delete()
    data = await state.get_data()
    mainMsg = data.get('mainMsg')
    
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
        callback_data: StuffEditData
):
    '''
    '''
    data = await state.get_data()
    offer_name = data.get('offer_name')
    currency = data.get('new_currency')
    rate = data.get('new_rate')
    banks_accounts = data.get('accounts')
    refBanks_id = [i['id'] for i in banks_accounts.get('MNT')]
    currencyBanks_id = [i['id'] for i in banks_accounts.get(currency)]
    min_amount = data.get('new_min_amount')
    max_amount = data.get('new_max_amount')

    post_data = {

        'owner': call.from_user.id,
        'bannerName': offer_name,
        'currency': currency,
        'rate': rate,
        'refBanks_id': refBanks_id,
        'currencyBanks_id': currencyBanks_id,
        'minAmount': min_amount,
        'maxAmount': max_amount,
        'isActive': True,

    }

    if callback_data.action == 'staff_set_offer_final':
        await call.message.edit_text(
            text = await msg_maker.staff_create_offer_show_final_text(
                post_data,
                banks_accounts
            ),
            reply_markup = await changer_kb.staff_create_offer_final_text_kb()
        )

    elif callback_data.action == 'staff_post_offer':
        
        await SimpleAPI.post(r.changerRoutes.myOffers, post_data)
        await call.message.edit_text(
            text= msg.staff_create_new_offer_succes,
            reply_markup= await changer_kb.staff_create_new_offer_succes()
        )

    elif callback_data.action == 'staff_post_offet_non_active':
        
        post_data['isActive'] = False        
        await SimpleAPI.post(r.changerRoutes.myOffers, post_data)
        await call.message.edit_text(
            text= msg.staff_create_new_offer_succes_non_active,
            reply_markup= await changer_kb.staff_create_new_offer_succes()
        )



# async def register_message_handlers_changer(dp: Dispatcher):
#     '''Registry message handlers there.
#     '''
    # dp.message.register(

    #     get_changer_proof,
    #     FSMSteps.GET_CHANGER_PROOF        
    
    # )




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
        StuffEditData.filter(
        
            F.action.in_({
                'new_offer_currency',
                'new_offer_currency_returned'
            })
        )
    )
    dp.callback_query.register(
        
        stuff_create_new_offer_banks,
        StuffEditData.filter(
        
            F.action.in_({
                'create_new_offer_banks',
                'staff_set_banks',
                'staff_will_set_amount',
            })
        )
    )
    dp.callback_query.register(
        
        stuff_create_new_offer_amount,
        StuffEditData.filter(
        
            F.action.in_({
                'set_min&max_amount'
            })
        )
    )
    dp.callback_query.register(
        
        stuff_create_new_offer_max_amount,
        StuffEditData.filter(
        
            F.action.in_({
                'staff_set_max_amount',
                'staff_pass_min_amount'
            })
        )
    )
    dp.callback_query.register(
        
        stuff_create_new_offer_name,
        StuffEditData.filter(
        
            F.action.in_({   
                'staff_new_offer_name',
                'staff_set_offer_name',
                'staff_pass_max_amount'
            })
        )
    )
    dp.callback_query.register(

        stuff_create_new_offer_final,
        StuffEditData.filter(
            
            F.action.in_({
                'staff_set_offer_final',
                'staff_post_offer',
                'staff_post_offet_non_active',
            })
        )
    )
