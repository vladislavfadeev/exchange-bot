from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from core.keyboards.callbackdata import StaffOfficeData, UserHomeData


async def user_home_inline_button(state: FSMContext):
    """Build InlineKeyboardButton for "/start" function."""
    data: dict = await state.get_data()
    events: list = data.get("user_events")
    uncompleted_transfers: list = data.get("uncompleted_transfers")
    value: str = f"({len(events)})" if events else ""

    builder = InlineKeyboardBuilder()
    if uncompleted_transfers:
        builder.button(
            text="Показать",
            callback_data=StaffOfficeData(action="changer_missed_events", id=0),
        )
    else:
        action = {
            "info": "📝 Справка",
            "support_us": "💰 Донат",
            "change": "💳 Обменять валюту",
            "user_new_events": f"✉ Мои сообщения {value}",
        }

        for i in action.keys():
            builder.button(text=action[i], callback_data=UserHomeData(action=i, id=0))
        builder.adjust(2, 1, 1)

    return builder.as_markup()


async def user_back_home_inline_button():
    """ """
    builder = InlineKeyboardBuilder()

    builder.button(
        text="↩ Вернуться на главную", callback_data=UserHomeData(action="cancel", id=0)
    )

    return builder.as_markup()
