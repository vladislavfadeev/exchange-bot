from aiogram.fsm.state import StatesGroup, State


class FSMSteps(StatesGroup):
    INIT_STATE = State()
    INIT_CHANGE_STATE = State()
