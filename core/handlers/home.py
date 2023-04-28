import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types.callback_query import CallbackQuery
from aiogram import F
from core.keyboards import changer_kb, home_kb
from core.keyboards.callbackdata import HomeData
from create_bot import dp, bot
from core.keyboards.home_kb import user_home_inline_button
from core.api_actions.bot_api import SimpleAPI
from core.utils import msg_maker
from core.utils import  msg_var as msg
from core.utils.bot_fsm import FSMSteps
from core.middlwares.routes import r    # Dataclass whith all api routes
from datetime import date
import os
from core.utils.notifier import (
    transfers_getter_changer
)


async def command_start(
        message: Message,
        state: FSMContext,
        apscheduler: AsyncIOScheduler
):
    '''Handler ansver on command "/start"
    '''
    await message.delete()
    data = await state.get_data()
    mainMsg: Message = data.get('mainMsg')
    msg_list = data.get('messageList')
    await state.update_data(messageList=[])

    if mainMsg:

        try:
            await bot.delete_message(
                mainMsg.chat.id,
                mainMsg.message_id
            )
        except:
            pass
        
        if msg_list:
            try:   
                for i in msg_list:
                    await bot.delete_message(
                        i.chat.id,
                        i.message_id
                    )
            except:
                pass

        try:
            if data.get('isStuff'):

                transfers = data.get('uncompleted_transfers')

                mainMsg = await bot.send_message(
                    message.from_user.id,
                    text = await msg_maker.staff_welcome(transfers),
                    reply_markup = await changer_kb.staff_welcome_button(
                        transfers
                    )
                )
                await state.set_state(FSMSteps.STUFF_INIT_STATE)

            else:
                
                mainMsg =  await bot.send_message(
                    message.from_user.id,
                    text= await msg_maker.start_message(message.from_user.id),
                    reply_markup= await user_home_inline_button(message.from_user.id)
                )
            
            await state.update_data(
                mainMsg = mainMsg
            )
            
        except Exception as e:
            logging.exception(e)
            
            mainMsg =  await bot.send_message(
                message.from_user.id,
                text= await msg_maker.start_message(message.from_user.id),
                reply_markup= await user_home_inline_button(message.from_user.id)
            )
            
            await state.update_data(mainMsg = mainMsg)
            await state.set_state(FSMSteps.USER_INIT_STATE)
    else:
        mainMsg =  await bot.send_message(
            message.from_user.id,
            text= await msg_maker.start_message(message.from_user.id), 
            reply_markup= await user_home_inline_button(message.from_user.id)
        )
        await SimpleAPI.post(
            r.homeRoutes.userInit,
            {
                'tg': message.from_user.id,
                "isActive": True
            }
        )
        await state.update_data(mainMsg = mainMsg)
        await state.set_state(FSMSteps.USER_INIT_STATE)



async def command_login(
        message: Message,
        state: FSMContext,
        apscheduler: AsyncIOScheduler
):
    '''Handler ansver on command "/login"
    '''

    response = await SimpleAPI.getDetails(
        r.changerRoutes.changerProfile,
        message.from_user.id
    )
    data = await state.get_data()
    mainMsg = data.get('mainMsg')
    messageList = data.get('messageList')
    isStuff = data.get('isStuff')
    uncompleted_transfers = data.get('uncompleted_transfers')
    new_transfer = data.get('new_transfer')

    if not isStuff:

        if response.status_code == 404:
            info_msg = await message.answer(
                text=msg.staff_404
            )
            await message.delete()
            await asyncio.sleep(3)
            try:
                await info_msg.delete()
            except:
                pass

        elif response.status_code == 200:

            getter_id = f'user_getter-{message.from_user.id}'
            job_list: list = [job.id for job in apscheduler.get_jobs()]
                
            if getter_id in job_list:
                apscheduler.pause_job(getter_id)

            if uncompleted_transfers is None:
                await state.update_data(uncompleted_transfers = [])

            if new_transfer is None:
                await state.update_data(new_transfer = [])

            if messageList:
                
                for i in messageList:
                    try:
                        await i.delete()
                    except:
                        pass
            
            if mainMsg:
                try:
                    await mainMsg.delete()
                except:
                    pass

            changer_id = message.from_user.id

            patch_data = {
                'online': True
            }
            await SimpleAPI.patch(
                r.changerRoutes.changerProfile,
                changer_id,
                patch_data
            )

            transfers = data.get('uncompleted_transfers')

            await message.delete()
            mainMsg = await bot.send_message(
                message.from_user.id,
                text = await msg_maker.staff_welcome(
                    transfers
                ),
                reply_markup = await changer_kb.staff_welcome_button(
                    transfers
                )
            )
            await state.update_data(mainMsg = mainMsg)
            await state.update_data(isStuff = True)
            await state.set_state(FSMSteps.STUFF_INIT_STATE)
            
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

    elif isStuff:
        await message.delete()
        del_msg = await bot.send_message(
            message.from_user.id,
            text = f'Вы уже вошли в систему как зарегистрированный пользователь'
        )
        await asyncio.sleep(2)
        try:
            await del_msg.delete()
        except:
            pass



async def command_logout(
        message: Message,
        state: FSMContext,
        apscheduler: AsyncIOScheduler
):
    '''
    '''
    data = await state.get_data()
    mainMsg = data.get('mainMsg')
    messageList = data.get('messageList')
    isStuff = data.get('isStuff')

    await message.delete()

    if isStuff:

        if messageList:
            
            for i in messageList:
                try:
                    await i.delete()
                except:
                    pass
        
        if mainMsg:
            try:
                await mainMsg.delete()
            except:
                pass

        mainMsg =  await bot.send_message(
            message.from_user.id,
            text= await msg_maker.start_message(message.from_user.id), 
            reply_markup= await user_home_inline_button(message.from_user.id)
        )
        patch_data = {
            'online': False
        }

        await SimpleAPI.patch(
            r.changerRoutes.changerProfile,
            message.from_user.id,
            patch_data
        )
        
        await state.update_data(mainMsg = mainMsg)
        await state.update_data(isStuff = False)
        await state.set_state(FSMSteps.USER_INIT_STATE)
        
        getter_id = f'user_getter-{message.from_user.id}'
        job_list: list = [job.id for job in apscheduler.get_jobs()]
            
        if getter_id in job_list:
            apscheduler.resume_job(getter_id)

        apscheduler.remove_job(f'changer_getter-{message.from_user.id}')
        try:
            apscheduler.remove_job(f'changer_notifier-{message.from_user.id}')
        except:
            pass

    else:

        del_msg = await bot.send_message(
            message.from_user.id,
            text = f'Вы не авторизованы'
        )
        await asyncio.sleep(2)
        try:
            await del_msg.delete()
        except:
            pass
    



async def user_main_menu(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: HomeData
):
    ''' Show "main" message
    '''
    data = await state.get_data()
    await state.update_data(messageList=[])
    msg_list = data.get('messageList')
    mainMsg: Message = data.get('mainMsg')

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

    try:
        await bot.delete_message(
            mainMsg.chat.id,
            mainMsg.message_id
        )
    except:
        pass

    try:

        if data.get('isStuff'):

            transfers = data.get('uncompleted_transfers')
                
            mainMsg = await bot.send_message(
                call.from_user.id,
                text = await msg_maker.staff_welcome(transfers),
                reply_markup = await changer_kb.staff_welcome_button(
                    transfers
                )
            )
            await state.update_data(mainMsg = mainMsg)
            
            await state.set_state(FSMSteps.STUFF_INIT_STATE)
        
        else:

            mainMsg = await bot.send_message(
                call.from_user.id,
                text= await msg_maker.start_message(call.from_user.id), 
                reply_markup= await user_home_inline_button(call.from_user.id)
            )
            await state.update_data(mainMsg = mainMsg)

            await state.set_state(FSMSteps.USER_INIT_STATE)
        
    except Exception as e:
        logging.exception(e)
        
        if data.get('isStuff'):

            transfers = data.get('uncompleted_transfers')

            await call.message.edit_text(
                text = await msg_maker.staff_welcome(transfers),
                reply_markup = await changer_kb.staff_welcome_button(
                    transfers
                )
            )
            await state.set_state(FSMSteps.STUFF_INIT_STATE)

        else:
            await call.message.edit_text(
                text=await msg_maker.start_message(call.from_user.id),
                reply_markup= await user_home_inline_button(call.from_user.id)
            )
            await state.set_state(FSMSteps.USER_INIT_STATE)



async def get_help(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: HomeData
):
    ''' Show information about rules, for correctly using the bot 
    '''
    await call.message.edit_text(
        text=msg.start_help_message,
        reply_markup= await home_kb.user_back_home_inline_button()
    )


async def work_time(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: HomeData
):
    ''' Show information about work time
    '''
    await call.message.edit_text(
        text=msg.start_work_mode_info,
        reply_markup= await home_kb.user_back_home_inline_button()
    )



async def del_not_handled_message(message: Message):

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



# Only for dev
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



async def register_handlers_home():
    '''Registry handlers there.
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



async def register_callback_handlers_home():
    '''
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








    # dp.message.register(file_info, F.content_type.in_({'photo', 'document'}))
    # dp.message.register(file_info, F.text == 'get file')


# async def file_info(message: Message, state: FSMContext):

#     data = await state.get_data()
#     await bot.send_document('151436997', document= data['fileId'])
    # if message.document:
    #     dumps_str = dumps.dumps(message.dict(), default=str)
    #     print(dumps_str)

    #     file1 = await bot.get_file(message.document.file_id)
    #     print(message.document.file_id)
    #     await bot.send_document('151436997', document= 'BQACAgIAAxkBAAIMnGQyl2KgWg9C8IpI3EspVDgpA4a-AAIMKwACc5KZSWJceE5Kb4_QLwQ')
    #     await bot.download_file(file1.file_path, message.document.file_name)
    # !dir = f'proof/{message.from_user.id}/{date.today()}'

    # !if not os.path.exists(dir):
    #     os.makedirs(dir)

    # !if message.photo:
    #     await message.answer(text='photo')
    #     file = await bot.get_file(message.photo[-1].file_id)
    #     await bot.download_file(file.file_path, f'{dir}/{message.photo[-1].file_unique_id}.jpg')
    #     # dumps_str = dumps.dumps(message.dict(), default=str)
    #     # print(dumps_str)

    # !elif message.document:
    #     await message.answer(text='doc')
    #     file = await bot.get_file(message.document.file_id)
    #     await bot.download_file(file.file_path, f'{dir}/{message.document.file_name}')


