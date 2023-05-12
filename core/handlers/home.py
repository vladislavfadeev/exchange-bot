from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types.callback_query import CallbackQuery
from aiogram import F, Bot, Dispatcher

from core.keyboards import changer_kb, home_kb
from core.keyboards.callbackdata import HomeData
from core.api_actions.bot_api import SimpleAPI
from core.utils import msg_maker
from core.utils import  msg_var as msg
from core.utils.bot_fsm import FSMSteps
from core.middlwares.routes import r    # Dataclass whith all api routes
from core.utils.notifier import (
    transfers_getter_changer
)
import asyncio


async def command_start(
        message: Message,
        state: FSMContext,
        bot: Bot, 
        dp: Dispatcher
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
    await state.update_data(messageList=[])

    # Send user identification data to db
    await SimpleAPI.post(
        r.homeRoutes.userInit,
        {
            'tg': message.from_user.id,
            "isActive": True
        }
    )
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
        if data.get('isStuff'):
            transfers: list = data.get('uncompleted_transfers')
            mainMsg: Message = await bot.send_message(
                message.from_user.id,
                text = await msg_maker.staff_welcome(transfers),
                reply_markup = await changer_kb.staff_welcome_button(
                    transfers
                )
            )
            await state.update_data(mainMsg = mainMsg)
            await state.set_state(FSMSteps.STUFF_INIT_STATE)
        # if user is not staff - send him usual start message
        else:
            mainMsg =  await bot.send_message(
                message.from_user.id,
                text= await msg_maker.start_message(
                    message.from_user.id,
                    bot,
                    dp
                ),
                reply_markup= await home_kb.user_home_inline_button(
                    message.from_user.id,
                    bot,
                    dp
                )
            )
        await state.update_data(mainMsg = mainMsg)
        await state.set_state(FSMSteps.USER_INIT_STATE)
            


async def command_login(
        message: Message,
        state: FSMContext,
        apscheduler: AsyncIOScheduler,
        bot: Bot
):
    '''
    Handler ansver on command "/login" and check user id in backend.
    If he is staff - bot send message with personal menu for changers.
    '''
    # send request for check user id
    response = await SimpleAPI.getDetails(
        r.changerRoutes.changerProfile,
        message.from_user.id
    )
    data: dict = await state.get_data()
    mainMsg: Message = data.get('mainMsg')
    messageList: list = data.get('messageList')
    isStuff: bool = data.get('isStuff')
    uncompleted_transfers: list = data.get('uncompleted_transfers')
    new_transfer: list = data.get('new_transfer')
    # if bot state have not information about current user status,
    # or user is not staff
    if not isStuff:
        if response.status_code == 404:
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

        elif response.status_code == 200:
            # if backend replied that current user is a staff
            getter_id = f'user_getter-{message.from_user.id}'
            job_list: list = [job.id for job in apscheduler.get_jobs()]
            # delete command message
            await message.delete()
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
            # if mainMsg is exists - refresh it for correctly bot working
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
            await SimpleAPI.patch(
                r.changerRoutes.changerProfile,
                changer_id,
                patch_data
            )
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
            await state.set_state(FSMSteps.STUFF_INIT_STATE)
            # there bot add changer notifier to job list if it is not in list
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
        dp: Dispatcher
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
                message.from_user.id,
                bot,
                dp
            ), 
            reply_markup= await home_kb.user_home_inline_button(
                message.from_user.id,
                bot,
                dp
            )
        )
        # set offline staff status
        patch_data = {'online': False}
        await SimpleAPI.patch(
            r.changerRoutes.changerProfile,
            message.from_user.id,
            patch_data
        )
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
        apscheduler.remove_job(f'changer_getter-{message.from_user.id}')
        try:
            apscheduler.remove_job(f'changer_notifier-{message.from_user.id}')
        except:
            pass
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
        callback_data: HomeData,
        bot: Bot, 
        dp: Dispatcher
):
    '''
    Show start message for users depending of his status
    (staff or not)
    '''
    data: dict = await state.get_data()
    msg_list: list = data.get('messageList')
    mainMsg: Message = data.get('mainMsg')
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
    if data.get('isStuff'):
        transfers: list = data.get('uncompleted_transfers')
        mainMsg = await bot.send_message(
            call.from_user.id,
            text = await msg_maker.staff_welcome(transfers),
            reply_markup = await changer_kb.staff_welcome_button(
                transfers
            )
        )
        await state.update_data(mainMsg = mainMsg)
        await state.set_state(FSMSteps.STUFF_INIT_STATE)
    # if 'isStaff' key does not exists or have bool value False
    else:
        mainMsg = await bot.send_message(
            call.from_user.id,
            text= await msg_maker.start_message(
                call.from_user.id,
                bot,
                dp
            ), 
            reply_markup = await home_kb.user_home_inline_button(
                call.from_user.id,
                bot,
                dp
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
        text=msg.start_help_message,
        reply_markup= await home_kb.user_back_home_inline_button()
    )


async def work_time(
        call: CallbackQuery,
):
    '''
    Show information about work time
    '''
    await call.message.edit_text(
        text=msg.start_work_mode_info,
        reply_markup= await home_kb.user_back_home_inline_button()
    )



async def del_not_handled_message(message: Message, bot: Bot):

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
async def msg_dumps(message: Message, state: FSMContext, apscheduler: AsyncIOScheduler):

    i = apscheduler.get_jobs()
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



async def register_handlers_home(dp: Dispatcher):
    '''
    Registry message handlers.
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
    dp.message.register(
        del_not_handled_message,
    )



async def register_callback_handlers_home(dp: Dispatcher):
    '''
    Registry callback handlers.
    '''
    dp.callback_query.register(
        user_main_menu,
        HomeData.filter(F.action == 'cancel'),
    )
    dp.callback_query.register(
        get_help,
        HomeData.filter(F.action == 'info'),
    )
    dp.callback_query.register(
        work_time,
        HomeData.filter(F.action == 'time'),
    )