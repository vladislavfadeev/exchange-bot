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
import json



async def command_start(message: Message, state: FSMContext):
    '''Handler ansver on command "/start"
    '''
    await state.set_state(FSMSteps.INIT_STATE)
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


async def file_info(message: Message):
    # if message.photo:
        # import json
        # file = await bot.get_file(message.photo[-1].file_id)
        # await bot.download_file(file.file_path, f'{message.from_user.id} - photo.jpg')

        # json_str = json.dumps(message.dict(), default=str)
        # print(json_str) https://api.telegram.org/file/bot<token>/<file_path>

    if message.document:
        json_str = json.dumps(message.dict(), default=str)
        print(json_str)

        # file1 = await bot.get_file(message.document.file_id)
        print(message.document.file_id)
        await bot.send_document('151436997', document= 'BQACAgIAAxkBAAIMnGQyl2KgWg9C8IpI3EspVDgpA4a-AAIMKwACc5KZSWJceE5Kb4_QLwQ')
        # await bot.download_file(file1.file_path, message.document.file_name)



# Only for dev
async def function_msg(message: Message):
    await message.answer('Any msg')
    await bot.send_document('5934368607', document= 'BQACAgIAAxkBAAIMnGQyl2KgWg9C8IpI3EspVDgpA4a-AAIMKwACc5KZSWJceE5Kb4_QLwQ')



async def register_handlers_main():
    '''Registry handlers there.
    '''
    dp.message.register(
        command_start,
        Command(commands=['start'])
    )
    dp.message.register(
        command_help,
        Command(commands=['help']),
        FSMSteps.INIT_STATE
    )
    dp.message.register(
        work_time,
        Command(commands=['work_time']),
        FSMSteps.INIT_STATE
    )

    # dev func
    dp.message.register(msg_json, F.text == 'get info')
    dp.message.register(file_info, FSMSteps.INIT_STATE, F.document)
    dp.message.register(function_msg)
    


