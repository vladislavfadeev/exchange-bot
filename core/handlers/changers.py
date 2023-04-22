from datetime import datetime
import logging
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.types.callback_query import CallbackQuery
from aiogram.types import Message
from aiogram import F
from create_bot import bot, dp
from core.middlwares.routes import r    # Dataclass whith all api routes
from core.utils import msg_maker
from core.api_actions.bot_api import SimpleAPI
from core.utils.bot_fsm import FSMSteps
from core.utils import msg_var as msg
from core.keyboards import changer_kb
from core.keyboards import user_kb
from core.middlwares.exceptions import MaxLenError
from core.keyboards.callbackdata import (
    CurrencyData,
    StuffEditData,
    StuffOfficeData,
    UserProofActions,
)


async def offer_menu(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: StuffOfficeData
):
    '''
    '''
    await state.set_state(FSMSteps.STUFF_OFFERS)
    data = await state.get_data()
    mainMsg = data.get('mainMsg')
    messageList = data.get('messageList')

    try:
        await mainMsg.delete()
    except:
        pass

    if messageList:

        for i in messageList:
            try:
                await i.delete()
            except:
                pass

    mainMsg = await bot.send_message(
        call.from_user.id,
        text = await msg_maker.stuff_offer_menu(),
        reply_markup = await changer_kb.stuff_offer_menu_buttons()
    )
    await state.update_data(mainMsg = mainMsg)



async def offer_menu_give_result(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: StuffOfficeData
):
    '''
    '''
    data = await state.get_data()

    if callback_data.action == 'create_new':

        await call.message.edit_text(
            text= await msg_maker.stuff_set_currency(),
            reply_markup= await changer_kb.set_sell_currency_button()
        )

    elif callback_data.action == 'edit_offers':

        params = {
            'owner': call.from_user.id,
            'isActive': True,
            'isDeleted': False
        }
        response = await SimpleAPI.get(
            r.changerRoutes.myOffers,
            params=params
        )
        offer_list = response.json()

        if len(offer_list):

            await state.update_data(offerList = offer_list)
            messages = await msg_maker.offer_list_msg_maker(offer_list)

            await call.message.delete()

            messageList = []
            counter = 0
            for i in range(len(messages)):
                
                counter += 1
                isLatest = True if counter == len(messages) else False
                value = offer_list[i]

                self_msg = await bot.send_message(
                    call.from_user.id,
                    text = messages[i],
                    reply_markup= await changer_kb.stuff_edit_offer_list_buttons(
                        value['id'],
                    )
                )
                if isLatest:
                    sep_msg = await bot.send_message(
                        call.from_user.id,
                        text = msg.separator,
                        reply_markup = await changer_kb.staff_back_to_offer_menu()
                    )
                    messageList.append(sep_msg)

                messageList.append(self_msg)

            await state.update_data(messageList = messageList)

        else:
            await call.message.edit_text(
                text = msg.stuff_zero_offer,
                reply_markup = await changer_kb.sfuff_cancel_button()
            )

    elif callback_data.action == 'inactive':
        
        params = {
            'owner': call.from_user.id,
            'isActive': False,
            'isDeleted': False
        }

        response = await SimpleAPI.get(
            r.changerRoutes.myOffers,
            params = params
        )
        inactive_offers = response.json(

        )
        if len(inactive_offers):

            await state.update_data(offerList = inactive_offers)
            messages = await msg_maker.offer_list_msg_maker(inactive_offers)

            await call.message.delete()

            messageList = []
            counter = 0
            for i in range(len(messages)):
                
                counter += 1
                isLatest = True if counter == len(messages) else False
                char = inactive_offers[i]

                self_msg = await bot.send_message(
                    call.from_user.id,
                    text = messages[i],
                    reply_markup= await changer_kb.stuff_edit_inactive_offers_buttons(
                        char['id']
                    )
                )
                if isLatest:
                    sep_msg = await bot.send_message(
                        call.from_user.id,
                        text = msg.separator,
                        reply_markup = await changer_kb.staff_back_to_offer_menu()
                    )
                    messageList.append(sep_msg)

                messageList.append(self_msg)

            await state.update_data(messageList = messageList)

        else:
            await call.message.edit_text(
                text = msg.stuff_zero_offer,
                reply_markup = await changer_kb.sfuff_cancel_button()
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
        await state.set_state(FSMSteps.STUFF_OFFERS)    



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
        
        await call.answer()

        for i in banks:
            if i['id'] == account_id and i not in accounts:
                accounts.append(i)
                
        await state.update_data(accounts = accounts)

        await call.message.edit_text(
            text = await msg_maker.stuff_create_new_offer_banks(currency, accounts),
            reply_markup= await changer_kb.stuff_create_new_offer_banks(banks)
        )

    elif callback_data.action == 'staff_will_set_amount':

        accounts = data.get('accounts')
        currency_list = [i['currency']['name'] for i in accounts]

        if currency not in currency_list:
            await call.answer(f'Вы не указали банк для {currency}', show_alert=True)

        if 'MNT' not in currency_list:
            await call.answer(f'Вы не указали банк для MNT', show_alert=True)

        elif currency in currency_list and 'MNT' in currency_list:
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
        await state.set_state(FSMSteps.STUFF_OFFERS)    



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
        await state.set_state(FSMSteps.STUFF_OFFERS)    
    


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
        await state.set_state(FSMSteps.STUFF_OFFERS)    
    


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
    banks_id = [i['id'] for i in banks_accounts]
    min_amount = data.get('new_min_amount')
    max_amount = data.get('new_max_amount')

    post_data = {

        'owner': call.from_user.id,
        'bannerName': offer_name,
        'currency': currency,
        'rate': rate,
        'banks_id': banks_id,
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



async def staff_edit_offer(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: StuffEditData
):
    '''
    '''
    offer_id = callback_data.id
    response = await SimpleAPI.getDetails(
        r.changerRoutes.myOffers,
        offer_id
    )
    offer = response.json()
    offer_currency = response.json()['currency']
    await state.update_data(editable_offer_id = offer_id)
    await state.update_data(offer_currency = offer_currency)

    data = await state.get_data()
    msg_list = data.get('messageList')
    
    try:

        for i in range(len(msg_list)):
            await msg_list[i].delete()

    except Exception as e:
        logging.exception(e)

    else:
        mainMsg = await bot.send_message(
            call.from_user.id,
            text = await msg_maker.staff_edit_offer_show(offer),
            reply_markup= await changer_kb.staff_edit_offer_show_kb(offer)
        )
        await state.update_data(mainMsg = mainMsg)


    
async def staff_edit_offer_steps(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: StuffEditData
):
    '''
    '''
    data = await state.get_data()
    currency = data.get('offer_currency')

    if callback_data.action == 'staff_edit_offer_name':
        
        await call.message.edit_text(
            text = msg.staff_set_offer_name,
            reply_markup = await changer_kb.staff_back_to_offer_menu()
        )
        await state.update_data(editable_key = 'bannerName')
        await state.set_state(FSMSteps.STAFF_EDIT_VALUES)

    elif callback_data.action == 'staff_edit_offer_rate':
        
        await call.message.edit_text(
            text = msg.staff_edit_offer_new_rate,
            reply_markup = await changer_kb.staff_back_to_offer_menu()
        )
        await state.update_data(editable_key = 'rate')
        await state.set_state(FSMSteps.STAFF_EDIT_VALUES)

    elif callback_data.action == 'staff_edit_offer_min_amount':
        
        await call.message.edit_text(
            text = await msg_maker.staff_set_min_amount(currency),
            reply_markup = await changer_kb.staff_back_to_offer_menu()
        )
        await state.update_data(editable_key = 'minAmount')
        await state.set_state(FSMSteps.STAFF_EDIT_VALUES)

    elif callback_data.action == 'staff_edit_offer_max_amount':

        await call.message.edit_text(
            text = await msg_maker.stuff_set_max_amount(currency),
            reply_markup = await changer_kb.staff_back_to_offer_menu()
        )
        await state.update_data(editable_key = 'maxAmount')
        await state.set_state(FSMSteps.STAFF_EDIT_VALUES)



async def staff_edit_offer_values_checker(
        message: Message,
        state: FSMContext
):
    '''
    '''
    await message.delete()
    data = await state.get_data()
    editable_key = data.get('editable_key')
    mainMsg = data.get('mainMsg')
    currency = data.get('offer_currency')

    if editable_key == 'bannerName':
        
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
            await state.update_data(editable_field = description)

            decline_edit_name = 'staff_edit_offer_name'

            await mainMsg.edit_text(
                text= await msg_maker.staff_show_offer_name(description),
                reply_markup= await changer_kb.staff_edit_offer_values(
                    decline_edit_name
                )
            )

    elif editable_key == 'rate':
    
        try:

            value = message.text
            rate = float(value.replace(',', '.'))
                
        except (ValueError, AttributeError) as e:
            logging.error(e)
            await mainMsg.edit_text(
                text = msg.staff_edit_offer_new_rate_error,
                reply_markup = await changer_kb.sfuff_cancel_button()
            )

        else:
            await state.update_data(editable_field = rate)

            decline_edit_rate = 'staff_edit_offer_rate'

            await mainMsg.edit_text(
                text= await msg_maker.stuff_show_rate(rate, currency),
                reply_markup= await changer_kb.staff_edit_offer_values(
                    decline_edit_rate
                )
            )

    elif editable_key in ['minAmount', 'maxAmount']:

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

            await state.update_data(editable_field = amount)

            if editable_key == 'minAmount':
                
                decline_edit_min_sum = 'staff_edit_offer_min_amount'

                await mainMsg.edit_text(
                    text= await msg_maker.stuff_show_min_amount(amount, currency),
                    reply_markup= await changer_kb.staff_edit_offer_values(
                        decline_edit_min_sum
                    )
                )
            
            elif editable_key == 'maxAmount':

                decline_edit_max_sum = 'staff_edit_offer_max_amount'

                await mainMsg.edit_text(
                    text= await msg_maker.stuff_show_max_amount(amount, currency),
                    reply_markup= await changer_kb.staff_edit_offer_values(
                        decline_edit_max_sum
                    )
                )

    await state.set_state(FSMSteps.STUFF_OFFERS)    



async def staff_edit_offer_banks(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: StuffEditData
):
    '''
    '''
    data = await state.get_data()
    currency = data.get('offer_currency')

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

    if callback_data.action == 'staff_edit_offer_banks':

        offer_id = callback_data.id
        await state.update_data(editable_offer_id = offer_id)

        if len(banks):
            await call.message.edit_text(
                text = await msg_maker.stuff_create_new_offer_banks(currency),
                reply_markup= await changer_kb.stuff_edit_offer_banks_dis_next(
                    banks
                )
            )

        else:
            await call.message.edit_text(
                text = msg.staff_zero_banks,
                reply_markup= await changer_kb.staff_zero_banks_buttons()
            )
        
    elif callback_data.action == 'staff_edit_offer_banks_set':

        account_id = callback_data.id
        accounts = data.get('editable_accounts')
        
        if not accounts:
            accounts = []

        await call.answer()

        for i in banks:
            if i['id'] == account_id and i not in accounts:
                accounts.append(i)
                
        await state.update_data(editable_accounts = accounts)

        await call.message.edit_text(
            text = await msg_maker.stuff_create_new_offer_banks(currency, accounts),
            reply_markup= await changer_kb.stuff_edit_offer_banks(banks)
        )
    
    elif callback_data.action == 'staff_edit_offer_banks_patch':

        accounts = data.get('editable_accounts')
        currency_list = [i['currency']['name'] for i in accounts]

        if currency not in currency_list:
            await call.answer(f'Вы не указали банк для {currency}', show_alert=True)

        if 'MNT' not in currency_list:
            await call.answer(f'Вы не указали банк для MNT', show_alert=True)

        else:
            new_banks_id = [i['id'] for i in accounts]
            offer_id = data.get('editable_offer_id')

            patch_data = {
                'banks_id': new_banks_id
            }
            await SimpleAPI.patch(
                r.changerRoutes.myOffers,
                offer_id,
                patch_data
            )
            await call.message.edit_text(
                text = msg.staff_edit_offer_banks_success,
                reply_markup = await changer_kb.staff_edit_offer_succes_kb()
            )



async def staff_show_banks_account(                                # Доделать после проработки проверки!!!!!
        call: CallbackQuery,
        state: FSMContext,
        callback_data: StuffOfficeData
):
    ''' 
    '''
    await state.set_state(FSMSteps.STUFF_ACCOUNTS)
    changer_id = call.from_user.id

    params = {
        'owner': changer_id,
        'isDeleted': False
    }

    response = await SimpleAPI.get(
        r.changerRoutes.banks,
        params
    )
    banks_list = response.json()

    if len(banks_list):

        # accounts_list = [i['id'] for i in banks_list]
        
        # for i in banks_list:
        #     accounts_dict = 
        await call.message.delete()

        await state.update_data(staff_editable_banks = banks_list)
        messages = await msg_maker.staff_show_editable_banks(banks_list)

        messageList = []
        counter = 0
        for i in range(len(messages)):

            counter += 1
            isLatest = True if counter == len(messages) else False
            char = banks_list[i]
            isActive = char['isActive']

            self_msg = await bot.send_message(
                call.from_user.id,
                text = messages[i],
                reply_markup = await changer_kb.staff_edit_banks_accounts(
                    char['id'],
                    isActive
                )
            )
            if isLatest:
                sep_msg = await bot.send_message(
                    call.from_user.id,
                    text = msg.separator,
                    reply_markup = await changer_kb.sfuff_cancel_button()
                )
                messageList.append(sep_msg)
            messageList.append(self_msg)

        await state.update_data(messageList = messageList)

    else:
        await call.message.edit_text(
            text = msg.staff_show_banks_account,
            reply_markup = await changer_kb.staff_zero_banks_buttons()
        )



async def staff_edit_offer_values_setter(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: StuffEditData
):
    '''
    '''
    data = await state.get_data()
    message_list = data.get('messageList')

    if callback_data.action == 'staff_edit_accept':
        
        key = data.get('editable_key')
        value = data.get('editable_field')
        offer_id = data.get('editable_offer_id')

        patch_data = {
            key: value
        }

        await SimpleAPI.patch(
            r.changerRoutes.myOffers,
            offer_id,
            patch_data
        )
        await call.message.edit_text(
            text = msg.staff_edit_offer_success,
            reply_markup = await changer_kb.staff_edit_offer_succes_kb()
        )

    elif callback_data.action == 'staff_delete_offer':
        
        offer_id = callback_data.id

        patch_data = {
            'isDeleted': True
        }

        await SimpleAPI.patch(
            r.changerRoutes.myOffers,
            offer_id,
            patch_data
        )
        await call.answer('Выполнено!', show_alert=True)

        if len(message_list) > 1:
            await call.message.delete()
        
        elif len(message_list) == 1:
            await call.message.edit_text(
                text = await msg_maker.stuff_offer_menu(),
                reply_markup = await changer_kb.stuff_offer_menu_buttons()
            )

        # await call.message.edit_text(
        #     text = msg.staff_delete_offer_success,
        #     reply_markup = await changer_kb.staff_edit_offer_succes_kb()
        # )
    
    elif callback_data.action in ['staff_publish_offer', 'staff_unpublish_offer']:
        
        offer_id = callback_data.id
        value = True if callback_data.action == 'staff_publish_offer' else False

        patch_data = {
            'isActive': value
        }
        await SimpleAPI.patch(
            r.changerRoutes.myOffers,
            offer_id,
            patch_data
        )
        await call.answer('Выполнено!', show_alert=True)

        if len(message_list) > 1:
            await call.message.delete()
        
        elif len(message_list) == 1:
            await call.message.edit_text(
                text = await msg_maker.stuff_offer_menu(),
                reply_markup = await changer_kb.stuff_offer_menu_buttons()
            )

    elif callback_data.action in [                              # Доделать после проработки проверки!!!! 
        'staff_edit_banks_active',
        'staff_edit_banks_inactive',
        'staff_edit_banks_delete'
        ]:

        account_id = callback_data.id
        action = callback_data.action

        key = 'isActive' if action in [
                            'staff_edit_banks_active',
                            'staff_edit_banks_inactive'] else 'isDeleted'
        
        value = True if action in [
                            'staff_edit_banks_active',
                            'staff_edit_banks_delete'] else False

        patch_data = {
            key: value
        }



async def staff_show_transfers(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: StuffEditData
):
    '''
    '''
    await state.set_state(FSMSteps.STAFF_TRANSFRES)
    data = await state.get_data()
    uncompleted_transfers = data.get('user_transfers')

    if not uncompleted_transfers:

        params = {
            'changer': call.from_user.id,
            'claims': False,
            'isCompleted': False
        }
        response = await SimpleAPI.get(
            r.changerRoutes.transactions,
            params=params
        )
        uncompleted_transfers = response.json()
        await state.update_data(user_transfers = uncompleted_transfers)

    if len(uncompleted_transfers):

        await call.message.delete()

        messages = await msg_maker.staff_show_uncompleted_transfers(
            uncompleted_transfers
        )
        counter = 0
        messageList = []

        for i in range(len(uncompleted_transfers)):

            counter += 1
            isLatest = True if counter == len(uncompleted_transfers) else False
            char = uncompleted_transfers[i]

            self_msg = await bot.send_message(
                call.from_user.id,
                text = messages[i],
                reply_markup = await changer_kb.staff_show_transfers(char['id'])
            )
            if isLatest:
                sep_msg = await bot.send_message(
                    call.from_user.id,
                    text = msg.separator,
                    reply_markup = await changer_kb.sfuff_cancel_button()
                )
                messageList.append(sep_msg)

            messageList.append(self_msg)
        
        await state.update_data(messageList = messageList)

    else:
        await call.message.edit_text(
            text = msg.staff_empty_uncompleted_transfers,
            reply_markup = changer_kb.sfuff_cancel_button()
        )



async def staff_show_transfer_detail(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: StuffEditData
):
    '''
    '''
    data = await state.get_data()
    tr_id = callback_data.id
    transfer_detail = data['user_transfers'][tr_id]
    # mainMsg = data.get('mainMsg')
    messageList = data.get('messageList')
    await state.update_data(ansvered_transfer_id = tr_id)

    # try:
    #     await mainMsg.delete()
    # except:
    #     pass

    if callback_data.action == 'staff_transfers_get_detail':

        if messageList:

            for i in messageList:
                try:
                    await i.delete()
                except:
                    pass

        if transfer_detail['userProofType'] == 'photo':

            mainMsg = bot.send_photo(

                call.from_user.id,
                photo = transfer_detail['userProof'],
                caption = msg_maker.staff_show_uncompleted_transfer_detail(transfer_detail),
                reply_markup = await changer_kb.staff_show_transfer_detail_none_next()

            )
            await state.update_data(mainMsg = mainMsg)

        elif transfer_detail['userProofType'] == 'document':

            mainMsg = bot.send_document(

                call.from_user.id,
                document = transfer_detail['userProof'],
                caption = msg_maker.staff_show_uncompleted_transfer_detail(transfer_detail),
                reply_markup = await changer_kb.staff_show_transfer_detail_none_next()

            )
            await state.update_data(mainMsg = mainMsg)

        await state.set_state(FSMSteps.STAFF_TRANSFERS_PROOF)

    elif callback_data.action == 'staff_transfer_claims':

        ...


    elif callback_data.action == 'staff_transfer_accepted':

        ...



async def staff_transfer_proof_getter(message: Message, state: FSMContext):
    '''
    '''
    await message.delete()
    data = state.get_data()
    mainMsg = data.get('mainMsg')
    transfer_id = data.get('ansvered_transfer_id')

    if message.photo:

        fileId = message.photo[-1].file_id
        proofType = 'photo'

    elif message.document:

        fileId = message.document.file_id
        proofType = 'document'

    await mainMsg.edit_reply_markup(
        reply_markup = staff_show_transfer_detail(transfer_id)
    )
    await message.answer(msg.staff_get_proof_success)
    await state.set_state(FSMSteps.STAFF_TRANSFERS_PROOF)

    








async def accept_or_decline_user_transfer(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: UserProofActions):
    '''
    '''
    response = await SimpleAPI.getDetails(
        r.changerRoutes.transactions,
        callback_data.transferId
    )
    transfer = response.json()
    await state.update_data(transfer = transfer)

    if callback_data.action == 'accept':

        tmpMessage = await bot.send_message(
            transfer['user'],
            text= await msg_maker.accept_user_transfer2()
        )
        await state.update_data(tmpMessage = tmpMessage)
        await bot.send_message(
            call.from_user.id,
            text= await msg_maker.accept_changer_transfer(transfer),
        )

        patchData = {
            'changerAcceptDate': datetime.now()
        }
        await SimpleAPI.patch(
            r.changerRoutes.transactions,
            transfer['id'],
            data=patchData
        )
        await state.set_state(FSMSteps.GET_CHANGER_PROOF)

    elif callback_data.action == 'decline':
        
        await bot.send_message(
            transfer['user'],
            text= await msg_maker.decline_user_transfer()

        )


    elif callback_data.action == 'admin':
        await bot.send_message(
            call.from_user.id,
            text= await msg_maker.contact_to_admin()
        )


async def get_changer_proof(message: Message, state: FSMContext):
    '''
    '''

    allData = await state.get_data()
    transferId = allData['transfer']['id']
    userId = allData['transfer']['user']
    buyAmount = allData['transfer']['buyAmount']
    tmpMessage = allData['tmpMessage']
    await message.delete()


    if message.photo:

        fileId = message.photo[-1].file_id
        proofType = 'photo'

    elif message.document:

        fileId = message.document.file_id
        proofType = 'document'

    data = {
        'changerSendMoneyDate': datetime.now(),
        'changerProofType': proofType,
        'changerProof': fileId,
    }

    response = await SimpleAPI.patch(
        r.changerRoutes.transactions,
        transferId,
        data=data
    )

    if proofType == 'photo':

        await tmpMessage.delete()
        await bot.send_photo(
            userId,
            photo = fileId,
            caption= await msg_maker.accept_changer_proof(transferId),
            reply_markup= await user_kb.accept_changer_transfer(response.json()['id'])
        )

    if proofType == 'document':

        await bot.send_document(
            userId, 
            document= fileId,
            caption= await msg_maker.accept_changer_proof(),
            reply_markup= await user_kb.accept_changer_transfer(response.json()['id'])
        )

    await bot.send_message(
        message.from_user.id,
        text= await msg_maker.changer_inform2(transferId)
        )
    await state.set_state(FSMSteps.STUFF_INIT_STATE)









async def register_message_handlers_changer():
    '''Registry message handlers there.
    '''
    dp.message.register(

        get_changer_proof,
        FSMSteps.GET_CHANGER_PROOF        
    
    )
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
    dp.message.register(

        staff_edit_offer_values_checker,
        FSMSteps.STAFF_EDIT_VALUES,
        F.text

    )
    dp.message.register(

        staff_transfer_proof_getter,
        FSMSteps.STAFF_TRANSFERS_PROOF,
        F.content_type.in_({'photo', 'document'})

    )



async def register_callback_handler_changer():
    '''Register callback_querry handlers there.
    '''

    dp.callback_query.register(

        offer_menu,
        StuffOfficeData.filter(F.action == 'offers'),
    
    )
    dp.callback_query.register(
        
        offer_menu_give_result,
        StuffOfficeData.filter(
        
            F.action.in_({
                'create_new',
                'edit_offers',
                'inactive'
            })
        )
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
    dp.callback_query.register(

        staff_edit_offer,
        StuffEditData.filter(
        
            F.action == 'staff_edit_offer'
        )
    )
    dp.callback_query.register(

        staff_edit_offer_steps,
        StuffEditData.filter(
            
            F.action.in_({
                'staff_edit_offer_name',
                'staff_edit_offer_rate',
                'staff_edit_offer_min_amount',
                'staff_edit_offer_max_amount',
            })
        )

    )
    dp.callback_query.register(

        staff_edit_offer_values_setter,
        StuffEditData.filter(
            
            F.action.in_({
                'staff_edit_accept',
                'staff_delete_offer',
                'staff_publish_offer',
                'staff_unpublish_offer',
                'staff_edit_banks_inactive',
                'staff_edit_banks_delete',
            })
        )
    )
    dp.callback_query.register(

        staff_edit_offer_banks,
        StuffEditData.filter(
            
            F.action.in_({
                'staff_edit_offer_banks',
                'staff_edit_offer_banks_set',
                'staff_edit_offer_banks_patch',
            })
        )
    )
    dp.callback_query.register(

        staff_show_banks_account,
        StuffOfficeData.filter(
            
            F.action == 'staff_show_accounts'
        )
    )
    dp.callback_query.register(

        staff_show_transfers,
        StuffOfficeData.filter(
            
            F.action == 'staff_show_transfers'
        )
    )
    dp.callback_query.register(

        staff_show_transfer_detail,
        StuffEditData.filter(
        
            F.action == 'staff_transfers_get_detail'
        )
    )

    dp.callback_query.register(
        accept_or_decline_user_transfer,
        UserProofActions.filter(),
        FSMSteps.STUFF_INIT_STATE
    )

