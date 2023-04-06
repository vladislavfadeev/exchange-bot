from aiogram.fsm.state import StatesGroup, State


class FSMSteps(StatesGroup):
    INIT_STATE = State()
    INIT_CHANGE_STATE = State()
    SET_AMOUNT_STATE = State()
