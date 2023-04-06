from locale import currency
from sys import prefix
from aiogram.filters.callback_data import CallbackData


class CurrencyData(CallbackData, prefix='curr'):
    id: int
    name: str
    isReturned: bool


class OfferData(CallbackData, prefix='off_d'):
    id: int
