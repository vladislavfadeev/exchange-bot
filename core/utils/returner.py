from datetime import datetime, timedelta
from types import NoneType
import logging

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message
from aiogram import Bot, Dispatcher

from core.middlwares.routes import r    # Dataclass whith all api routes
from core.keyboards import changer_kb
from core.utils import msg_maker
from core.utils.bot_fsm import FSMSteps
from core.api_actions.bot_api import SimpleAPI



async def main_msg_returner(
        bot: Bot,
        dp: Dispatcher,
        api_gateway: SimpleAPI
    ):
    '''
    Function execute every 30 seconds. It compares 
    curren time and last action time of every user and
    if it more than 2 minutes - function reset current
    user state, messages an retunr him to main message
    for he can receive notification.
    '''
    # try to get all changers id from backend
    response: dict = await api_gateway.get(
            path=r.changerRoutes.changerIdList,
            exp_code=[200]
        )
    exception: bool = response.get('exception')
    # if something went wrong we notify
    # tech staff and logging this exception
    if not exception:
        id_list: list = response.get('response')
        # get FSM State for current user from list_id
        for changer in id_list:
            state: FSMContext = FSMContext(
                bot=bot,
                storage=dp.storage,
                key=StorageKey(
                    chat_id=changer,
                    user_id=changer,  
                    bot_id=bot.id
                )
            )
            data: dict = await state.get_data()
            mainMsg: Message = data.get('mainMsg')
            last_action: datetime | NoneType = data.get('last_action')
            message_list: list = data.get('messageList')
            transfers: dict = data.get('uncompleted_transfers')
            current_state: FSMSteps = await state.get_state()
            home_state: FSMSteps = FSMSteps.STAFF_HOME_STATE
            time: datetime = datetime.now()
            if last_action:
                time_delta: timedelta = time - last_action
            else:
                time_delta: timedelta = timedelta(seconds=1)
            # if user has not returned to main message by himself
            # we will do it for them 
            if current_state != home_state and \
                time_delta.total_seconds() >= 120:
                # if in user's chat has many messages
                if message_list:
                    for i in message_list:
                        i: Message
                        try:
                            await bot.delete_message(
                                i.chat.id,
                                i.message_id
                            )
                        except:
                            pass
                    await state.update_data(messageList = [])
                try:
                    await bot.delete_message(
                        mainMsg.chat.id,
                        mainMsg.message_id
                    )
                except:
                    pass
                # return user to main message
                mainMsg: Message = await bot.send_message(
                    changer,
                    text = await msg_maker.staff_welcome(transfers),
                    reply_markup = await changer_kb.staff_welcome_button(
                        transfers
                    ),
                    disable_notification=True
                )
                # save new main message to FSM State
                await state.update_data(mainMsg = mainMsg)
                await state.set_state(home_state)