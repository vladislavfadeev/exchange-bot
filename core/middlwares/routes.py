from dataclasses import dataclass


@dataclass
class HomeRoutes:
    '''Dataclass include routes for "home" handlers.
    '''
    userInit: str


@dataclass
class UserRoutes:
    '''Routes fot "user" handlers.
    '''
    offer: str
    changerBanks: str
    userBanks: str
    banksNameList: str
    transactions : str


@dataclass
class ChangerRoutes:
    '''Routes for "changer" handlers.
    '''
    changerProfile: str
    transactions: str
    banksCheker: str
    myOffers: str
    banks: str
    

@dataclass
class KeysRoutes:
    '''Routes for all keyboard making functions.
    '''
    currencyList: str


@dataclass
class Routes:
    
    homeRoutes: HomeRoutes
    userRoutes: UserRoutes
    changerRoutes: ChangerRoutes
    keysRoutes: KeysRoutes


def get_routes():

    return Routes(
        homeRoutes = HomeRoutes(
            userInit='/api/v1/user',

        ),
        userRoutes = UserRoutes(
            offer='/api/v1/offer',
            changerBanks='api/v1/changer_banks',
            userBanks='api/v1/user_banks',
            banksNameList='api/v1/banks_name_list',
            transactions='/api/v1/transactions'
        ),
        changerRoutes = ChangerRoutes(
            changerProfile='api/v1/changer_profile',
            transactions='/api/v1/transactions',
            banksCheker='/api/v1/changer_banks/checker',
            myOffers='/api/v1/offer',
            banks='/api/v1/changer_banks',
        ),
        keysRoutes = KeysRoutes(
            currencyList='/api/v1/currency',
        )
    )


r = get_routes()