from aiogram.fsm.context import FSMContext
from core.middlwares.routes import r    # Dataclass whith all api routes
from core.api_actions.bot_api import SimpleAPI



async def start_message(id: int, state: FSMContext):
    '''
    '''
    data: dict = await state.get_data()
    events: list = data.get('user_events')
    changer_missed_event: list = data.get('changer_missed_event')
    insert: str = '<b>У вас новое сообщение!</b>\n\n' if events else ''
    message = (
        f'{insert}'
        'Рады приветствовать вас!\n'
        'У нас вы можете обменять валюту онлайн.\n\n'
        'Для получения справки воспользуйтесь соответствующей кнопкой ниже.'
    )

    return message



async def offer_list_msg_maker(offer: dict):

    minAmount = 'Любая' if offer['minAmount'] == None else f"{offer['minAmount']} {offer['currency']}"
    maxAmount = 'Любая' if offer['maxAmount'] == None else f"{offer['maxAmount']} {offer['currency']}"
    score_data = offer.get('owner_score')
    type_var: str = offer.get('type')
    type: str = 'Продажа' if type_var == 'sell' else 'Покупка'
    rbanks = ''
    cbanks = ''
    for rName in offer['refBanks']:
        rbanks += f'👉 {rName["name"]}\n'

    for cName in offer['currencyBanks']:
        cbanks += f'👉 {cName["name"]}\n'

    rbanks = "⚠️ Счет не назначен!" if not rbanks else rbanks
    cbanks = "⚠️ Счет не назначен!" if not cbanks else cbanks
    
    message = (
        f'⚡⚡⚡Рейтинг обменника:\n'
        f'⚡Средний сумма сделки: {score_data["avg_amount"]} MNT\n'
        f'⚡Среднее время ответа на перевод: {score_data["avg_time"]}\n'
        f'⚡Всего обменов: {score_data["total_transactions"]}\n\n'
        f'💰 <b>{type} {offer["currency"]}</b> 💰\n'
        f'💸 {offer["bannerName"]} 💸\n'
        f'💳 Банки, с которыми работает обменник:👇\n\n'
        f'{offer["currency"]}\n'
        f'{cbanks}'
        f'\nMNT:\n'
        f'{rbanks}\n\n'
        f'▶️ Минимальная сумма обмена: ⚡ {minAmount}\n'
        f'▶️ Максимальная сумма обмена: ⚡ {maxAmount}\n\n'
        f'🔥 Курс в MNT: ⚡ {offer["rate"]} \n'
    )

    return message


async def set_amount_msg_maker(offerData):

    message = f'👌 Ваш выбор принят!\n👇 Введите сумму {offerData["currency"]} которую хотите продать: 👇'

    return message


async def set_amount_returned_msg_maker(offerData):

    message = f'👇 Введите новую сумму {offerData["currency"]} которую хотите продать: 👇'

    return message


async def min_amount_error_msg_maker(offerData):

    message = f'⚠️ Вы указали сумму меньше, чем минимальная сумма\
                сделки, обозначенная обменником в данном объявлении.\
                \n\n↩ Вы можете вернуться к выбору предложений и выбрать\
                \nдругой вариант или указать сумму в пределах: \
                \n💰 от {offerData["minAmount"]} до {offerData["maxAmount"]} {offerData["currency"]}'
    
    return message


async def max_amount_error_msg_maker(offerData):

    message = f'⚠️ Вы указали сумму больше, чем максимальная сумма\
                сделки, обозначенная обменником в данном объявлении.\
                \n\n↩ Вы можете вернуться к выбору предложений и выбрать\
                \nдругой вариант или указать сумму в пределах: \
                \n💰 от {offerData["minAmount"]} до {offerData["maxAmount"]} {offerData["currency"]}'    

    return message


async def show_user_buy_amount(sellAmount, rate, currency):

    message = f'💸 Вы продаете: ⚡ {sellAmount} {currency}\
                \n💰 Вы получаете: ⚡ {round(sellAmount * rate)} MNT'
    
    return message


async def set_changer_bank(currency):

    message = f'🏦 Выберете банк, на который вам будет удобно\
                \nперевести 💸 {currency} обменнику 👇'
    
    return message


async def choose_user_bank_from_db():

    message = f'⚠️ Ранее вы указывали следующие счета для\
                \nMNT за проданную валюту. Вы можете выбрать\
                \nодин из них либо указать новый. 👇'
    
    return message


async def set_buy_bank_account(bankName):

    message = f'💰 Укажите номер вашего счета в банке\
                \n🏦 {bankName}, на который вы хотите\
                \nполучить оплату от обменника.\
                \n\n⚠️ Будьте предельно внимательны! ⚠️'
    
    return message


async def complete_set_new_bank(allData, api_gateway: SimpleAPI):

    sellAmount = allData['sellAmount']
    offerData = allData['selectedOffer']

    detailUrl = allData["changerBank"]
    response: dict = await api_gateway.get_detail(
        path=r.changerRoutes.banks,
        detailUrl=detailUrl
    )
    exception: bool = response.get('exception')
    if not exception:
        acc: list = response.get('response')

        message = f'👌 Ваши реквизиты приняты! 👌\
                    \n\n👉 Теперь выполните перевод {sellAmount} {offerData["currency"]}\
                    \nна счет обменника, по реквизитам ниже 👇\
                    \n\n🏦 Банк: {acc["name"]}\
                    \n💳 Счет: ```{acc["bankAccount"]}```\
                    \n\n⚠️ Обязательно! ⚠️\
                    \n После перевода, ответным сообщением\
                    \nпришлите скриншот / фото\
                    \nэкрана (или чек) с информацией\
                    \nо платеже ⚠️'
        
        return message



async def user_inform(amount: int, currency: str):

    message= (
        'Ваша заявка успешно зарегистрирована!\n'
        f'Ожидайте поступление {amount} {currency} '
        f'на указанные вами реквизиты'
    )
    return message



async def set_user_bank_name(currency):

    value: str = (
        '<b>Внимание!</b>\n'
        f'В настоящее время, операции по валюте {currency}'
        f'поддеживаются только с банками Монголии.\n'
    )
    alert: str = value if currency == 'USD' else ''
    
    message= (
        f'{alert}\n'
        'Вы впервые производите обмен в нашей системе, у вас нет сохранившихся счетов'
        f'🏦 Выберите название банка, куда вы ходите получить 💸 {currency}: 👇'
    )
    return message


async def enter_user_bank_name(currency):

    message = (
        f'🏦 Введите название банка, куда хотите получить 💸 {currency} '
        'от обменника: 👇'
    )
    return message


async def staff_welcome(transfers):

    # stuff_name = f'{response["name"]} {response["lastName"]}'
    value = len(transfers) if transfers else None
    alert = f'<b>У вас есть неотвеченный перевод!</b>\n\n' if value else '💰'

    message = (
        f'{alert}'
        f'💻 Добро пожаловать в личный кабинет.\n'
        f'Выберите пункт меню:\n'
        f'\n'
    )

    return message


async def stuff_offer_menu():

    message = (
        'Вы вошли в меню просмотра и редактирования ваших предложений по обмену'
    ) 
    return message


async def stuff_set_currency():

    message = (
        '💵 Выберите валюту, в которой будет размещено предложение 👇'
    )
    return message


async def stuff_show_rate(rate, currency):

    message = (
        f'💰 Вы указали курс продажи для {currency}'
        f'\n\n⚡ {rate} MNT ⚡\n\n'
        f'⚠️ Подтверждаете?'
    )
    
    return message


async def stuff_create_new_offer_banks(currency, accounts = None):

    message_mini = (
        f'💰 Выберите счет(а), которые будут использоваться\n'
        f'для перевода {currency} и MNT. Можно выбрать несколько,\n'
        'просто нажимайте на соответствующие кнопки ниже 👇'
    )

    if accounts:
        acc_input = ''

        for key, value in accounts.items():
            for i in value:
                currency = i['currency']['name']
                acc_input += f'\n⚡ {i["name"]}\n {currency} {i["bankAccount"]}\n'

        message = (
            f'💰 Выберите счет(а), которые будут\n'
            f'использоваться для перевода {currency}.\n'
            f'{acc_input}'
            '\nМожно выбрать несколько, просто\n'
            'нажимайте на соответствующие кнопки ниже 👇'
        )

    return message if accounts else message_mini


async def staff_set_min_amount(currency):

    message = (
        f'Укажите минимальную сумму {currency}\n'
        'для данного предложения'
    )

    return message


async def stuff_show_min_amount(amount, currency):

    message = (
        f'💰 Вы указали минимальную сумму\n'
        'для данного предложения'
        f'\n\n⚡ {amount} {currency} ⚡\n\n'
        f'⚠️ Подтверждаете?'
    )
    
    return message


async def stuff_set_max_amount(currency):

    message = (
        f'Укажите максимальную сумму {currency}\n'
        'для данного предложения'
    )

    return message


async def stuff_show_max_amount(amount, currency):

    message = (
        f'💰 Вы указали максимальную сумму\n'
        'для данного предложения'
        f'\n\n⚡ {amount} {currency} ⚡\n\n'
        f'⚠️ Подтверждаете?'
    )
    
    return message


async def staff_max_len_message(var):

    message = (
        f'Введеный вами комментарий имеет\n'
        f'длину более 50 символов. А именно {var}.\n'
        f'Сократите количество символов.\n'
    )

    return message


async def staff_show_offer_name(description):

    message = (
        f'Вы ввели следующее описание:\n\n'
        f'{description}\n\n'
        f'Подтверждаете?'
    )

    return message


async def staff_create_offer_show_final_text(
        post_data: dict,
        banks_accounts: dict
    ):

    minAmount = 'Любая' if post_data['minAmount'] == None else f"{post_data['minAmount']} {post_data['currency']}"
    maxAmount = 'Любая' if post_data['maxAmount'] == None else f"{post_data['maxAmount']} {post_data['currency']}"
    currency = post_data.get('currency')
    type_var: str = post_data.get('type')
    type: str = 'Продажа' if type_var == 'sell' else 'Покупка'

    rbanks = ''
    cbanks = ''
    for rName in banks_accounts['MNT']:
        rbanks += f'👉 {rName["name"]}\n'

    for cName in banks_accounts[currency]:
        cbanks += f'👉 {cName["name"]}\n'

    rbanks = "⚠️ Счет не назначен!" if not rbanks else rbanks
    cbanks = "⚠️ Счет не назначен!" if not cbanks else cbanks

    message = (

        f'💰 <b>{type} {post_data["currency"]}</b> 💰\n'
        f'💸 {post_data["bannerName"]} 💸\n'
        f'💳 Банки, с которыми работает обменник:👇\n'
        f'{post_data["currency"]}\n'
        f'{cbanks}'
        f'MNT:\n'
        f'{rbanks}\n'
        f'▶️ Минимальная сумма обмена: ⚡ {minAmount}\n'
        f'▶️ Максимальная сумма обмена: ⚡ {maxAmount}\n\n'
        f'🔥 Курс в MNT: ⚡ {post_data["rate"]} \n'
    )

    return message



async def staff_edit_offer_show(offer):

    minAmount = 'Любая' if offer['minAmount'] == None else f"{offer['minAmount']} {offer['currency']}"
    maxAmount = 'Любая' if offer['maxAmount'] == None else f"{offer['maxAmount']} {offer['currency']}"
    score_data = offer['owner_score']
    rbanks = ''
    cbanks = ''
    for rName in offer['refBanks']:
        rbanks += f'👉 {rName["name"]}\n'

    for cName in offer['currencyBanks']:
        cbanks += f'👉 {cName["name"]}\n'

    rbanks = "⚠️ Счет не назначен!" if not rbanks else rbanks
    cbanks = "⚠️ Счет не назначен!" if not cbanks else cbanks

    message = (
        f'⚡⚡⚡Рейтинг обменника:\n'
        f'⚡Средний сумма сделки: {score_data["avg_amount"]} MNT\n'
        f'⚡Среднее время ответа на перевод: {score_data["avg_time"]}\n'
        f'⚡Всего обменов: {score_data["total_transactions"]}\n\n'
        f'💰 Обмен {offer["currency"]} 💰\n'
        f'💸 {offer["bannerName"]} 💸\n'
        f'💳 Банки, с которыми работает обменник:👇\n'
        f'{offer["currency"]}\n'
        f'{cbanks}'
        f'MNT:\n'
        f'{rbanks}\n'
        f'▶️ Минимальная сумма обмена: ⚡ {minAmount}\n'
        f'▶️ Максимальная сумма обмена: ⚡ {maxAmount}\n\n'
        f'🔥 Курс в MNT: ⚡ {offer["rate"]} \n'
    )

    return message




async def staff_show_editable_banks(bank: dict):

    alert_msg = ''
    if bank.get('will_deactivate') and bank.get('isActive'):
        alert_msg = (
        'Если сделать данный счет не активным - с публикации '
        f'снимется {bank.get("will_deactivate")} предложения на обмен.'
        'Они отобразятся в разделе "Мои предложения">"Не активные"'
        )
    message = (
        f'💰 Банк {bank["name"]} 💰\n\n'
        f'💵 Валюта {bank["currency"]["name"]} 💵\n'
        f'💳 Счет ```{bank["bankAccount"]}``` 💳\n\n'
        f'{alert_msg}'
    )

    return message


async def staff_show_uncompleted_transfers(transfer):

    id = transfer['id']
    sell_cur = transfer['offerCurrency']
    sell_amount = transfer['sellAmount']
    buy_amount = transfer['buyAmount']
    rate = transfer['rate']
    type_var = transfer['type']

    type: str = 'Продажа' if type_var == 'sell' else 'Покупка'

    message = (
        '💵💵💵💵💵💵💵💵💵💵\n\n'
        f'<b>Перевод id {id}</b>\n\n'
        f'💰<b> {type} {sell_cur}</b> 💰\n'
        f'Курс {rate}\n\n'
        f'<b>Вам перевели {sell_amount} {sell_cur}</b>\n'
    )

    return message



async def staff_show_uncompleted_transfer_detail(transfer):

    id = transfer['id']
    sell_cur = transfer['offerCurrency']
    sell_amount = transfer['sellAmount']
    buy_amount = transfer['buyAmount']
    rate = transfer['rate']
    type_var = transfer['type']
    changer_bank_name = transfer['changerBank']['name']
    changer_bank_acc = transfer['changerBank']['bankAccount']
    user_bank_name = transfer['userBank']['name']
    user_bank_acc = transfer['userBank']['bankAccount']

    type: str = 'Продажа' if type_var == 'sell' else 'Покупка'

    message = (
        f'\nПеревод id {id}\n'
        f'💰<b> {type} {sell_cur}</b> 💰\n'
        f'Курс{rate} - сумма {sell_amount} {sell_cur}\n'
        f'💳 Банк, на который пользователь сделал перевод:👇\n\n'
        f'{changer_bank_name}\n'
        f'{changer_bank_acc}\n\n'
        f'Вы должны перевести ⚡ {buy_amount} MNT\n'
        f'<b>по следующим реквизитам</b> :\n\n'
        f'<b>{user_bank_name}</b>\n'
        f'<b>```{user_bank_acc}```</b>\n\n'
        '📢⚠️📢⚠️📢⚠️📢⚠️📢⚠️\n'
        '<b>После этого сразу пришлите подтверждение</b>\n'
        'в виде скриншота с платежной информацией или\n'
        'чек и нажмите появившуюся кнопку <b>"Подтвердить"!</b>\n'
        'В противном случае перевод не будет завершен\n'
        'что прямо влияет на вашу репутацию!\n'
    )

    return message



async def user_show_events(user_event: dict):

    id = user_event['id']
    sell_cur = user_event['offerCurrency']
    sell_amount = user_event['sellAmount']
    buy_amount = user_event['buyAmount']
    rate = user_event['rate']
    type_var: str = user_event.get('type')
    type: str = 'Продажа' if type_var == 'sell' else 'Покупка'

    user_bank_name = user_event['userBank']['name']
    user_bank_acc = user_event['userBank']['bankAccount']

    message = (
        f'\nПеревод id {id}\n'
        f'💰<b> {type} {sell_cur}</b> 💰\n'
        f'Курс {rate} - сумма {sell_amount} {sell_cur}\n'
        f'💳 Банк, на который обменник сделал перевод:👇\n\n'
        f'{user_bank_name}\n'
        f'```{user_bank_acc}```\n\n'
        f'Сумма: {buy_amount}\n\n'
        '📢⚠️📢⚠️📢⚠️📢⚠️📢⚠️\n'
        '<b>Убедительная просьба!</b>\n'
        'Если вы получили деньги нажмите '
        'на кнопку <b>"Подтвердить перевод"!</b>\n'
        'В противном случае перевод не будет завершен'
        'что прямо влияет на репутацию обменника!\n'
    )

    return message



async def user_max_len_message(value: int):
    message = (
        f'Введеное вами нименование имеет\n'
        f'длину более 20 символов. А именно {value}.\n'
        f'Сократите их количество.\n'
    )
    return message


async def error_set_new_bank(account: int):

    message = (
        f'К сожалению, указанный вами банковский счет '
        f'уже зарегистрирован в системе. '
        f'Вероятно вы допустили ошибку в его номере:'
        f'\n```<b>{account}</b>```\n'
        f'Если это так - просто повторите ввод еще раз.\n'
        f'Если вы уверены в правильности номера, сообщите '
        f'о возникшей ситуации администратору, он во всем разберется.'
    )

    return message