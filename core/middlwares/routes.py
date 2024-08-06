from dataclasses import dataclass


@dataclass
class HomeRoutes:
    """Dataclass include routes for "home" handlers."""

    userInit: str
    rate: str


@dataclass
class UserRoutes:
    """Routes fot "user" handlers."""

    offer: str
    changerBanks: str
    userBanks: str
    banksNameList: str
    transactions: str
    crypto_orders: str


@dataclass
class ChangerRoutes:
    """Routes for "changer" handlers."""

    changerProfile: str
    changerIdList: str
    transactions: str
    banksCheker: str
    myOffers: str
    banks: str


@dataclass
class KeysRoutes:
    """Routes for all keyboard making functions."""

    currencyList: str
    cr_currency_list: str


@dataclass
class Routes:
    homeRoutes: HomeRoutes
    userRoutes: UserRoutes
    changerRoutes: ChangerRoutes
    keysRoutes: KeysRoutes


def get_routes():
    return Routes(
        homeRoutes=HomeRoutes(
            userInit="/api/v1/user",
            rate="/api/v1/get_rate"
        ),
        userRoutes=UserRoutes(
            offer="/api/v1/offer",
            changerBanks="api/v1/changer_banks",
            userBanks="api/v1/user_banks",
            banksNameList="api/v1/banks_name_list",
            transactions="/api/v1/transactions",
            crypto_orders="/api/v1/crypto_orders"
        ),
        changerRoutes=ChangerRoutes(
            changerProfile="api/v1/changer_profile",
            changerIdList="api/v1/changer_profile/id_list",
            transactions="/api/v1/transactions",
            banksCheker="/api/v1/changer_banks/checker",
            myOffers="/api/v1/offer",
            banks="/api/v1/changer_banks",
        ),
        keysRoutes=KeysRoutes(
            currencyList="/api/v1/currency",
            cr_currency_list="/api/v1/crypto_rate",
        ),
    )


r = get_routes()
