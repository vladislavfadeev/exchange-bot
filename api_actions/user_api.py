from .sessions import session


class APISimpleMethods:
    
    async def api_get(route):
        async with session.get(route) as response:
            return await response.json()
        
    async def api_post(route, data):
        async with session.post(route, data=data) as response:
            return await response.json()
        
    async def api_patch(route, data):
        async with session.patch(route, data=data) as response:
            return await response.json()



async def insert_user_todb(post_data):
    async with session.get(f'/api/v1/customer/{post_data["tg_id"]}') as resp:
        print(resp.status)
        if resp.status == 200:
            pass
        else:
            async with session.post('/api/v1/customer', data=post_data) as response:
                print(response.status)


async def insert_request_todb(post_data):
    async with session.post('/api/v1/request', data=post_data) as response:
        return await response.json()
        # print(response.status, await response.text())


async def get_changers_list():
    async with session.get('/api/v1/changers-list') as response:
        return await response.json()
    

async def insert_response_todb(post_data):
    async with session.post('/api/v1/response', data=post_data) as response:
        return await response.json()
        

async def insert_user_choise_todb(post_data):
    async with session.post('/api/v1/customer-choice', data=post_data) as response:
        return await response.json()
    