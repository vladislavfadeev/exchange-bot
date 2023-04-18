from sys import prefix
from aiogram.filters.callback_data import CallbackData


class HomeData(CallbackData, prefix='home'):
    action: str


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


class UserProofActions(CallbackData, prefix='upa'):
    action: str
    transferId: int


class ChangerProofActions(CallbackData, prefix='cpa'):
    action: str
    transferId: int


class TestData(CallbackData, prefix='test'):
    url: str


class StuffOfficeData(CallbackData, prefix='office'):
    action: str


class StuffEditData(CallbackData, prefix='stuff_edit'):
    id: int
    action: str
    value: str