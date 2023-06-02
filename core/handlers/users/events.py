from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiogram.types.callback_query import CallbackQuery
from aiogram.types import Message
from aiogram import F, Bot, Dispatcher

from core.keyboards import admin_kb, home_kb
from core.middlwares.settigns import appSettings
from core.middlwares.routes import r    # Dataclass whith all api routes
from core.utils import msg_maker
from core.api_actions.bot_api import SimpleAPI
from core.utils.bot_fsm import FSMSteps
from core.utils import msg_var as msg
from core.keyboards import user_kb
from core.keyboards.callbackdata import UserHomeData
from core.utils.notifier import alert_message_sender



async def new_user_event(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: UserHomeData,
        api_gateway: SimpleAPI,
        bot: Bot
):
    '''
    Handles show user his events.
    Responses from exchangers to outgoing transfers
    '''
    data: dict = await state.get_data()
    mainMsg: Message = data.get('mainMsg')
    user_event: list = data.get('user_events')
    
    if callback_data.action == 'user_new_events':
        if user_event:
            try:
                await bot.delete_message(
                    mainMsg.chat.id,
                    mainMsg.message_id
                )
            except:
                pass
            messageList = []
            for event in user_event:
                event: dict
                changer_proof_type: str = event.get('changerProofType')
                proof_id: str = event.get('changerProof')
                if changer_proof_type == 'photo':
                    self_msg: Message = await bot.send_photo(
                        call.from_user.id,
                        photo=proof_id,
                        caption=await msg_maker.user_show_events(event),
                        reply_markup=await user_kb.user_show_event_kb(event),
                    )
                elif changer_proof_type == 'document':
                    self_msg: Message = await bot.send_document(
                        call.from_user.id,
                        document=proof_id,
                        caption=await msg_maker.user_show_events(event),
                        reply_markup=await user_kb.user_show_event_kb(event),
                    )
                messageList.append(self_msg)
            sep_msg: Message = await bot.send_message(
                call.from_user.id,
                text = msg.separator,
                reply_markup = await home_kb.user_back_home_inline_button()
            )
            messageList.append(sep_msg)
            await state.update_data(messageList = messageList)
        else:
            await call.message.edit_text(
                text = msg.user_empty_event,
                reply_markup = await home_kb.user_back_home_inline_button()
            )
        
    elif callback_data.action == 'user_transfer_accepted':
        messageList: list = data.get('messageList')       
        transfer_id: int = callback_data.id
        patch_data = {
            'userAcceptDate': datetime.now(),
            'isCompleted': True
        }
        response: dict = await api_gateway.patch(
            path=r.userRoutes.transactions,
            detailUrl=transfer_id,
            data=patch_data,
            exp_code=[200]
        )
        exception: bool = response.get('exception')
        if not exception:
            new_event_list: list = [i for i in user_event if i['id'] != transfer_id]
            await state.update_data(user_events = new_event_list)
            if not new_event_list:
                for i in messageList:
                    i: Message
                    try:
                        await bot.delete_message(
                            i.chat.id,
                            i.message_id
                        )
                    except:
                        pass
                mainMsg = await bot.send_message(
                    call.from_user.id,
                    text= await msg_maker.start_message(state), 
                    reply_markup= await home_kb.user_home_inline_button(
                        state
                    )
                )
                await state.update_data(mainMsg = mainMsg)
                await state.set_state(FSMSteps.USER_INIT_STATE)
            else:
                await bot.delete_message(
                    call.from_user.id,
                    call.message.message_id
                )
                await call.answer('Done!', show_alert=True)
        else:
            await alert_message_sender(bot, call.from_user.id)

    elif callback_data.action == 'user_transfer_claims':
        transfer_id = callback_data.id
        messageList = data.get('messageList')
        # transfer: dict = [i for i in user_event if i['id']==transfer_id][0]
        for i in user_event:
            i: dict
            if i.get('id') == transfer_id:
                transfer: dict = i
        patch_data = {
            'claims': True
        }
        response: dict = await api_gateway.patch(
            path=r.userRoutes.transactions,
            detailUrl=transfer_id,
            data=patch_data,
            exp_code=[200]
        )
        exception: bool = response.get('exception')
        if not exception:
            new_event_list: list = [i for i in user_event if i['id'] != transfer_id]
            await state.update_data(user_events = new_event_list)
            await bot.send_message(
                appSettings.botSetting.troubleStaffId,
                text=f'Пользователь не принял перевод обменника, Заявка {transfer["id"]}',
                reply_markup= await admin_kb.get_claim_contacts_toadmin(
                    call.from_user.id,
                    transfer['changer']
                )
            )
            if transfer['userProofType'] == 'photo':
                await bot.send_photo(
                    appSettings.botSetting.troubleStaffId,
                    photo= transfer['userProof'],
                    caption= f'Подтверждение пользователя. Заявка {transfer["id"]}'
                )
            elif transfer['userProofType'] == 'document':
                await bot.send_document(
                    appSettings.botSetting.troubleStaffId,
                    document= transfer['userProof'],
                    caption= f'Подтверждение пользователя. Заявка {transfer["id"]}'
                )

            if transfer['changerProofType'] == 'photo':
                await bot.send_photo(
                    appSettings.botSetting.troubleStaffId,
                    photo= transfer['changerProof'],
                    caption= f'Подтверждение обменника. Заявка {transfer["id"]}'
                )
            elif transfer['changerProofType'] == 'document':
                await bot.send_document(
                    appSettings.botSetting.troubleStaffId,
                    document= transfer['changerProof'],
                    caption= f'Подтверждение обменника. Заявка {transfer["id"]}'
                )
            try:
                await bot.delete_message(
                    call.message.chat.id,
                    call.message.message_id
                )
            except:
                pass
            await call.answer(text=msg.user_transfer_claims_message, show_alert=True)
            if not new_event_list:
                for i in messageList:
                    i: Message
                    try:
                        await bot.delete_message(
                            i.chat.id,
                            i.message_id
                        )
                    except:
                        pass
                mainMsg = await bot.send_message(
                    call.from_user.id,
                    text= await msg_maker.start_message(state),
                    reply_markup= await home_kb.user_home_inline_button(
                        state
                    )
                )
                await state.update_data(mainMsg = mainMsg)
                await state.set_state(FSMSteps.USER_INIT_STATE)
        else:
            await alert_message_sender(bot, call.from_user.id)
        




async def setup_events_handlers(dp: Dispatcher):
    '''Registry message handlers there.
    '''
    dp.callback_query.register(

        new_user_event,
        UserHomeData.filter(
        
            F.action.in_({
                'user_new_events',
                'user_transfer_accepted',
                'user_transfer_claims'
            })
        )
    )
