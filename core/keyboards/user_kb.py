from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from core.api_actions.bot_api import SimpleAPI
from core.middlwares.routes import r    # Dataclass whith all api routes
from core.middlwares.settigns import appSettings
from core.keyboards.callbackdata import (
    AmountData,
    CurrencyData,
    HomeData,
    OfferData,
    ChangerProofActions,
    SetBuyBankData,
    SetSellBankData,
    StuffEditData,
    StuffOfficeData,
    TestData,
)


async def set_sell_currency_button():
    '''Build InlineKeyboardButton with currency for "start_change" handler.
    '''
    currency = await SimpleAPI.get(r.keysRoutes.currencyList)
    builder = InlineKeyboardBuilder()

    for curr in currency.json():
        
        if curr['name'] == 'MNT':
            pass

        else:
            builder.button(
                text=curr["name"],
                callback_data=CurrencyData(
                    id=curr['id'],
                    name=curr['name'],
                    isReturned=False
                )
            )
    builder.button(
        text='↩ Отменить',
        callback_data= HomeData(
            action='cancel'
        )
    )
    builder.adjust(2, 1)

    return builder.as_markup()


async def user_cancel_buttons_offerslist():
    '''Build RelyKeyboardButton for cancel all process and retun to INIT_STATE.
    '''
    builder = InlineKeyboardBuilder()
    builder.button(
        text='↩ Вернуться к выбору валюты',
        callback_data=HomeData(
            action='change'
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


async def set_amount_check_inlkb():
    '''
    '''
    builder = InlineKeyboardBuilder()
    builder.button(
        text='⤵️ Согласен, продолжить',
        callback_data=AmountData(
            action='next'
        )
    )
    builder.button(
        text='⤴️ Вернуться, ввести другую сумму',
        callback_data=OfferData(
            id=0,
            isReturned=True
        )
    )
    builder.adjust(1)

    return builder.as_markup()
    

async def set_sell_bank(banks):

    builder = InlineKeyboardBuilder()

    for bank in banks.json():
        builder.button(
            text=bank['name'],
            callback_data=SetSellBankData(
                id=bank['id'],
                setNew=False
            )
        )
    builder.adjust(1)

    return builder.as_markup()


async def choose_user_bank_from_db(banks):

    builder = InlineKeyboardBuilder()
    builder.button(
        text=f'💰 Указать новый счет',
        callback_data=SetSellBankData(
            id=0,
            setNew = True 
        )
    )

    for bank in banks.json():
        builder.button(
            text=f'🏦 {bank["name"]}\n💳 {bank["bankAccount"]}',
            callback_data=SetBuyBankData(
                id=bank['id'],
                setNew = False,
                bankName=''
            )
        )
    builder.adjust(1)

    return builder.as_markup()


async def choose_bank_name_from_list(banksName):

    builder = InlineKeyboardBuilder()

    for bank in banksName.json():
        builder.button(
            text=f'{bank["name"]}',
            callback_data=SetBuyBankData(
                id=0,
                setNew=True,
                bankName=bank['name']
            )
        )
    builder.adjust(3)

    return builder.as_markup()


async def accept_changer_transfer(transfer_id):
    '''
    '''
    builder = InlineKeyboardBuilder()
    actions = {
        'accept': '🤝 Подтвердить получение',
        'decline': '👎 Перевод не получил',
        'admin': '⚠️ Связаться с админом'
    
    }

    for action in actions.keys():
        builder.button(
            text=actions[action],
            callback_data=ChangerProofActions(
                action= action,
                transferId=transfer_id
            )
        )
    builder.adjust(1)

    return builder.as_markup()


async def get_trouble_staff_contact():

    contact = appSettings.botSetting.troubleStaffId
    builder = InlineKeyboardBuilder()

    builder.button(
        text='👮🏻 Связаться с админом',
        url= f'tg://user?id={contact}',
        callback_data=TestData(
            url= ''
        )
    )

    return builder.as_markup()

