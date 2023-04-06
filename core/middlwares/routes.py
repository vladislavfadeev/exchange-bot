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


@dataclass
class ChangerRoutes:
    '''Routes for "changer" handlers.
    '''
    ...


@dataclass
class KeysRoutes:
    '''Routes for all keyboard making functions.
    '''
    currencyList: str


@dataclass
class Routes:
    
    homeRoutes: HomeRoutes
    userRoutes: UserRoutes
    # changerRoutes: ChangerRoutes
    keysRoutes: KeysRoutes


def get_routes():

    return Routes(
        homeRoutes = HomeRoutes(
            userInit='/api/v1/user',

        ),
        userRoutes = UserRoutes(
            offer='/api/v1/offer'
        ),
        # changerRoutes = ChangerRoutes(
        #     ...
        # ),
        keysRoutes = KeysRoutes(
            currencyList='/api/v1/currency',
        )
    )


r = get_routes()