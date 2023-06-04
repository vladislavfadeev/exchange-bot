from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types.callback_query import CallbackQuery
from aiogram import F, Bot, Dispatcher

from core.keyboards import changer_kb, home_kb
from core.keyboards.callbackdata import UserHomeData
from core.api_actions.bot_api import SimpleAPI
from core.utils import msg_maker
from core.utils import  msg_var as msg
from core.utils.bot_fsm import FSMSteps
from core.middlwares.routes import r    # Dataclass whith all api routes
from core.utils.state_cleaner import user_state_cleaner
from core.utils.notifier import (
    alert_message_sender,
    transfers_getter_changer
)
import asyncio



async def command_start(
        message: Message,
        state: FSMContext,
        bot: Bot, 
        api_gateway: SimpleAPI
):
    '''
    Handler ansver on command "/start" and gives for user message
    with "main menu", were he can choose his actions. Exactly it is:
    - Help; Working time; Start change; My messages
    '''
    # delete user command message 
    await message.delete()

    data: dict = await state.get_data()
    mainMsg: Message = data.get('mainMsg')
    msg_list: list = data.get('messageList')
    is_staff: bool = data.get('isStuff')
    await state.update_data(messageList=[])

    # Send user identification data to backend
    response: dict = await api_gateway.post(
        path = r.homeRoutes.userInit,
        data = {
            'tg': message.from_user.id,
            "isActive": True
        },
        exp_code = [201, 400]
    )
    # get request status
    exception: bool = response.get('exception')
    code: int = response.get('status_code')
    if not exception:
        if code == 201:
            del_message = await message.answer('.')
            await del_message.delete()
        # if mainMsg is exists - refresh it for correctly bot working
        if mainMsg:
            try:
                await bot.delete_message(
                    mainMsg.chat.id,
                    mainMsg.message_id
                )
            except:
                pass
            # if user send command /start from any message list - delete it
            if msg_list:
                try:   
                    for i in msg_list:
                        i: Message
                        await bot.delete_message(
                            i.chat.id,
                            i.message_id
                        )
                except:
                    pass
            # if user is staff - check state for new uncompleted 
            # transfers for him and show it in his main message
            if is_staff:
                transfers: list = data.get('uncompleted_transfers')
                mainMsg: Message = await bot.send_message(
                    message.from_user.id,
                    text = await msg_maker.staff_welcome(transfers),
                    reply_markup = await changer_kb.staff_welcome_button(
                        transfers
                    )
                )
                await state.update_data(mainMsg = mainMsg)
                await state.set_state(FSMSteps.STAFF_HOME_STATE)
        # if user is not staff - send him usual start message
        # or he send commad /start for the first time
        if not mainMsg or not is_staff:
            await state.update_data(user_start_change_time = None)
            await user_state_cleaner(state)
            mainMsg =  await bot.send_message(
                message.from_user.id,
                text= await msg_maker.start_message(
                    state
                ),
                reply_markup= await home_kb.user_home_inline_button(
                    state
                )
            )
            await state.update_data(mainMsg = mainMsg)
            await state.set_state(FSMSteps.USER_INIT_STATE)
    else:
        await alert_message_sender(bot, message.from_user.id)


async def command_login(
        message: Message,
        state: FSMContext,
        apscheduler: AsyncIOScheduler,
        api_gateway: SimpleAPI,
        bot: Bot
):
    '''
    Handler ansver on command "/login" and check user id in backend.
    If he is staff - bot send message with personal menu for changers.
    '''

    data: dict = await state.get_data()
    mainMsg: Message = data.get('mainMsg')
    messageList: list = data.get('messageList')
    isStuff: bool = data.get('isStuff')
    uncompleted_transfers: list = data.get('uncompleted_transfers')
    new_transfer: list = data.get('new_transfer')
    # if bot state have not information about current user status,
    # or user is not staff
    if not isStuff:
        # send request for check user id
        response: dict = await api_gateway.get_detail(
            path=r.changerRoutes.changerProfile,
            detailUrl=message.from_user.id,
            exp_code=[200, 404]
        )
        code: int = response.get('status_code')
        exception: bool = response.get('exception')
        if not exception:
            if code == 404:
                # if user is not staff bot will tell him about it
                await message.delete()
                info_msg = await message.answer(
                    text=msg.staff_404
                )
                await asyncio.sleep(3)
                try:
                    await info_msg.delete()
                except:
                    pass

            elif code == 200:
                # if backend replied that current user is a staff
                getter_id = f'user_getter-{message.from_user.id}'
                job_list: list = [job.id for job in apscheduler.get_jobs()]
                # delete command message
                await message.delete()
                await user_state_cleaner(state)
                await state.update_data(user_start_change_time = None)
                if getter_id in job_list:
                    apscheduler.pause_job(getter_id)
                if uncompleted_transfers is None:
                    await state.update_data(uncompleted_transfers = [])
                if new_transfer is None:
                    await state.update_data(new_transfer = [])
                # user can send login commad from any message list.
                # if he do that - bot delete all this messages
                if messageList:
                    for i in messageList:
                        i: Message
                        try:
                            await i.delete()
                        except:
                            pass
                # if mainMsg is exists - refresh it 
                # for correctly bot working
                if mainMsg:
                    try:
                        await mainMsg.delete()
                    except:
                        pass

                changer_id = message.from_user.id
                patch_data = {
                    'online': True
                }
                # change staff status to online
                response: dict = await api_gateway.patch(
                    path=r.changerRoutes.changerProfile,
                    detailUrl=changer_id,
                    data=patch_data,
                    exp_code=[200]
                )
                exception: bool = response.get('exception')
                if not exception:
                    # send staff welcome message and save it in to bot state
                    mainMsg: Message = await bot.send_message(
                        message.from_user.id,
                        text = await msg_maker.staff_welcome(
                            uncompleted_transfers
                        ),
                        reply_markup = await changer_kb.staff_welcome_button(
                            uncompleted_transfers
                        )
                    )
                    await state.update_data(mainMsg = mainMsg)
                    await state.update_data(isStuff = True)
                    await state.update_data(logout_time = None)
                    await state.set_state(FSMSteps.STAFF_HOME_STATE)
                    # there bot add changer notifier to job list if
                    # it is not in list
                    getter_id = f'changer_getter-{message.from_user.id}'
                    job_list: list = apscheduler.get_jobs()
                    job_id_list: list = [job.id for job in job_list]

                    if getter_id not in job_id_list:
                        apscheduler.add_job(
                            transfers_getter_changer,
                            'interval',
                            minutes=1,
                            id = getter_id,
                            kwargs={
                                'changer_id': changer_id,
                            }
                        )
                else:
                    await alert_message_sender(bot, message.from_user.id)
        else:
            await alert_message_sender(bot, message.from_user.id)
    # if bot state have information about current user
    elif isStuff:
        await message.delete()
        del_msg = await bot.send_message(
            message.from_user.id,
            text = msg.staff_islogin
        )
        await asyncio.sleep(2)
        try:
            await del_msg.delete()
        except:
            pass



async def command_logout(
        message: Message,
        state: FSMContext,
        apscheduler: AsyncIOScheduler,
        bot: Bot,
        api_gateway: SimpleAPI
):
    '''
    React on /logout command. If user was logged in
    he will be logged out and his offers will not be shown.
    '''
    data: dict = await state.get_data()
    mainMsg: Message = data.get('mainMsg')
    messageList: list = data.get('messageList')
    isStuff: bool = data.get('isStuff')
    await message.delete()
    # if current user is staff
    if isStuff:
        if messageList:
            # if user send command from message list
            for i in messageList:
                i: Message
                try:
                    await bot.delete_message(
                        i.chat.id,
                        i.message_id
                    )
                except:
                    pass
        # refresh mainMsg for correctly bot working
        if mainMsg:
            try:
                await bot.delete_message(
                    mainMsg.chat.id,
                    mainMsg.message_id
                )
            except:
                pass
        mainMsg: Message =  await bot.send_message(
            message.from_user.id,
            text= await msg_maker.start_message(
                state
            ), 
            reply_markup= await home_kb.user_home_inline_button(
                state
            )
        )
        # set offline staff status
        patch_data = {'online': False}
        response: dict = await api_gateway.patch(
            path=r.changerRoutes.changerProfile,
            detailUrl=message.from_user.id,
            data=patch_data,
            exp_code=[200]
        )
        exception: bool = response.get('exception')
        if not exception:
            # fix all changes in bot state
            await state.update_data(mainMsg = mainMsg)
            await state.update_data(isStuff = False)
            await state.set_state(FSMSteps.USER_INIT_STATE)
            # check existense user notifier job in job list. If it is
            # exist - resume this job.
            getter_id = f'user_getter-{message.from_user.id}'
            job_list: list = [job.id for job in apscheduler.get_jobs()]
            if getter_id in job_list:
                apscheduler.resume_job(getter_id)
            # remove other jobs from job list
            await state.update_data(logout_time = datetime.now())
            # apscheduler.remove_job(
            #     f'changer_getter-{message.from_user.id}'
            # )
            # try:
            #     apscheduler.remove_job(
            #         f'changer_notifier-{message.from_user.id}'
            #     )
            # except:
            #     pass
        else:
            await alert_message_sender(bot, message.from_user.id)
    # if user have not staff status
    else:
        del_msg = await bot.send_message(
            message.from_user.id,
            text = msg.user_not_loggin
        )
        await asyncio.sleep(2)
        try:
            await del_msg.delete()
        except:
            pass



async def user_main_menu(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: UserHomeData,
        bot: Bot, 
):
    '''
    Show start message for users depending of his status
    (staff or not)
    '''
    data: dict = await state.get_data()
    msg_list: list = data.get('messageList')
    mainMsg: Message = data.get('mainMsg')
    is_staff: bool = data.get('isStuff')
    await state.update_data(messageList=[])
    # if user send command from message list
    if msg_list:
        for i in msg_list:
            i: Message
            try:
                await bot.delete_message(
                    i.chat.id,
                    i.message_id
                )
            except:
                pass
    # refresh mainMsg for correctly bot working
    try:
        await bot.delete_message(
            mainMsg.chat.id,
            mainMsg.message_id
        )
    except:
        pass
    # if in bot state have 'isStaff' key with bool value True
    if is_staff:
        transfers: list = data.get('uncompleted_transfers')
        mainMsg = await bot.send_message(
            call.from_user.id,
            text = await msg_maker.staff_welcome(transfers),
            reply_markup = await changer_kb.staff_welcome_button(
                transfers
            )
        )
        await state.update_data(mainMsg = mainMsg)
        await state.set_state(FSMSteps.STAFF_HOME_STATE)
    # if 'isStaff' key does not exists or have bool value False
    else:
        await user_state_cleaner(state)
        await state.update_data(user_start_change_time = None)
        mainMsg = await bot.send_message(
            call.from_user.id,
            text= await msg_maker.start_message(
                state
            ), 
            reply_markup = await home_kb.user_home_inline_button(
                state
            )
        )
        await state.update_data(mainMsg = mainMsg)
        await state.set_state(FSMSteps.USER_INIT_STATE)



async def get_help(
        call: CallbackQuery,
):
    '''
    Show information about rules, for correctly using the bot 
    '''
    await call.message.edit_text(
        text=msg.help_message,
        reply_markup= await home_kb.user_back_home_inline_button()
    )


async def support_us(
        call: CallbackQuery,
):
    '''
    Show information about work time
    '''
    await call.message.edit_text(
        text=msg.support_us_message,
        reply_markup= await home_kb.user_back_home_inline_button()
    )



async def del_not_handled_message(message: Message, bot: Bot):
    '''
    Service handler.
    '''
    bill = message.text
    await message.delete()
    del_msg = await bot.send_message(
        message.from_user.id,
        text = f'Unknown command: "{bill}"')
    await asyncio.sleep(3)
    try:
        await del_msg.delete()
    except:
        pass



# Only for dev mode
async def msg_dumps(
        message: Message,
        state: FSMContext,
        apscheduler: AsyncIOScheduler
):

    i = apscheduler.get_jobs()
    it = await state.get_data()
    t = it.get('test')
    print(i)
    # await message.answer('Printed to console')
    # fileId = message.document.file_id
    # await state.update_data(fileId = fileId)
    # dumps_str = dumps.dumps(message.dict(), default=str)
    # print(dumps_str)
    # res = await bot.send_message(
    #     message.from_user.id,
    #     text='yh'
    # )
    # print(dumps.dumps(res.dict(), default=str))
    await message.delete()



async def setup_home_handlers(dp: Dispatcher):
    '''
    Registry callback handlers.
    '''
    dp.message.register(
        command_start,
        Command(commands=['start'],)
    )
    dp.message.register(
        command_login,
        Command(commands=['login'])
    )
    dp.message.register(
        command_logout,
        Command(commands=['logout'])
    )
    dp.message.register(msg_dumps, F.text == 'get_info')
    dp.callback_query.register(
        user_main_menu,
        UserHomeData.filter(F.action == 'cancel'),
    )
    dp.callback_query.register(
        get_help,
        UserHomeData.filter(F.action == 'info'),
    )
    dp.callback_query.register(
        support_us,
        UserHomeData.filter(F.action == 'support_us'),
    )


async def setup_service_handlers(dp: Dispatcher):
    dp.message.register(
        del_not_handled_message,
    )