import asyncio
from datetime import datetime

from aiogram.fsm.context import FSMContext
from aiogram.types.callback_query import CallbackQuery
from aiogram.types import Message
from aiogram import F, Bot, Dispatcher

from core.middlwares.routes import r    # Dataclass whith all api routes
from core.utils import msg_maker
from core.api_actions.bot_api import SimpleAPI
from core.middlwares.settigns import appSettings
from core.utils.bot_fsm import FSMSteps
from core.utils import msg_var as msg
from core.keyboards import (
    changer_kb,
    admin_kb
)
from core.keyboards.callbackdata import (
    StaffEditData,
    StaffOfficeData,
)
from core.utils.notifier import alert_message_sender



async def staff_show_transfers(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: StaffEditData,
        bot: Bot
):
    '''
    '''
    await state.set_state(FSMSteps.STAFF_TRANSFRES)
    data: dict = await state.get_data()
    uncompleted_transfers: list = data.get('uncompleted_transfers')

    # if not uncompleted_transfers:

    #     params = {
    #         'changer': call.from_user.id,
    #         'claims': False,
    #         'isCompleted': False,
    #         'changerAcceptDate': None
    #     }
    #     response = await SimpleAPI.get(
    #         r.changerRoutes.transactions,
    #         params=params
    #     )
    #     uncompleted_transfers = response.json()
    #     await state.update_data(uncompleted_transfers = uncompleted_transfers)

    if uncompleted_transfers:

        await call.message.delete()
        messageList = []

        for tr in uncompleted_transfers:

            self_msg = await bot.send_message(
                call.from_user.id,
                text = await msg_maker.staff_show_uncompleted_transfers(tr),
                reply_markup = await changer_kb.staff_show_transfers(tr['id'])
            )
            messageList.append(self_msg)

        sep_msg = await bot.send_message(
            call.from_user.id,
            text = msg.separator,
            reply_markup = await changer_kb.sfuff_cancel_button()
        )
        messageList.append(sep_msg)        
        await state.update_data(messageList = messageList)

    if not uncompleted_transfers:                    # проверить корректность! 
        await call.message.edit_text(
            text = msg.staff_empty_uncompleted_transfers,
            reply_markup = await changer_kb.sfuff_cancel_button()
        )



async def staff_show_transfer_detail(
        call: CallbackQuery,
        state: FSMContext,
        callback_data: StaffEditData,
        api_gateway: SimpleAPI,
        bot: Bot
):
    '''
    '''
    data: dict = await state.get_data()
    tr_id: int = callback_data.id
    transfers: list = data.get('uncompleted_transfers')
    # transfer_detail = [i for i in transfers if i['id']==tr_id]     # !!!!!!!!!!!
    messageList: list = data.get('messageList')
    await state.update_data(ansvered_transfer_id = tr_id)
    for i in transfers:
        i: dict
        if i.get('id') == tr_id:
            transfer_detail: dict = i

    if callback_data.action == 'staff_transfers_get_detail':
                
        if messageList:

            for i in messageList:
                i: Message

                try:
                    await bot.delete_message(
                        i.chat.id,
                        i.message_id
                    )
                except:
                    pass
            await state.update_data(messageList = [])

        if transfer_detail['userProofType'] == 'photo':

            mainMsg = await bot.send_photo(
                call.from_user.id,
                photo = transfer_detail['userProof'],
                caption = await msg_maker.staff_show_uncompleted_transfer_detail(transfer_detail),
                reply_markup = await changer_kb.staff_show_transfer_detail_none_next(tr_id),
                parse_mode='MARKDOWN',

            )
            await state.update_data(mainMsg = mainMsg)

        elif transfer_detail['userProofType'] == 'document':

            mainMsg = await bot.send_document(
                call.from_user.id,
                document = transfer_detail['userProof'],
                caption = await msg_maker.staff_show_uncompleted_transfer_detail(transfer_detail),
                reply_markup = await changer_kb.staff_show_transfer_detail_none_next(tr_id),
                parse_mode='MARKDOWN',
            )
            await state.update_data(mainMsg = mainMsg)

        await state.set_state(FSMSteps.STAFF_TRANSFERS_PROOF)


    elif callback_data.action == 'staff_transfer_claims':

        patch_data = {
            'claims': True
        }
        response: dict = await api_gateway.patch(
            path=r.changerRoutes.transactions,
            detailUrl=tr_id,
            data=patch_data,
            exp_code=[200]
        )
        exception: bool = response.get('exception')
        if not exception:
            new_list = [i for i in transfers if i['id']!=tr_id]
            await state.update_data(uncompleted_transfers = new_list)
            await bot.send_message(
                appSettings.botSetting.troubleStaffId,
                text=f'Обменник не принял перевод пользователя, Заявка {tr_id}',
                reply_markup= await admin_kb.get_claim_contacts_toadmin(
                    transfer_detail['user'],
                    call.from_user.id
                ),
            )
            if transfer_detail['userProofType'] == 'photo':
                await bot.send_photo(
                    appSettings.botSetting.troubleStaffId,
                    photo= transfer_detail['userProof'],
                    caption= f'Подтверждение пользователя. Заявка {tr_id}'
                )
            elif transfer_detail['userProofType'] == 'document':
                await bot.send_document(
                    appSettings.botSetting.troubleStaffId,
                    document= transfer_detail['userProof'],
                    caption= f'Подтверждение пользователя. Заявка {tr_id}'
                )
            await call.message.delete()

            mainMsg = await bot.send_message(
                call.from_user.id,
                text = msg.staff_transfer_claims_message,
                reply_markup= await changer_kb.sfuff_cancel_button()
            )
            await state.update_data(mainMsg = mainMsg)
            await state.set_state(FSMSteps.STUFF_INIT_STATE)
        else:
            await alert_message_sender(bot, call.from_user.id)

    elif callback_data.action == 'staff_transfer_accepted':

        proof_type = data.get('proof_type')
        proof_id = data.get('proof_id')

        patch_data = {
            'changerSendMoneyDate': datetime.now(),
            'changerAcceptDate': datetime.now(),
            'changerProofType': proof_type,
            'changerProof': proof_id,
            'changerAccepted': True
        }

        response: dict = await api_gateway.patch(
            path=r.changerRoutes.transactions,
            detailUrl=tr_id,
            data=patch_data,
            exp_code=[200]
        )
        exception: bool = response.get('exception')
        if not exception:
            new_list = [i for i in transfers if i['id'] != tr_id]
            await state.update_data(uncompleted_transfers = new_list)
            try:
                await bot.delete_message(
                    call.message.chat.id,
                    call.message.message_id
                )
            except:
                pass

            mainMsg = await bot.send_message(
                call.from_user.id,
                text = msg.staff_transfer_accept_success,
                reply_markup= await changer_kb.sfuff_cancel_button()
            )
            await state.update_data(mainMsg = mainMsg)
        else:
            await alert_message_sender(bot, call.from_user.id)



async def staff_transfer_proof_getter(message: Message, state: FSMContext, bot: Bot):
    '''
    '''
    await message.delete()
    data: dict = await state.get_data()
    mainMsg: Message = data.get('mainMsg')
    transfer_id: int = data.get('ansvered_transfer_id')
    try:
        if message.photo:
            fileId = message.photo[-1].file_id
            proofType = 'photo'
        elif message.document:
            fileId = message.document.file_id
            proofType = 'document'
        else:
            raise TypeError()
    except TypeError:
        # inform user about error and delete this message
        # after 3 seconds 
        del_msg: Message = await bot.send_message(
            text=msg.type_error_message
        )
        await asyncio.sleep(3)
        try:
            await del_msg.delete()
        except:
            pass
    else:
        await mainMsg.edit_reply_markup(
            reply_markup = await changer_kb.staff_show_transfer_detail_accept(
                transfer_id
            )
        )
        await state.update_data(proof_type = proofType)
        await state.update_data(proof_id = fileId)

        del_msg = await bot.send_message(
            message.from_user.id,
            text = msg.staff_get_proof_success
        )
        await asyncio.sleep(3)
        try:
            await del_msg.delete()
        except:
            pass

        await state.set_state(FSMSteps.STAFF_TRANSFRES)




async def setup_exchange_handlers(dp: Dispatcher):
    '''Register callback_querry handlers there.
    '''
    dp.message.register(

        staff_transfer_proof_getter,
        FSMSteps.STAFF_TRANSFERS_PROOF,
        # F.content_type.in_({'photo', 'document'})

    )
    dp.callback_query.register(

        staff_show_transfers,
        StaffOfficeData.filter(
            
            F.action.in_({
                'staff_show_transfers',
                'changer_missed_events'
            })
        )
    )
    dp.callback_query.register(

        staff_show_transfer_detail,
        StaffEditData.filter(
        
            F.action.in_({
              'staff_transfers_get_detail',
              'staff_transfer_claims',
              'staff_transfer_accepted'
            })
        )
    )