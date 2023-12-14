import asyncio
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher
from core.keyboards import changer_kb
from core.utils import msg_maker
from core.utils.bot_fsm import FSMSteps
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import Message
from core.middlwares.routes import r  # Dataclass whith all api routes
from core.api_actions.bot_api import SimpleAPI
from core.utils import msg_var as msg
from core.keyboards import home_kb
from create_storage import scheduler


async def changer_notifier(changer_id: int, bot: Bot, dp: Dispatcher):
    """ """
    state: FSMContext = FSMContext(
        bot=bot,
        storage=dp.storage,
        key=StorageKey(chat_id=changer_id, user_id=changer_id, bot_id=bot.id),
    )

    data: dict = await state.get_data()
    current_state: FSMSteps = await state.get_state()
    user_home_state: FSMSteps = FSMSteps.USER_INIT_STATE
    logout_time: datetime | None = data.get("logout_time")
    last_action: datetime | None = data.get("last_action")

    mainMsg: Message = data.get("mainMsg")
    uncompleted_transfers: dict = data.get("uncompleted_transfers")
    messageList: list = data.get("messageList")

    if not logout_time:
        if uncompleted_transfers and current_state == FSMSteps.STAFF_HOME_STATE:
            try:
                await bot.delete_message(mainMsg.chat.id, mainMsg.message_id)
            except:
                pass

            alertMsg: Message = await bot.send_message(
                mainMsg.chat.id,
                text=await msg_maker.staff_welcome(uncompleted_transfers),
                reply_markup=await changer_kb.staff_welcome_button(
                    uncompleted_transfers
                ),
            )
            await state.update_data(mainMsg=alertMsg)

        elif not uncompleted_transfers:
            changer_notifier_id = f"changer_notifier-{changer_id}"
            scheduler.remove_job(changer_notifier_id)

    elif isinstance(logout_time, datetime):
        logout_delta: timedelta = datetime.now() - logout_time

        if uncompleted_transfers:
            action_delta: timedelta = datetime.now() - last_action

            if current_state == user_home_state:
                if messageList:
                    for i in messageList:
                        i: Message
                        try:
                            await bot.delete_message(i.chat.id, i.message_id)
                        except:
                            pass
                try:
                    await bot.delete_message(mainMsg.chat.id, mainMsg.message_id)
                except:
                    pass
                mainMsg: Message = await bot.send_message(
                    changer_id,
                    text=await msg_maker.start_message(state),
                    reply_markup=await home_kb.user_home_inline_button(state),
                )
                await state.update_data(mainMsg=mainMsg)
            elif (
                current_state == FSMSteps.USER_CHANGE_STATE
            ):  # add state to change process!!!
                if messageList:
                    for i in messageList:
                        i: Message
                        try:
                            await bot.delete_message(i.chat.id, i.message_id)
                        except:
                            pass
                if mainMsg:
                    try:
                        await bot.delete_message(mainMsg.chat.id, mainMsg.message_id)
                    except:
                        pass
                mainMsg: Message = await bot.send_message(
                    changer_id,
                    text=await msg_maker.start_message(state),
                    reply_markup=await home_kb.user_home_inline_button(state),
                )
                await state.update_data(mainMsg=mainMsg)

            else:
                if (
                    current_state == FSMSteps.SET_AMOUNT_STATE
                    or current_state == FSMSteps.USER_ENTER_BANK_NAME
                    or current_state == FSMSteps.SET_BUY_BANK_ACCOUNT
                ):
                    if action_delta.total_seconds() > 180:
                        try:
                            await mainMsg.delete()
                        except:
                            pass
                        mainMsg: Message = bot.send_message(
                            changer_id,
                            text=await msg_maker.start_message(state),
                            reply_markup=await home_kb.user_home_inline_button(state),
                        )
                        await state.update_data(mainMsg=mainMsg)
                        await state.set_state(user_home_state)

                elif current_state == FSMSteps.GET_USER_PROOF:  # add more checks!!
                    if action_delta.total_seconds() > 600:
                        try:
                            await mainMsg.delete()
                        except:
                            pass
                        mainMsg: Message = bot.send_message(
                            changer_id,
                            text=await msg_maker.start_message(state),
                            reply_markup=await home_kb.user_home_inline_button(state),
                        )
                        await state.update_data(mainMsg=mainMsg)
                        await state.set_state(user_home_state)
        elif logout_delta.total_seconds() > 60 and not uncompleted_transfers:
            try:
                scheduler.remove_job(f"changer_notifier-{changer_id}")
            except:
                pass


async def transfers_getter_changer(
    changer_id: int, bot: Bot, dp: Dispatcher, api_gateway: SimpleAPI
):
    """ """
    state: FSMContext = FSMContext(
        bot=bot,
        storage=dp.storage,
        key=StorageKey(chat_id=changer_id, user_id=changer_id, bot_id=bot.id),
    )
    params = {
        "changer": changer_id,
        "claims": False,
        "isCompleted": False,
        "changerAccepted": False,
    }
    response: dict = await api_gateway.get(
        path=r.changerRoutes.transactions, params=params, exp_code=[200]
    )
    exception: bool = response.get("exception")
    if not exception:
        new_user_transfers: dict = response.get("response")
        data: dict = await state.get_data()
        transfers: list = data.get("uncompleted_transfers")
        mainMsg: Message = data.get("mainMsg")
        current_state: FSMSteps = await state.get_state()
        staff_home_state: FSMSteps = FSMSteps.STAFF_HOME_STATE
        logout_time: datetime | int = data.get("logout_time")

        if not new_user_transfers:
            await state.update_data(uncompleted_transfers=new_user_transfers)

        if transfers != new_user_transfers:
            await state.update_data(uncompleted_transfers=new_user_transfers)
            if current_state == staff_home_state and not logout_time:
                try:
                    await bot.delete_message(mainMsg.chat.id, mainMsg.message_id)
                except:
                    pass
                alert_tr: list = new_user_transfers
                alertMsg: Message = await bot.send_message(
                    mainMsg.chat.id,
                    text=await msg_maker.staff_welcome(alert_tr),
                    reply_markup=await changer_kb.staff_welcome_button(alert_tr),
                )
                await state.update_data(mainMsg=alertMsg)

            changer_notifier_id = f"changer_notifier-{changer_id}"
            job_list: list = scheduler.get_jobs()
            job_id_list: list = [job.id for job in job_list]
            if changer_notifier_id not in job_id_list:
                scheduler.add_job(
                    changer_notifier,
                    "interval",
                    minutes=2,
                    id=changer_notifier_id,
                    kwargs={
                        "changer_id": changer_id,
                    },
                )
        if isinstance(logout_time, datetime):
            logout_delta: timedelta = datetime.now() - logout_time
            if logout_delta.total_seconds() > 1800 and not transfers:
                try:
                    scheduler.remove_job(f"changer_getter-{changer_id}")
                except:
                    pass


async def transfers_getter_user(
    user_id: int, bot: Bot, dp: Dispatcher, api_gateway: SimpleAPI
):
    """ """
    state: FSMContext = FSMContext(
        bot=bot,
        storage=dp.storage,
        key=StorageKey(chat_id=user_id, user_id=user_id, bot_id=bot.id),
    )
    params = {
        "user": user_id,
        "claims": False,
        "isCompleted": False,
        "changerAccepted": True,
    }
    response: dict = await api_gateway.get(
        path=r.userRoutes.transactions, params=params, exp_code=[200]
    )
    exception: bool = response.get("exception")
    new_events: dict = response.get("response")
    if not exception:
        data: dict = await state.get_data()
        user_events: dict = data.get("user_events")
        current_state = await state.get_state()
        mainMsg: Message = data.get("mainMsg")

        if user_events != new_events and new_events:
            await state.update_data(user_events=new_events)

            if current_state == FSMSteps.USER_INIT_STATE or \
                current_state == FSMSteps.USER_WAIT_INCOME_TR:
                try:
                    await bot.delete_message(mainMsg.chat.id, mainMsg.message_id)
                except:
                    pass

                alertMsg: Message = await bot.send_message(
                    mainMsg.chat.id,
                    text=await msg_maker.start_message(state),
                    reply_markup=await home_kb.user_home_inline_button(state),
                )
                await state.update_data(mainMsg=alertMsg)
                await state.set_state(FSMSteps.USER_INIT_STATE)

        elif not new_events:
            params = {
                "user": user_id,
                "claims": False,
                "isCompleted": False,
                "changerAccepted": False,
            }
            response: dict = await api_gateway.get(
                path=r.userRoutes.transactions, params=params, exp_code=[200]
            )
            exception: bool = response.get("exception")
            response_data: dict = response.get("response")
            if not response_data and not exception:
                scheduler.remove_job(f"user_getter-{user_id}")


async def main_msg_updater(bot: Bot, dp: Dispatcher, api_gateway: SimpleAPI):
    """ """
    response: dict = await api_gateway.get(path=r.homeRoutes.userInit)
    exception: bool = response.get("exception")
    if not exception:
        id_list: list = response.get("response")

        for id in id_list:
            state: FSMContext = FSMContext(
                bot=bot,
                storage=dp.storage,
                key=StorageKey(chat_id=id, user_id=id, bot_id=bot.id),
            )
            data: dict = await state.get_data()
            mainMsg: Message = data.get("mainMsg")

            try:
                await bot.delete_message(mainMsg.chat.id, mainMsg.message_id)
            except:
                pass

            else:
                mainMsg = await bot.send_message(
                    id,
                    text=mainMsg.text,
                    reply_markup=mainMsg.reply_markup,
                    disable_notification=True,
                )
                await state.update_data(mainMsg=mainMsg)


async def alert_message_sender(bot: Bot, user_id: int):
    """ """
    alert: Message = await bot.send_message(user_id, text=msg.error_msg)
    await asyncio.sleep(3)
    try:
        await bot.delete_message(alert.chat.id, alert.message_id)
    except:
        pass
