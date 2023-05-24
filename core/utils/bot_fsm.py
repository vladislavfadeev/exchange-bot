from aiogram.fsm.state import StatesGroup, State


class FSMSteps(StatesGroup):

    USER_INIT_STATE = State()
    USER_ENTER_BANK_NAME = State()
    INIT_CHANGE_STATE = State()
    SET_AMOUNT_STATE = State()
    SET_SELL_BANK = State()
    SET_BUY_BANK_INIT = State()
    SET_BUY_BANK_ACCOUNT = State()
    GET_USER_PROOF = State()
    WAIT_CHANGER_PROOF = State()
    GET_CHANGER_PROOF = State()


    STAFF_HOME_STATE = State()
    STUFF_INIT_STATE = State()
    STUFF_ACCOUNTS = State()
    STAFF_TRANSFRES = State()
    STUFF_OFFERS_MENU = State()
    STUFF_OFFERS_RATE = State()
    STAFF_OFFERS_MINAMOUNT = State()
    STAFF_OFFERS_MAXAMOUNT = State()
    STAFF_OFFERS_SETNAME = State()
    STAFF_EDIT_VALUES = State()
    STAFF_TRANSFERS_PROOF = State()
    STAFF_WAITER = State()

