from aiogram.fsm.state import StatesGroup, State


class FSMSteps(StatesGroup):
    USER_INIT_STATE = State()
    INIT_CHANGE_STATE = State()
    SET_AMOUNT_STATE = State()
    SET_SELL_BANK = State()
    SET_BUY_BANK_INIT = State()
    SET_BUY_BANK_ACCOUNT = State()
    GET_USER_PROOF = State()
    WAIT_CHANGER_PROOF = State()
    GET_CHANGER_PROOF = State()
    CHANGER_INIT_STATE = State()


