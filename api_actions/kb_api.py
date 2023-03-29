from .sessions import session


async def get_curr_pair():
    async with session.get('/api/v1/curr-pair') as response:
            return await response.json()
            # res = [{i['id']: i['name']} for i in data]


async def get_bank_account(changer_id):
    async with session.get(
        f'/api/v1/changer-bank-account/{changer_id}') as response:
        return await response.json()