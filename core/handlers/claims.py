from datetime import datetime
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types.callback_query import CallbackQuery
from aiogram import F, Bot, Dispatcher

from core.keyboards import user_kb
from core.keyboards.callbackdata import UserExchangeData
from core.api_actions.bot_api import SimpleAPI
from core.utils import  msg_var as msg
from core.utils.bot_fsm import FSMSteps
from core.middlwares.routes import r    # Dataclass whith all api routes
from core.middlwares.settigns import appSettings
from core.utils.notifier import alert_message_sender
import asyncio


async def timeout_claims_handler(
        call: CallbackQuery,
        state: FSMContext
):
    '''
    '''
    await call.message.edit_text(
        text=msg.timeout_claims_proof_message,
        reply_markup=await user_kb.user_cancel_button()
    )
    await state.set_state(FSMSteps.USER_TIME_EXPIRED_PROOF)


async def get_user_timeout_claims_proof(
        message: Message,
        state: FSMContext,
        api_gateway: SimpleAPI,
        bot: Bot
):
    '''
    This handler get file or foto whit user proof that
    he make money transfer and create transaction on backend
    '''
    # delete user proof message from screen
    await message.delete()
    # check message type, supported only image and other
    # files. For example -pdf 
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
            message.from_user.id,
            text=msg.type_error_message
        )
        await asyncio.sleep(3)
        try:
            await del_msg.delete()
        except:
            pass
    else:
        data: dict = await state.get_data()
        selected_offer: dict = data.get('selectedOffer')
        mainMsg: Message = data.get('mainMsg')
        changerId: int = selected_offer.get('owner')
        offerId: int = selected_offer.get('id')
        changerBank: int = data.get('changerBank')
        userBank: int = data.get('userAccount')
        sellCurrency: str = selected_offer.get('currency')
        sellAmount: float = data.get('sellAmount')
        rate: float = selected_offer.get('rate')
        type: str = selected_offer.get('type')
        buyAmount: float = round(sellAmount * rate)
        accountId: int = message.from_user.id
        post_data = {
            'changer': changerId,
            'offer': offerId,
            'user': accountId,
            'changerBank_id': changerBank,
            'userBank_id': userBank,
            'offerCurrency': sellCurrency,
            'refCurrency': 'MNT',
            'sellAmount': sellAmount,
            'buyAmount': buyAmount,
            'rate': rate,
            'type': type,
            'userSendMoneyDate': datetime.now(),
            'userProofType': proofType,
            'userProof': fileId,
            'isCompleted': False,
            'claims': True,
            'changerAccepted': False
        }
        response: dict = await api_gateway.post(
            path=r.userRoutes.transactions,
            data=post_data,
            exp_code=[201]
        )
        exception: bool = response.get('exception')
        if not exception:
            # if all checks were sucsessful bot create new
            # task that will track the exchanger's response
            response_data: dict = response.get('response')
            tr_id: int = response_data.get('id')
            claim_message = (
                'Пользователь перевел деньги по истечении '
                'установленного срока. Изменились условия '
                'оффера / обменник давно офлайн\n\n'
                f'Перевод #<b>{tr_id}</b>\n'
                f'<a href="tg://user?id={changerId}">Обменник</a>\n'
                f'<a href="tg://user?id={accountId}">Пользователь</a>\n'
                f'Оффер ID: {offerId}\n'
                f'Тип оффера: {type}\n'
                f'ID банка обменника: {changerBank}\n'
                f'ID банка пользователя: {userBank}\n'
                f'Валюта оффера: {sellCurrency}\n'
                f'Сумма обменнику: {sellAmount}\n'
                f'Сумма пользователю: {buyAmount}\n'
                f'Курс оффера: {rate}\n'
            )
            if proofType == 'photo':
                await bot.send_photo(
                    appSettings.botSetting.troubleStaffId,
                    photo= fileId,
                    caption= claim_message
                )
            elif proofType == 'document':
                await bot.send_document(
                    appSettings.botSetting.troubleStaffId,
                    document= fileId,
                    caption= claim_message
                )
            await mainMsg.edit_text(
                text= msg.user_success_claims_message,
                reply_markup = await user_kb.final_transfer_stage()
            )
            await state.set_state(FSMSteps.USER_TIME_EXPIRED)

        else:
            await alert_message_sender(bot, message.from_user.id)




async def setup_claims_handlers(dp: Dispatcher):
    '''Registry message handlers there.
    '''
    dp.message.register(
        get_user_timeout_claims_proof,
        FSMSteps.USER_TIME_EXPIRED_PROOF
    )
    dp.callback_query.register(
        timeout_claims_handler,
        UserExchangeData.filter(
            F.action == 'send_money_on_expired_offer'
        ),
    )
