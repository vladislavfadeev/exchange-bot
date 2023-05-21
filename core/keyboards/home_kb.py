from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from core.keyboards.callbackdata import UserHomeData



async def user_home_inline_button(id: int, state: FSMContext):
    '''Build InlineKeyboardButton for "/start" function.
    '''
    data: dict = await state.get_data()
    events: list = data.get('user_events')
    value: str = f'({len(events)})' if events else ''

    builder = InlineKeyboardBuilder()

    action = {
        'info': 'Справка',
        'time': 'Режим работы',
        'change': 'Обменять валюту',
        'user_new_events': f'Мои сообщения {value}',
    }

    for i in action.keys():
        builder.button(
            text=action[i],
            callback_data=UserHomeData(
                action=i,
                id=0
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
        callback_data=UserHomeData(
            action='cancel',
            id=0
        )
    )

    return builder.as_markup()