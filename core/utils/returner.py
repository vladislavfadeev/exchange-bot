from datetime import datetime, timedelta
from types import NoneType
import logging

from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message
from aiogram import Bot, Dispatcher

from core.middlwares.routes import r    # Dataclass whith all api routes
from core.keyboards import changer_kb, user_kb
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



async def user_exchange_returner(
        bot: Bot,
        dp: Dispatcher,
        api_gateway: SimpleAPI
):
    '''
    '''
    response: dict = await api_gateway.get(
        path=r.homeRoutes.userInit,
        exp_code=[200]
    )
    exception: bool = response.get('exception')
    if not exception:
        user_list: list = response.get('response')
        for user in user_list:
            state: FSMContext = FSMContext(
                bot=bot,
                storage=dp.storage,
                key=StorageKey(
                    chat_id=user,
                    user_id=user,  
                    bot_id=bot.id
                )
            )
            data: dict = await state.get_data()
            current_state: FSMSteps = await state.get_state()
            claim_state: FSMSteps = FSMSteps.USER_TIME_EXPIRED
            claim_proof_state: FSMSteps = FSMSteps.USER_TIME_EXPIRED_PROOF
            is_staff: bool | NoneType = data.get('isStuff')
            if is_staff or current_state ==claim_state\
                or current_state == claim_proof_state:
                continue
            user_start_change_time = data.get('user_start_change_time')
            user_start_change_time: datetime | NoneType
            if isinstance(user_start_change_time, datetime):
                delta: timedelta = datetime.now() - user_start_change_time

                if delta.total_seconds() > 1200:
                # if delta.total_seconds() > 120:
                    offer: dict = data.get('selectedOffer')
                    offer_id: int = offer.get('id')
                    response: dict = await api_gateway.get(
                        path=f'{r.userRoutes.offer}/{offer_id}/offer_valid_checker',
                        exp_code=[200]
                    )
                    exception: bool = response.get('exception')

                    if not exception:
                        response_data: dict = response.get('response')
                        changer_online: bool = response.get('owner_online')
                        edit_time: datetime = datetime.strptime(
                            response_data.get('edited'),
                            '%Y-%m-%dT%H:%M:%S.%fZ'
                        )
                        if edit_time < user_start_change_time\
                            or not changer_online:
                            mainMsg: Message = data.get('mainMsg')
                            try:
                                await bot.delete_message(
                                    mainMsg.chat.id,
                                    mainMsg.message_id
                                )
                            except:
                                pass
                            final_step: bool = data.get('final_step')
                            if final_step:
                                mainMsg: Message = await bot.send_message(
                                    user,
                                    text=await msg_maker.final_step_timeout_message(),
                                    reply_markup=await user_kb.final_step_timeout_kb()
                                )
                            else:
                                mainMsg: Message = await bot.send_message(
                                    user,
                                    text=await msg_maker.timeout_message(),
                                    reply_markup=await user_kb.timeout_kb()
                                )
                            await state.update_data(mainMsg = mainMsg)
                            await state.set_state(FSMSteps.USER_TIME_EXPIRED)