from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import Message
from create_bot import dp, bot
from aiogram import F
from core.keyboards.home_kb import user_home_button
from core.api_actions.bot_api import SimpleAPI
from core.utils import msg_var as msg
from core.utils.bot_fsm import FSMSteps
from core.middlwares.routes import r    # Dataclass whith all api routes
from datetime import date
import json
import os




async def command_start(message: Message, state: FSMContext):
    '''Handler ansver on command "/start"
    '''
    await state.set_state(FSMSteps.USER_INIT_STATE)
    await bot.send_message(
        message.from_user.id,
        text=msg.start_message, 
        reply_markup=user_home_button()
    )
    await SimpleAPI.post(
        r.homeRoutes.userInit,
        {
            'tg': message.from_user.id,
            "isActive": True
        }
    )


async def command_staff(message: Message, state: FSMContext):
    '''Handler ansver on command "/staff"
    '''
    response = await SimpleAPI.getDetails(
        r.changerRoutes.changerProfile,
        message.from_user.id
    )
    if response.status_code == 404:
        await message.answer(
            text=msg.staff_404
        )
        await message.delete()

    elif response.status_code == 200:
        await message.answer(
            text= msg.staff_hello
        )
        await message.delete()
        await state.set_state(FSMSteps.CHANGER_INIT_STATE)

    else:
        await message.answer(
            text= msg.staff_else
        )


async def command_help(message: Message):
    '''Handler ansver on command "/help"
    '''
    await bot.send_message(
        message.from_user.id,
        text=msg.start_help_message
    )


async def work_time(message: Message):
    '''Handler ansver on command "/work_time"
    '''
    await bot.send_message(
        message.from_user.id,
        text=message.from_user.id  # Now it send userId
    )

# Only for dev
async def msg_json(message: Message):
    await message.answer('Printed to console')
    json_str = json.dumps(message.dict(), default=str)
    print(json_str)


# async def file_info(message: Message):

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



# Only for dev
async def function_msg(message: Message):
    await message.answer('Any msg')
    


async def register_handlers_main():
    '''Registry handlers there.
    '''
    dp.message.register(
        command_start,
        Command(commands=['start'])
    )
    dp.message.register(
        command_staff,
        Command(commands=['staff'])
    )
    dp.message.register(
        command_help,
        Command(commands=['help']),
    )
    dp.message.register(
        work_time,
        Command(commands=['work_time']),
    )

    # dev func
    dp.message.register(msg_json, F.text == 'get info')
    # dp.message.register(file_info, F.content_type.in_({'photo', 'document'}))
    dp.message.register(function_msg)
    


