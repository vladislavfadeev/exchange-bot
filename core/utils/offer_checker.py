from core.api_actions.bot_api import SimpleAPI
from core.middlwares.routes import r    # Dataclass whith all api routes



async def offer_banks_checker(
        accounts_list,
        currency
):
    offer_disable_list = []

    params = {
        'banks_id': accounts_list
    }

    response = await SimpleAPI.post(
        r.changerRoutes.checkBanks,
        params=params
    )
    offer_list = response.json()

    for offer in offer_list:

        non_active_counter = 0
        currency_counter = 0

        for bank in offer['banks']:

            bank_currency = bank['currency']['name']

            if currency == bank_currency:

                currency_counter += 1

            if bank['isActive'] == False and currency == bank_currency:

                non_active_counter += 1

        if non_active_counter !=0 and currency_counter !=0:

            if non_active_counter == currency_counter:
                offer_disable_list.append(offer['id'])

    caution = {
        # account_id
    }

    return offer_disable_list

