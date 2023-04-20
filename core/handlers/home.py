import asyncio
import logging
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.types.callback_query import CallbackQuery
from core.keyboards import changer_kb, home_kb
from core.keyboards.callbackdata import HomeData
from core.utils.notifier import changer_notifier, get_new_transfers
from create_bot import dp, bot, scheduler
from aiogram import F
from core.keyboards.home_kb import user_home_button, user_home_inline_button
from core.api_actions.bot_api import SimpleAPI
from core.utils import msg_maker, msg_var as msg
from core.utils.bot_fsm import FSMSteps
from core.middlwares.routes import r    # Dataclass whith all api routes
from datetime import date
import json
import os

# from core.utils.notifier import 



async def command_start(message: Message, state: FSMContext):
    '''Handler ansver on command "/start"
    '''
    await message.delete()
    data = await state.get_data()

    if data.get('mainMsg'):
        try:
            await bot.delete_message(
                chat_id= message.from_user.id,              # обернуть в отдельный try, иначе выдает меняле сообщение
                message_id=data['mainMsg'].message_id       # юзера при нажатии на /start из какого-либо списка, так как 
            )                                               # mainMsg удаляется при формировании списка и бот потом его 
            if data.get('isStuff'):                         # не может найти и отрабатывает exception

                transfers = data.get('user_transfers')

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
                    text=msg.start_message, 
                    reply_markup= await user_home_inline_button()
                )
            await state.update_data(mainMsg = mainMsg)
            
        except Exception as e:
            logging.exception(e)
            await state.update_data(messageList=[])
            msg_list = data.get('messageList')

            for i in range(len(msg_list)):
                await msg_list[i].delete()
            
            mainMsg =  await bot.send_message(
                message.from_user.id,
                text=msg.start_message,
                reply_markup= await user_home_inline_button()
            )
            await state.update_data(mainMsg = mainMsg)
            await state.set_state(FSMSteps.USER_INIT_STATE)
    else:
        mainMsg =  await bot.send_message(
            message.from_user.id,
            text=msg.start_message, 
            reply_markup= await user_home_inline_button()
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


async def command_staff(message: Message, state: FSMContext):
    '''Handler ansver on command "/staff"
    '''
    data = await state.get_data()

    response = await SimpleAPI.getDetails(
        r.changerRoutes.changerProfile,
        message.from_user.id
    )
    data = await state.get_data()
    mainMsg = data.get('mainMsg')

    if not data.get('isStuff'):
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
            transfers = data.get('user_transfers')

            await message.delete()
            await mainMsg.edit_text(
                text = await msg_maker.staff_welcome(
                    # response.json(),
                    transfers
                ),
                reply_markup = await changer_kb.staff_welcome_button(
                    transfers
                )
            )
            await state.update_data(isStuff = True)
            await state.set_state(FSMSteps.STUFF_INIT_STATE)
            
            scheduler.add_job(
                get_new_transfers,
                'interval',
                minutes=1,
                args=(message.from_user.id, state)
            )
            scheduler.add_job(
                changer_notifier,
                'interval',
                minutes=1.5,
                args=(state, )
            )
    else:
        await message.delete()
        del_msg = await bot.send_message(
            message.from_user.id,
            text = f'Вы уже вошли в систему как зарегистрированный пользователь'
        )
        # await state.set_state(FSMSteps.STUFF_INIT_STATE)
        await asyncio.sleep(3)
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

    try:
        
        if len(msg_list):
            for i in range(len(msg_list)):
                await msg_list[i].delete()

        if data.get('isStuff'):

            transfers = data.get('user_transfers')

            if len(msg_list):
                mainMsg = await bot.send_message(
                    call.from_user.id,
                    text = await msg_maker.staff_welcome(transfers),
                    reply_markup = await changer_kb.staff_welcome_button(
                        transfers
                    )
                )
                await state.update_data(mainMsg = mainMsg)

            else:
                await call.message.edit_text(
                    text = await msg_maker.staff_welcome(transfers),
                    reply_markup = await changer_kb.staff_welcome_button(
                        transfers
                    )
                )
            
            await state.set_state(FSMSteps.STUFF_INIT_STATE)
        
        else:
            if len(msg_list):
                mainMsg = await bot.send_message(
                    call.from_user.id,
                    text=msg.start_message, 
                    reply_markup= await user_home_inline_button()
                )
                await state.update_data(mainMsg = mainMsg)

            else:
                await call.message.edit_text(
                    text=msg.start_message, 
                    reply_markup= await user_home_inline_button()
                )

            await state.set_state(FSMSteps.USER_INIT_STATE)
        
    except Exception as e:
        logging.exception(e)
        
        if data.get('isStuff'):

            transfers = data.get('user_transfers')

            await call.message.edit_text(
                text = await msg_maker.staff_welcome(transfers),
                reply_markup = await changer_kb.staff_welcome_button(
                    transfers
                )
            )
            await state.set_state(FSMSteps.STUFF_INIT_STATE)

        else:
            await call.message.edit_text(
                text=msg.start_message, 
                reply_markup= await user_home_inline_button()
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
        text = f'неизвестная команда {bill}')
    await asyncio.sleep(3)
    try:
        await del_msg.delete()
    except:
        pass


async def command_cancel(message: Message, state: FSMContext):
    '''
    '''
    await message.answer('Отменено')
    await bot.send_message(
        message.from_user.id,
        text=msg.start_message, 
        reply_markup=user_home_button()
    )
    await state.set_state(FSMSteps.USER_INIT_STATE)



# Only for dev
async def msg_json(message: Message, state: FSMContext):
    await message.answer('Printed to console')
    fileId = message.document.file_id
    await state.update_data(fileId = fileId)
    # json_str = json.dumps(message.dict(), default=str)
    # print(json_str)
    # res = await bot.send_message(
    #     message.from_user.id,
    #     text='yh'
    # )
    # print(json.dumps(res.dict(), default=str))
    await message.delete()
        


async def register_handlers_home():
    '''Registry handlers there.
    '''
    dp.message.register(
        command_start,
        Command(commands=['start'],),
    )
    dp.message.register(
        command_staff,
        Command(commands=['staff'])
    )
    dp.message.register(
        command_cancel,
        F.text == 'Отмена'
    )
    dp.message.register(
        del_not_handled_message,
    )

    # dev func
    dp.message.register(msg_json, F.document)
    # dp.message.register(file_info, F.content_type.in_({'photo', 'document'}))
    # dp.message.register(file_info, F.text == 'get file')


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











# async def file_info(message: Message, state: FSMContext):

#     data = await state.get_data()
#     await bot.send_document('151436997', document= data['fileId'])
    # if message.document:
    #     json_str = json.dumps(message.dict(), default=str)
    #     print(json_str)

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
    #     # json_str = json.dumps(message.dict(), default=str)
    #     # print(json_str)

    # !elif message.document:
    #     await message.answer(text='doc')
    #     file = await bot.get_file(message.document.file_id)
    #     await bot.download_file(file.file_path, f'{dir}/{message.document.file_name}')


