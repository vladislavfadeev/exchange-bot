from aiogram.filters.callback_data import CallbackData


class CurrencyData(CallbackData, prefix='curr'):
    id: int
    name: str
    isReturned: bool


class OfferData(CallbackData, prefix='off_d'):
    id: int
    isReturned: bool


class AmountData(CallbackData, prefix='am_d'):
    action: str


class SetSellBankData(CallbackData, prefix='sell_bd'):
    id: int
    setNew: bool


class SetBuyBankData(CallbackData, prefix='buy_bd'):
    id: int
    setNew: bool
    bankName: str