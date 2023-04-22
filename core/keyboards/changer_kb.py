from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from core.middlwares.settigns import appSettings
from core.api_actions.bot_api import SimpleAPI
from core.middlwares.routes import r    # Dataclass whith all api routes
from core.keyboards.callbackdata import (
    StuffEditData,
    StuffOfficeData,
    HomeData,
    TestData,
    UserProofActions,
)



async def staff_welcome_button(transfers):

    value = len(transfers) if transfers else None
    button_text = f'💰 Входящие переводы ({value})' if value else '💰 Входящие переводы'

    builder = InlineKeyboardBuilder()
    actions = {
        'offers': '📊 Мои предложения',
        'staff_show_accounts': '💳 Мои счета',
        'staff_show_transfers': button_text
    }
    for action in actions.keys():
        builder.button(
            text=actions[action],
            callback_data=StuffOfficeData(
                action=action
            )
        )
    builder.adjust(2)

    return builder.as_markup()


async def stuff_offer_menu_buttons():

    builder = InlineKeyboardBuilder()
    actions = {
        'create_new': '📝 Создать новое',
        'edit_offers': '⚙️ Активные',
        'inactive': '🗄 Не активные'
    }
    for action in actions.keys():
        builder.button(
            text=actions[action],
            callback_data=StuffOfficeData(
                action=action
            )
        )
    builder.button(
        text='↩ Вернуться на главную',
        callback_data= HomeData(
            action='cancel'
        )
    )
    builder.adjust(2, 1)

    return builder.as_markup()



async def stuff_edit_offer_list_buttons(offer_id):

    builder = InlineKeyboardBuilder()
    actions = {
        'staff_edit_offer': '⚙️ Редактировать',
        'staff_delete_offer': '🗑️ Удалить',
        'staff_unpublish_offer': '🗄 Убрать с публикации'
        
    }

    for action in actions.keys():

        builder.button(
            text= actions[action],
            callback_data=StuffEditData(
                id= offer_id,
                action= action,
                value= ''
            )
        )

    builder.adjust(2, 1)

    return builder.as_markup()



async def stuff_edit_inactive_offers_buttons(offer_id):

    builder = InlineKeyboardBuilder()
    actions = {
        'staff_edit_offer': '⚙️ Редактировать',
        'staff_delete_offer': '🗑️ Удалить из архива',
        'staff_publish_offer': '📢 Опубликовать'
    }

    for action in actions.keys():

        builder.button(
            text= actions[action],
            callback_data=StuffEditData(
                id= offer_id,
                action= action,
                value= ''
            )
        )

    builder.adjust(2, 1)

    return builder.as_markup()


async def sfuff_cancel_button():
    '''.
    '''
    builder = InlineKeyboardBuilder()
    builder.button(
        text='↩ Вернуться на главную',
        callback_data=HomeData(
            action='cancel'
        )
    )
    builder.adjust(1)

    return builder.as_markup() 


async def set_sell_currency_button():
    '''
    '''
    currency = await SimpleAPI.get(r.keysRoutes.currencyList)
    builder = InlineKeyboardBuilder()

    for curr in currency.json():
        builder.button(
            text=curr["name"],
            callback_data=StuffEditData(
                id=curr['id'],
                value=curr['name'],
                action='new_offer_currency'
            )
        )
    builder.button(
        text='↩ Отменить',
        callback_data= HomeData(
            action='cancel'
        )
    )
    builder.adjust(3)

    return builder.as_markup()


async def staff_accept_new_rate():
    '''
    '''
    builder = InlineKeyboardBuilder()
    builder.button(
        text='⤵️ Согласен, продолжить',
        callback_data=StuffEditData(
            id=0,
            action='create_new_offer_banks',
            value=''
        )
    )
    builder.button(
        text='⤴️ Вернуться, ввести другую сумму',
        callback_data=StuffEditData(
            id=0,
            action='new_offer_currency_returned',
            value=''
        )
    )
    builder.adjust(1)
    return builder.as_markup()


async def stuff_create_new_offer_banks_dis_next(banks):

    builder = InlineKeyboardBuilder()

    for bank in banks:

        currency = bank['currency']['name']

        builder.button(
            text = f"💳 {bank.get('name')} - ({currency})\n{bank.get('bankAccount')}",
            callback_data=StuffEditData(
                id=bank.get('id'),
                action='staff_set_banks',
                value=''
            )
        )
    builder.button(
        text='↩ Вернуться на главную',
        callback_data=HomeData(
            action='cancel'
        )
    )
    builder.adjust(1)

    return builder.as_markup()



async def stuff_create_new_offer_banks(banks):

    builder = InlineKeyboardBuilder()

    for bank in banks:
        currency = bank['currency']['name']

        builder.button(
            text = f"💳 {bank.get('name')} - ({currency})\n{bank.get('bankAccount')}",
            callback_data=StuffEditData(
                id=bank.get('id'),
                action='staff_set_banks',
                value=''
            )
        )
    builder.button(
        text='👌 Продолжить',
        callback_data=StuffEditData(
            id=bank.get('id'),
            action='staff_will_set_amount',
            value=''
        )
    )
    builder.button(
        text='↩ Вернуться на главную',
        callback_data=HomeData(
            action='cancel'
        )
    )
    builder.adjust(1)

    return builder.as_markup()


async def staff_zero_banks_buttons():

    contact = appSettings.botSetting.troubleStaffId
    builder = InlineKeyboardBuilder()

    builder.button(
        text='👮🏻 Связаться с админом',
        url= f'tg://user?id={contact}',
        callback_data=TestData(
            url= ''
        )
    )
    builder.button(
        text='↩ Вернуться на главную',
        callback_data= HomeData(
            action='cancel'
        )
    )
    builder.adjust(1)

    return builder.as_markup()
    

async def staff_will_set_amount_kb():

    builder = InlineKeyboardBuilder()
    builder.button(
        text='👉 Указать',
        callback_data=StuffEditData(
            id=0,
            action='set_min&max_amount',
            value=''
        )
    )
    builder.button(
        text='⤵️ Пропустить',
        callback_data=StuffEditData(
            id=0,
            action='staff_new_offer_name',
            value=''
        )
    )    
    builder.button(
        text='↩ Вернуться на главную',
        callback_data= HomeData(
            action='cancel'
        )
    )
    builder.adjust(2, 1)

    return builder.as_markup()


async def staff_set_min_amount():
    '''.
    '''
    builder = InlineKeyboardBuilder()
    builder.button(
        text='⤵️ Пропустить шаг',
        callback_data=StuffEditData(
            id=0,
            action='staff_pass_min_amount',
            value=''
        )
    )
    builder.button(
        text='↩ Вернуться на главную',
        callback_data=HomeData(
            action='cancel'
        )
    )
    builder.adjust(1)

    return builder.as_markup() 


async def staff_accept_min_amount():
    '''
    '''
    builder = InlineKeyboardBuilder()
    builder.button(
        text='⤵️ Согласен, продолжить',
        callback_data=StuffEditData(
            id=0,
            action='staff_set_max_amount',
            value=''
        )
    )
    builder.button(
        text='⤴️ Вернуться, ввести другую сумму',
        callback_data=StuffEditData(
            id=0,
            action='set_min&max_amount',
            value=''
        )
    )
    builder.adjust(1)

    return builder.as_markup()


async def staff_set_max_amount():
    '''.
    '''
    builder = InlineKeyboardBuilder()
    builder.button(
        text='⤵️ Пропустить шаг',
        callback_data=StuffEditData(
            id=0,
            action='staff_pass_max_amount',
            value=''
        )
    )
    builder.button(
        text='↩ Вернуться на главную',
        callback_data=HomeData(
            action='cancel'
        )
    )
    builder.adjust(1)

    return builder.as_markup() 


async def staff_accept_max_amount():
    '''
    '''
    builder = InlineKeyboardBuilder()
    builder.button(
        text='⤵️ Согласен, продолжить',
        callback_data=StuffEditData(
            id=0,
            action='staff_new_offer_name',
            value=''
        )
    )
    builder.button(
        text='⤴️ Вернуться, ввести другую сумму',
        callback_data=StuffEditData(
            id=0,
            action='staff_set_max_amount',
            value=''
        )
    )
    builder.adjust(1)

    return builder.as_markup()


async def staff_will_set_name():
    '''
    '''
    builder = InlineKeyboardBuilder()
    builder.button(
        text='👍 Да',
        callback_data=StuffEditData(
            id=0,
            action='staff_set_offer_name',
            value=''
        )
    )
    builder.button(
        text='👎 Нет',
        callback_data=StuffEditData(
            id=0,
            action='staff_set_offer_final',
            value=''
        )
    )
    builder.button(
        text='↩ Вернуться на главную',
        callback_data=HomeData(
            action='cancel'
        )
    )
    builder.adjust(2, 1)

    return builder.as_markup()


async def staff_accept_offer_name():
    '''
    '''
    builder = InlineKeyboardBuilder()
    builder.button(
        text='👍 Продолжить',
        callback_data=StuffEditData(
            id=0,
            action='staff_set_offer_final',
            value=''
        )
    )
    builder.button(
        text='⤴️ Вернуться, ввести заново',
        callback_data=StuffEditData(
            id=0,
            action='staff_set_offer_name',
            value=''
        )
    )
    builder.button(
        text='↩ Вернуться на главную',
        callback_data=HomeData(
            action='cancel'
        )
    )
    builder.adjust(1)

    return builder.as_markup()


async def staff_create_offer_final_text_kb():

    builder = InlineKeyboardBuilder()
    builder.button(
        text = '👌 Опубликовать',
        callback_data=StuffEditData(
            id=0,
            action='staff_post_offer',
            value=''
        )
    )
    builder.button(
        text='⚠️ Сохранить без публикации',
        callback_data=StuffEditData(
            id=0,
            action='staff_post_offet_non_active',
            value=''
        )
    )
    builder.button(
        text='↩ Отклонить',
        callback_data=HomeData(
            action='cancel'
        )
    )
    builder.adjust(1)

    return builder.as_markup()


async def staff_create_new_offer_succes():

    builder = InlineKeyboardBuilder()
    builder.button(
        text='⚠️ Понятно, в главное меню',
        callback_data=HomeData(
            action='cancel'
        )
    )
    
    return builder.as_markup()


async def staff_edit_offer_show_kb(offer):

    builder = InlineKeyboardBuilder()
    actions = {
        'staff_edit_offer_name': '👉 Комментарий',
        'staff_edit_offer_rate': '👉 Курс обмена',
        'staff_edit_offer_banks': '👉 Банк',
        'staff_edit_offer_min_amount': '👉 Минимальная сумма обмена',
        'staff_edit_offer_max_amount': '👉 Максимальная сумма обмена',
    }

    for action, text in actions.items():

        builder.button(
            text=text,
            callback_data=StuffEditData(
                id=offer.get('id'),
                action=action,
                value=''
            )
        )
    builder.button(
        text='↩ Отмена, на главную',
        callback_data=HomeData(
            action='cancel'
        )
    )
    builder.adjust(1)

    return builder.as_markup()


async def staff_back_to_offer_menu():

    builder = InlineKeyboardBuilder()
    builder.button(
        text='↩ Отмена, вернуться в меню',
        callback_data=StuffOfficeData(
            action='offers'
        )
    )

    return builder.as_markup()


async def staff_edit_offer_values(decline):
    '''
    '''
    builder = InlineKeyboardBuilder()
    builder.button(
        text='👍 Продолжить',
        callback_data=StuffEditData(
            id=0,
            action='staff_edit_accept',
            value=''
        )
    )
    builder.button(
        text='⤴️ Вернуться, ввести заново',
        callback_data=StuffEditData(
            id=0,
            action=decline,
            value=''
        )
    )
    builder.button(
        text='↩ Вернуться на главную',
        callback_data=StuffOfficeData(
            action='offers'
        )
    )
    builder.adjust(1)

    return builder.as_markup()


async def staff_edit_offer_succes_kb():

    builder = InlineKeyboardBuilder()
    builder.button(
        text='👍 Понятно, в меню',
        callback_data=StuffOfficeData(
            action='offers'
        )
    )

    return builder.as_markup()



async def stuff_edit_offer_banks_dis_next(banks):

    builder = InlineKeyboardBuilder()

    for bank in banks:
        currency = bank['currency']['name']

        builder.button(
            text = f"💳 {bank.get('name')} - ({currency})\n{bank.get('bankAccount')}",
            callback_data=StuffEditData(
                id=bank.get('id'),
                action='staff_edit_offer_banks_set',
                value=''
            )
        )
    builder.button(
        text='↩ Вернуться в меню',
        callback_data=StuffOfficeData(
            action='offers'
        )
    )
    builder.adjust(1)

    return builder.as_markup()


async def stuff_edit_offer_banks(banks):

    builder = InlineKeyboardBuilder()

    for bank in banks:
        currency = bank['currency']['name']

        builder.button(
            text = f"💳 {bank.get('name')} - ({currency})\n{bank.get('bankAccount')}",
            callback_data=StuffEditData(
                id=bank.get('id'),
                action='staff_edit_offer_banks_set',
                value=''
            )
        )
    builder.button(
        text='👍 Продолжить',
        callback_data=StuffEditData(
            id=0,
            action='staff_edit_offer_banks_patch',
            value=''
        )
    )
    builder.button(
        text='↩ Вернуться в меню',
        callback_data=StuffOfficeData(
            action='offers'
        )
    )
    builder.adjust(1)

    return builder.as_markup()


async def staff_edit_banks_accounts(account_id, isActive):

    builder = InlineKeyboardBuilder()

    if isActive:
        actions = {
            'staff_edit_banks_inactive': '🗄 Сделать не активным',
            'staff_edit_banks_delete': '🗑️ Удалить',
        }

        for action in actions.keys():

            builder.button(
                text= actions[action],
                callback_data=StuffEditData(
                    id= account_id,
                    action= action,
                    value= ''
                )
            )

    elif not isActive:
        actions = {
            'staff_edit_banks_active': '⚡ Сделать активным',
            'staff_edit_banks_delete': '🗑️ Удалить',
        }

        for action in actions.keys():

            builder.button(
                text= actions[action],
                callback_data=StuffEditData(
                    id= account_id,
                    action= action,
                    value= ''
                )
            )

    builder.adjust(1)
    return builder.as_markup()



async def staff_show_transfers(transfer_id):

    builder = InlineKeyboardBuilder()

    builder.button(
        text = '🤝 Ответить',
        callback_data=StuffEditData(
            id= transfer_id,
            action= 'staff_transfers_get_detail',
            value= ''
        )
    )

    builder.adjust(1)
    return builder.as_markup()



async def staff_show_transfer_detail_none_next(transfer_id):

    contact = appSettings.botSetting.troubleStaffId

    builder = InlineKeyboardBuilder()

    builder.button(
        text = '⚠️ Перевод не получил',
        callback_data=StuffEditData(
            id= transfer_id,
            action= 'staff_transfer_claims',
            value= ''
        )
    )

    builder.button(
        text='👮🏻 Связаться с админом',
        url= f'tg://user?id={contact}',
        callback_data=TestData(
            url= ''
        )
    )
    
    return builder.as_markup()


async def staff_show_transfer_detail(transfer_id):

    contact = appSettings.botSetting.troubleStaffId

    builder = InlineKeyboardBuilder()

    builder.button(
        text = '⚠️ Подтвердить',
        callback_data=StuffEditData(
            id= transfer_id,
            action= 'staff_transfer_accepted',
            value= ''
        )
    )

    builder.button(
        text='👮🏻 Связаться с админом',
        url= f'tg://user?id={contact}',
        callback_data=TestData(
            url= ''
        )
    )
    
    return builder.as_markup()