from aiogram.filters.callback_data import CallbackData


class UserHomeData(CallbackData, prefix="user_home"):
    action: str
    id: int


class UserExchangeData(CallbackData, prefix="user_ch"):
    id: int
    action: str
    name: str
    is_returned: bool


class StaffOfficeData(CallbackData, prefix="staff_office"):
    action: str


class StaffEditData(CallbackData, prefix="staff_edit"):
    id: int
    action: str
    value: str


class URLData(CallbackData, prefix="url"):
    ...
