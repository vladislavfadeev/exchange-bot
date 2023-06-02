import logging
import traceback
from types import NoneType
from httpx import AsyncClient, Response
from aiogram import Bot, Dispatcher
from core.middlwares.exceptions import ResponseError
from core.middlwares.settigns import appSettings



class SimpleAPI():

    def __init__(self, bot: Bot, dp: Dispatcher):
        self.bot = bot
        self.dp = dp
        self.client = AsyncClient(
            base_url=appSettings.apiSettings.baseUrl,
            headers= {
                "Authorization": appSettings.apiSettings.authToken
            }
        )
    
    def responce_processor(func):
        async def wrapper(self, *args, **kwargs):
            bot: Bot = self.bot
            exp_code: list | NoneType = kwargs.get('exp_code')
            response: Response | NoneType = None
            method: str | NoneType = None
            try:
                response, method = await func(self, **kwargs)
                if exp_code:
                    if response.status_code not in exp_code:
                        raise ResponseError
                    
            except Exception as e:

                post_data: dict | NoneType = kwargs.get('data')
                params: dict | NoneType = kwargs.get('params')
                path: str = kwargs.get('path')
                detailUrl: str | NoneType = kwargs.get('detailUrl')
                det: str = f'/{detailUrl}' if detailUrl else ''
                exception: bool = True
                try:
                    response_data: dict | NoneType = response.json()
                    code: int = response.status_code
                except:
                    response_data : NoneType = None
                    code: NoneType = None

                logging.exception(
                    f'method: {method}\n'
                    f'exp_code: {exp_code} | code: {code}\n'
                    f'get params:\n{params}\n\n'
                    f'post | patch data:\n{post_data}\n\n'
                    f'endpoint: {path}{det}\n\n'
                    f'response: \n{response_data}\n'
                    f'{e}\n'
                )
                await bot.send_message(
                    appSettings.botSetting.devStaffId,
                    text=(
                        'SimpleAPI raise exception!\n\n'
                        f'method: {method}\n'
                        f'exp_code: {exp_code} | code: {code}\n'
                        f'get params:\n{params}\n\n'
                        f'post/patch data:\n{post_data}\n\n'
                        f'endpoint: {path}{det}\n\n'
                        f'response: \n{response_data}\n'
                        f'{traceback.format_exc(limit=1)}\n'
                    )
                )
            else:
                exception: bool = False
                code: int = response.status_code
                response_data: dict = response.json()
            data = {
                'exception': exception,
                'status_code': code,
                'response': response_data,
            }
            return data
        return wrapper


    @responce_processor
    async def get(self, **kwargs):
        method='GET'
        path: str = kwargs.get('path')
        params: dict = kwargs.get('params')

        response: Response = await self.client.get(
            path,
            params=params
        )
        return response, method

    @responce_processor
    async def get_detail(self, **kwargs):
        method='GET_DETAIL'
        path: str = kwargs.get('path')
        detailUrl: str = kwargs.get('detailUrl')
        params: dict = kwargs.get('params')

        response: Response = await self.client.get(
            f'{path}/{detailUrl}',
            params=params
        )
        return response, method

    @responce_processor
    async def post(self, **kwargs):
        method='POST'
        path: str = kwargs.get('path')
        data: dict = kwargs.get('data')
        response: Response = await self.client.post(
            path,
            data=data
        )
        return response, method
    
    @responce_processor
    async def patch(self, **kwargs):
        method='PATCH'
        path: str = kwargs.get('path')
        detailUrl: str = kwargs.get('detailUrl')
        data: dict = kwargs.get('data')

        response: Response = await self.client.patch(
            f'{path}/{detailUrl}',
            data=data
        )
        return response, method