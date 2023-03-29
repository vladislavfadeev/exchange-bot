from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from api_actions import user_api
from create_bot import dp, bot
from keyboard import main_kb
import variables.service_message as sm




### Реакция на команду /start
async def command_start(message : types.Message):
    await bot.send_message(message.from_user.id, 
                            text=sm.start_message, 
                            reply_markup=main_kb.customer_start_key)
    post_data = {
        'tg_id': message.from_user.id,
        'name': message.from_user.first_name
    }
    await user_api.insert_user_todb(post_data)

    # async with session.post('/api/v1/customer/', data=post_data) as response:
    #     print(response.status)
    #     print(await response.text())
    #     print(response)



### Реакция на "Справка"
async def command_help(message: types.Message):
    await bot.send_message(message.from_user.id, text=sm.start_help_message)

### Реакиция на "Режим работы"
async def working_hours(message : types.Message):
    # await bot.send_message(message.from_user.id, text=sm.start_work_mode_info)
    await bot.send_message(message.from_user.id, text=message.from_user.id)

### Реакция на "Расположение"
async def pizza__location(message : types.Message):
    await message.answer(message.from_user.id, text=sm.start_work_mode_info)




# async def all_menu_category(message : types.Message):
#     await message.answer('Выберите категорию меню:',reply_markup= client_kb.inline_kb_category)

# @dp.callback_query_handler(lambda x: x.data and x.data.startswith('btn'))
# async def show_category(callback_qwery: types.CallbackQuery):
#     await sqlite_db.sql_read_user(callback_qwery.data.replace('btn ', ''), callback_qwery.from_user.id)


### Регистрируем хендлеры.
def register_handlers_main(dp : Dispatcher):
    dp.register_message_handler(command_start, commands=['start'])
    dp.register_message_handler(command_help, Text(equals='Справка', ignore_case=True))
    dp.register_message_handler(working_hours, Text(equals='Режим работы', ignore_case=True))
    # dp.register_message_handler(pizza__location, Text(equals='Расположение', ignore_case=True))
    # dp.register_message_handler(all_menu_category, Text(equals='Показать меню', ignore_case=True))
