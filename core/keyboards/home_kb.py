from asyncio import events
from aiogram.types import KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from core.keyboards.callbackdata import HomeData, UserProofActions
from create_bot import dp, bot



async def state_getter(id: int):
    '''
    '''
    state: FSMContext = FSMContext(
        bot=bot,
        storage=dp.storage,
        key=StorageKey(
            chat_id=id,
            user_id=id,  
            bot_id=bot.id
        )
    )
    state_dict: dict = await state.get_data()
    return state_dict



async def user_home_inline_button(id):
    '''Build InlineKeyboardButton for "/start" function.
    '''
    data: dict = await state_getter(id)
    events: list = data.get('user_events')
    value: str = f'({len(events)})' if events else ''

    builder = InlineKeyboardBuilder()

    action = {
        'info': 'Справка',
        'time': 'Режим работы',
        'change': 'Обменять валюту',
    }

    for i in action.keys():
        builder.button(
            text=action[i],
            callback_data=HomeData(
                action=i
            )
        )

    builder.button(
        text = f'Мои события {value}',
        callback_data = UserProofActions(
            action = 'user_new_events',
            transferId=0
        )
    )
    builder.adjust(2, 1, 1)

    return builder.as_markup()

async def user_back_home_inline_button():
    '''
    '''
    builder = InlineKeyboardBuilder()

    builder.button(
        text='↩ Вернуться на главную',
        callback_data=HomeData(
            action='cancel'
        )
    )

    return builder.as_markup()