from aiogram.fsm.context import FSMContext



async def user_state_cleaner(state: FSMContext):
    '''
    '''
    await state.update_data(selected_curr_id= None)
    await state.update_data(selectedOffer= None)
    await state.update_data(sellAmount= None)
    await state.update_data(changerBank= None)
    await state.update_data(userBank= None)
    await state.update_data(userAccount= None)
    await state.update_data(final_step= False)