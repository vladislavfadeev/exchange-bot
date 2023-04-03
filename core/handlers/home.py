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
    dp.message.register(function_msg)


