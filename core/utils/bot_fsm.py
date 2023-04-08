from aiogram.fsm.state import StatesGroup, State


class FSMSteps(StatesGroup):
    INIT_STATE = State()
    INIT_CHANGE_STATE = State()
    SET_AMOUNT_STATE = State()
    SET_SELL_BANK = State()
    SET_BUY_BANK_INIT = State()
