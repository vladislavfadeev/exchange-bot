from core.middlwares.settigns import appSettings
import httpx


headers = {
    "Authorization": appSettings.apiSettings.authToken
}
client = httpx.AsyncClient(
    base_url=appSettings.apiSettings.baseUrl,
    headers=headers
)


class SimpleAPI():

    async def get(path, params=None):
        
        response = await client.get(path, params=params)
        return response


    async def getDetails(path, detailUrl, params=None):

        response = await client.get(
            f'{path}/{detailUrl}',
            params=params
        )
        return response


    async def post(path, data):
        response = await client.post(
            path,
            data=data
        )
        return response
    
    
    async def patch(path, detailUrl, data):
        response = await client.patch(
            f'{path}/{detailUrl}',
            data=data
        )
        return response











        # async with aiohttp.ClientSession('http://127.0.0.1:8000/', headers=headers) as session:
        #     async with session.patch('/api/v1/user/12221') as response:

        #         print("Status:", response.status)
        #         print("Content-type:", response.headers['content-type'])

        #         html = await response.text()
        #         print("Body:", html)





    
#     async def get(route, data=None):

#         async with session.get(route) as response:
#             return await response.json()
        

#     async def post(route, data):

#         async with session.post(route, data=data) as response:
#             return await response.json()
        

#     async def patch(route, data):

#         async with session.patch(route, data=data) as response:
#             return await response.json()


# async def post(route, data):

#     async with session.post(route, data=data) as response:
#         return await response.json()


# async def insert_user_todb(post_data):
#     async with session.get(f'/api/v1/customer/{post_data["tg_id"]}') as resp:
#         print(resp.status)
#         if resp.status == 200:
#             pass
#         else:
#             async with session.post('/api/v1/customer', data=post_data) as response:
#                 print(response.status)


# async def insert_request_todb(post_data):
#     async with session.post('/api/v1/request', data=post_data) as response:
#         return await response.json()
#         # print(response.status, await response.text())


# async def get_changers_list():
#     async with session.get('/api/v1/changers-list') as response:
#         return await response.json()
    

# async def insert_response_todb(post_data):
#     async with session.post('/api/v1/response', data=post_data) as response:
#         return await response.json()
        

# async def insert_user_choise_todb(post_data):
#     async with session.post('/api/v1/customer-choice', data=post_data) as response:
#         return await response.json()
    