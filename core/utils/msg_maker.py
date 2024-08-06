from aiogram.fsm.context import FSMContext
from core.middlwares.routes import r    # Dataclass whith all api routes
from core.api_actions.bot_api import SimpleAPI
from core.utils.notifier import alert_message_sender



async def start_message(state: FSMContext):
    '''
    '''
    data: dict = await state.get_data()
    events: list = data.get('user_events')
    uncompleted_transfers: list = data.get('uncompleted_transfers')
    cr_orders: list = data.get("cr_orders")
    insert: str = '<b>У вас новое сообщение!</b> ✉\n\n' if events else ''

    new_order_exists = 0
    if uncompleted_transfers:
        new_order_exists += len(uncompleted_transfers)
    if cr_orders:
        new_order_exists += len(cr_orders)
    
    if new_order_exists:
        message = (
            '⚠️ <b>У вас пропущенный входящий перевод!</b>\n\n'
            '<b>Нажмите кнопку ниже чтобы ответить.</b>'
        )
    else:
        message = (
            f'{insert}'
            '📝 <b>Вы находитесь в главном меню.</b>\n'
            'Если вы впервые пользуетесь данным ботом - то '
            'настоятельно рекомедуем вам воспользоваться справкой перед '
            'совершением обмена.\n\n'
            'Выберите соответствующий пункт меню:'
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
        if rName['isDeleted'] == True or rName['isActive'] == False:
            continue
        rbanks += f'🔹 {rName["name"]}\n'

    for cName in offer['currencyBanks']:
        if cName['isDeleted'] == True or cName['isActive'] == False:
            continue
        cbanks += f'🔹 {cName["name"]}\n'

    rbanks = "⚠️ Счет не назначен!" if not rbanks else rbanks
    cbanks = "⚠️ Счет не назначен!" if not cbanks else cbanks
    
    message = (
        f'✅ <b>Рейтинг обменника:</b>\n'
        f'🔹Средняя сумма сделки: {score_data["avg_amount"]} MNT\n'
        f'🔹Среднее время ответа на перевод: {score_data["avg_time"]}\n'
        f'🔹Всего обменов: {score_data["total_transactions"]}\n\n'
        f'💸 <b>{offer["bannerName"]}</b> 💸\n'
        f'💰 <b>{type} {offer["currency"]}</b> 💰\n'
        f'💳 Банки, с которыми работает обменник:\n\n'
        f'{offer["currency"]}\n'
        f'{cbanks}'
        f'\nMNT:\n'
        f'{rbanks}\n'
        f'▶️ Минимальная сумма обмена: ⚡ {minAmount}\n'
        f'▶️ Максимальная сумма обмена: ⚡ {maxAmount}\n\n'
        f'🔥 Курс в MNT:<b> {offer["rate"]}</b>\n'
    )

    return message


async def set_amount_msg_maker(offerData):

    message = (
        f'✅ Ваш выбор принят!\n\n'
        '<b>Дорогие пользователи!</b>\n'
        'Обменники могут корректировать курс валют до нескольких раз '
        'в день, поэтому условия по выбранному предложению действительны 20 минут.\n\n'
        f'💵 <b>Введите сумму {offerData["currency"]} для обмена:</b>'
        )
        

    return message


async def set_amount_returned_msg_maker(offerData):

    message = f'🔹 Введите новую сумму {offerData["currency"]} которую хотите продать:'

    return message


async def min_amount_error_msg_maker(offerData):

    message = (
        '⚠️ Вы указали сумму меньше, чем минимальная сумма '
        'сделки, обозначенная обменником в данном объявлении.\n\n'
        '↩ Вы можете вернуться к выбору предложений и выбрать '
        'другой вариант или указать сумму в пределах:\n\n'
        f'💰 от <b>{offerData["minAmount"]}</b> до <b>{offerData["maxAmount"]} {offerData["currency"]}</b>'
    )
    return message


async def max_amount_error_msg_maker(offerData):

    message = (
        '⚠️ Вы указали сумму больше, чем максимальная сумма '
        'сделки, обозначенная обменником в данном объявлении.\n\n'
        '↩ Вы можете вернуться к выбору предложений и выбрать '
        'другой вариант или указать сумму в пределах:\n\n'
        f'💰 от <b>{offerData["minAmount"]}</b> до <b>{offerData["maxAmount"]} {offerData["currency"]}</b>'
    )
    return message


async def show_user_buy_amount(sellAmount, rate, currency, type):

    message_buy =(
        f'💸 Вы продаете: ⚡ {sellAmount} {currency}\n'
        f'💰 Вы получаете: ⚡ {round(sellAmount * rate)} MNT'
    )
   
    message_sell =(
        f'💸 Вы покупаете: ⚡ {sellAmount} {currency}\n'
        f'💰 Вы заплатите: ⚡ {round(sellAmount * rate)} MNT'
    )    
    return message_buy if type == 'buy' else message_sell


async def set_changer_bank(currency):

    message = (
        '<b>Дорогие пользователи!</b> Обращаем ваше внимание на то, '
        'что имя отправителя и имя получателя должны совпадать, '
        'иначе обменник может вернуть перевод отправителю с вычетом комиссии банка\n\n'
        '🏦 Выберите банк, на который вам будет удобно '
        f'перевести 💸 {currency} обменнику 👇'
    )    
    return message


async def choose_user_bank_from_db(currency):

    message = (
        '<b>Дорогие пользователи!</b> Обращаем ваше внимание на то, '
        'что имя отправителя и имя получателя должны совпадать, '
        'иначе обменник может вернуть перевод отправителю с вычетом комиссии банка\n\n'
        f'✅ Ранее вы указывали следующие счета для работы с {currency}. '
        'Вы можете выбрать один из них, либо указать новый. ⬇'
    )
    return message


async def set_buy_bank_account(bankName, currency, type):

    account = 'вашей карты' if currency=='RUB' and type=='sell' else 'вашего счета' 

    message = (
        f'✅ Укажите номер {account} в банке '
        f'🏦 {bankName}, для получения '
        'перевода от обменника.\n\n'
        '⚠️ <b>Будьте предельно внимательны!</b> ⚠️'
    )
    return message


async def complete_set_new_bank(allData: dict, api_gateway: SimpleAPI):

    sellAmount: float = allData.get('sellAmount')
    offerData: dict = allData.get('selectedOffer')
    rate: float = offerData.get('rate')
    type: str = offerData.get('type')
    buyAmount: float = round(sellAmount * rate)
    type: str = offerData.get('type')
    currency: str = offerData.get('currency')
    curr: str = 'MNT' if type == 'sell' else currency
    amount: int = sellAmount if type == 'buy' else buyAmount
    offer_type: str = offerData.get('type')
    acc_type: str = 'Карта №:' if curr=='RUB' and offer_type=='buy' else 'Счет №:'

    detailUrl = allData["changerBank"]
    response: dict = await api_gateway.get_detail(
        path=r.changerRoutes.banks,
        detailUrl=detailUrl
    )
    exception: bool = response.get('exception')
    if not exception:
        acc: list = response.get('response')

        message = (
            '✅ <b>Реквизиты приняты!</b>\n'
            f'👉 Выполните перевод {amount} {curr} '
            'на счет обменника, по реквизитам ниже:\n\n'
            f'🏦 Банк: {acc["name"]}\n'
            f'💳 {acc_type} <code>{acc["bankAccount"]}</code>\n\n'
            '⚠️ <b>Обязательно!</b>⚠️\n'
            'После перевода, ответным сообщением '
            'пришлите <b>скриншот или чек</b> с информацией о платеже'
        )
        return message


async def user_inform(amount: int, currency: str):

    message= (
        '✅ <b>Ваша заявка успешно зарегистрирована!</b>\n'
        f'Ожидайте поступление 💵 {amount} {currency} '
        'на указанные вами реквизиты.'
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
        'Вы впервые производите обмен в нашей системе, у вас нет сохранившихся счетов.\n'
        f'🏦 Выберите название банка, куда вы хотите получить 💸 {currency}: 👇'
    )
    return message


async def enter_user_bank_name(currency):

    message = (
        f'🏦 Введите название банка, куда хотите получить 💸 {currency} '
        'от обменника:'
    )
    return message


async def final_step_timeout_message():

    message = (
        '<b>Мы сожалеем, но 20 минут уже пошли..</b>\n'
        'Условия по данному предложению поменялись, '
        'и заявку необходимо оформить заново.\n\n'
        '<b>Если вы перевели деньги</b>, то свяжитесь с администратором '
        'по кнопке ниже, он вам обязательно поможет.'
    )
    return message


async def timeout_message():
    message = (
        '<b>Мы сожалеем, но 20 минут уже пошли..</b>\n'
        'Условия по данному предложению поменялись, '
        'и заявку необходимо оформить заново.\n\n'
    )
    return message



async def staff_welcome(state):
    data: dict = await state.get_data()
    # stuff_name = f'{response["name"]} {response["lastName"]}'
    uncompleted_transfers: list = data.get('uncompleted_transfers')
    cr_orders: list = data.get("cr_orders")

    new_order_exists = 0
    if uncompleted_transfers:
        new_order_exists += len(uncompleted_transfers)
    if cr_orders:
        new_order_exists += len(cr_orders)

    alert = f'<b>У вас есть неотвеченный перевод!</b>\n\n' if new_order_exists else '💰'

    message = (
        f'{alert}'
        '💻 Вы находитесь в главном меню личного кабинета.\n\n'
        '<b>Выберите действие:</b>'
    )

    return message


async def stuff_offer_menu():

    message = (
        '✅ Вы вошли в меню просмотра и редактирования ваших предложений по обмену.\n\n'
        '<b>Выберите действие:</b>'
    ) 
    return message


async def stuff_set_currency():

    message = (
        '💵 Выберите валюту, в которой будет размещено предложение 👇'
    )
    return message


async def stuff_show_rate(rate, currency):

    message = (
        f'✅ Вы указали курс продажи для {currency}'
        f'\n\n⚡<b> {rate} MNT </b>⚡\n\n'
        f'⚠️ Подтверждаете?'
    )
    
    return message


async def stuff_create_new_offer_banks(currency, accounts = None):

    message_mini = (
        '✅ Выберите счет(а), которые будут использоваться '
        f'для перевода {currency} и MNT. <b>Можно выбрать несколько</b>, '
        'просто нажимайте на соответствующие кнопки ниже ⬇'
    )

    if accounts:
        acc_input = ''

        for key, value in accounts.items():
            for i in value:
                currency = i['currency']['name']
                acc_input += f'\n🔹 {i["name"]}\n {currency} {i["bankAccount"]}\n'

        message = (
            '✅ Выберите счет(а), которые будут '
            f'использоваться для перевода {currency} и MNT.\n'
            f'{acc_input}'
            '\n<b>Можно выбрать несколько</b>, просто '
            'нажимайте на соответствующие кнопки ниже ⬇'
        )

    return message if accounts else message_mini


async def staff_set_min_amount(currency):

    message = (
        f'✅ Укажите минимальную сумму {currency} '
        'для данного предложения'
    )

    return message


async def stuff_show_min_amount(amount, currency):

    message = (
        '✅ Вы указали <b>минимальную сумму</b> '
        'сделки для данного предложения'
        f'\n\n🔹 {amount} {currency}\n\n'
        f'⚠️ Подтверждаете?'
    )
    
    return message


async def stuff_set_max_amount(currency):

    message = (
        f'✅ Укажите максимальную сумму {currency} '
        'для данного предложения'
    )

    return message


async def stuff_show_max_amount(amount, currency):

    message = (
        f'✅ Вы указали <b>максимальную сумму</b> '
        'для данного предложения'
        f'\n\n🔹 {amount} {currency}\n\n'
        f'⚠️ Подтверждаете?'
    )
    
    return message


async def staff_max_len_message(var):

    message = (
        '⚠️ Введеный вами комментарий имеет '
        f'длину более 50 символов. А именно {var}.\n\n'
        '<b>Сократите количество символов.</b>'
    )

    return message


async def staff_show_offer_name(description):

    message = (
        f'✅ <b>Вы ввели следующее описание:</b>\n\n'
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
        rbanks += f'🔹 {rName["name"]}\n'

    for cName in banks_accounts[currency]:
        cbanks += f'🔹 {cName["name"]}\n'

    rbanks = "⚠️ Счет не назначен!" if not rbanks else rbanks
    cbanks = "⚠️ Счет не назначен!" if not cbanks else cbanks

    message = (
        f'💸 <b>{post_data["bannerName"]}</b> 💸\n'
        f'💰 <b>{type} {post_data["currency"]}</b> 💰\n'
        f'💳 Банки, с которыми работает обменник:👇\n\n'
        f'{post_data["currency"]}\n'
        f'{cbanks}'
        f'MNT:\n'
        f'{rbanks}\n'
        f'▶️ Минимальная сумма обмена: ⚡ {minAmount}\n'
        f'▶️ Максимальная сумма обмена: ⚡ {maxAmount}\n\n'
        f'🔥 Курс в MNT: <b>{post_data["rate"]}</b>\n'
    )
    return message



async def staff_edit_offer_show(offer: dict):

    minAmount = 'Любая' if offer['minAmount'] == None else f"{offer['minAmount']} {offer['currency']}"
    maxAmount = 'Любая' if offer['maxAmount'] == None else f"{offer['maxAmount']} {offer['currency']}"
    score_data = offer['owner_score']
    type_var: str = offer.get('type')
    type: str = 'Продажа' if type_var == 'sell' else 'Покупка'
    rbanks = ''
    cbanks = ''
    for rName in offer['refBanks']:
        if rName['isDeleted'] == True or rName['isActive'] == False:
            continue
        rbanks += f'👉 {rName["name"]}\n'

    for cName in offer['currencyBanks']:
        if cName['isDeleted'] == True or cName['isActive'] == False:
            continue
        cbanks += f'👉 {cName["name"]}\n'

    rbanks = "⚠️ Счет не назначен!" if not rbanks else rbanks
    cbanks = "⚠️ Счет не назначен!" if not cbanks else cbanks

    message = (
        f'✅ <b>Рейтинг обменника:</b>\n'
        f'🔹Средняя сумма сделки: {score_data["avg_amount"]} MNT\n'
        f'🔹Среднее время ответа на перевод: {score_data["avg_time"]}\n'
        f'🔹Всего обменов: {score_data["total_transactions"]}\n\n'
        f'💸 <b>{offer["bannerName"]}</b> 💸\n'
        f'💰 <b>{type} {offer["currency"]}</b> 💰\n'
        f'💳 Банки, с которыми работает обменник:\n\n'
        f'{offer["currency"]}\n'
        f'{cbanks}'
        f'\nMNT:\n'
        f'{rbanks}\n'
        f'▶️ Минимальная сумма обмена: ⚡ {minAmount}\n'
        f'▶️ Максимальная сумма обмена: ⚡ {maxAmount}\n\n'
        f'🔥 Курс в MNT:<b> {offer["rate"]}</b>\n'
    )
    return message




async def staff_show_editable_banks(bank: dict):

    currency = bank["currency"]["name"]
    account_type = 'Карта №:' if currency=='RUB' else 'Счет №:'
    alert_msg = ''
    if bank.get('will_deactivate') and bank.get('isActive'):
        alert_msg = (
        'Если сделать данный счет не активным - с публикации '
        f'снимется {bank.get("will_deactivate")} предложения на обмен. '
        'Они отобразятся в разделе <b>Мои предложения</b> > <b>Не активные</b>'
        )
    
    message = (
        f'💰 <b>Банк {bank["name"]}</b>\n\n'
        f'💵 Валюта {currency}\n'
        f'💳 {account_type} <code>{bank["bankAccount"]}</code>\n\n'
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

    curr: str = 'MNT' if type_var == 'sell' else sell_cur
    amount: int = buy_amount if type_var == 'sell' else sell_amount

    message = (
        '✅ <b>Новый перевод!</b>\n\n'
        f'🔹 <b>ID {id}</b>\n'
        f'🔹 <b>{type} {sell_cur}</b>\n'
        f'🔹 Курс {rate}\n\n'
        f'🔹 <b>Вам перевели {amount} {curr}</b>\n'
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
    curr: str = 'MNT' if type_var == 'buy' else sell_cur
    amount: int = buy_amount if type_var == 'buy' else sell_amount
    acc_type: str = 'Карта №:' if curr=='RUB' and type_var == 'sell' else 'Счет №:'

    message = (
        f'✅ <b>Перевод ID {id}</b>\n'
        f'💰<b> {type} {sell_cur}</b> 💰\n'
        f'🔹 Курс{rate} - сумма {sell_amount} {sell_cur}\n'
        f'💳 Банк, на который пользователь сделал перевод:\n\n'
        f'{changer_bank_name}\n'
        f'<code>{changer_bank_acc}</code>\n\n'
        f'<b>Вы должны перевести {amount} {curr}</b>\n'
        f'<b>по следующим реквизитам</b> :\n\n'
        f'<b>{user_bank_name}</b>\n'
        f'{acc_type}'
        f'<code>{user_bank_acc}</code>\n\n'
        '📢⚠️📢⚠️📢⚠️📢⚠️📢⚠️\n'
        '<b>После этого сразу пришлите подтверждение</b> '
        'в виде скриншота с платежной информацией или '
        'чека и нажмите появившуюся кнопку <b>Подтвердить</b>!\n\n'
        'В противном случае перевод не будет завершен '
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
    curr: str = 'MNT' if type_var == 'buy' else sell_cur
    amount: int = buy_amount if type_var == 'buy' else sell_amount

    message = (
        f'\nПеревод id {id}\n'
        f'💰<b> {type} {sell_cur}</b> 💰\n'
        f'Курс {rate} - сумма {sell_amount} {sell_cur}\n'
        f'💳 Банк, на который обменник сделал перевод:👇\n\n'
        f'{user_bank_name}\n'
        f'<code>{user_bank_acc}</code>\n\n'
        f'Сумма: {amount} {curr}\n\n'
        '📢⚠️📢⚠️📢⚠️📢⚠️📢⚠️\n'
        '<b>Убедительная просьба!</b>\n'
        'Если вы получили деньги нажмите '
        'на кнопку <b>Подтвердить перевод</b>!\n\n'
        'В противном случае перевод не будет завершен, '
        'что прямо влияет на рейтинг обменника!\n'
    )

    return message



async def user_max_len_message(value: int):
    message = (
        '⚠️ Введеное вами нименование имеет '
        f'длину более 20 символов. А именно {value}.\n\n'
        '<b>Сократите их количество.</b>'
    )
    return message


async def error_set_new_bank(account: int):

    message = (
        f'⚠️ К сожалению, указанный вами банковский счет '
        f'уже зарегистрирован в системе. '
        f'Вероятно вы допустили ошибку в его номере:'
        f'\n<code>{account}</code>\n'
        f'Если это так - просто повторите ввод еще раз. '
        f'Если вы уверены в правильности номера, сообщите '
        f'о возникшей ситуации администратору, он во всем разберется.'
    )

    return message


async def rate_message_maker(response_data):
    message = response_data[0].get('text')
    return message



# cryptocurrency place ------------




async def set_cr_amount_msg_maker(choosen_pair):

    message = (
        f'✅ Ваш выбор принят!\n\n'
        '<b>Дорогие пользователи!</b>\n'
        'Обменники могут корректировать курс валют до нескольких раз '
        'в день, поэтому условия по выбранному предложению действительны 20 минут.\n\n'
        f'💵 <b>Введите сумму {choosen_pair["pair_name"].split("/")[1]} для обмена:</b>'
        )
    
    return message


async def crypto_offer_list_msg_maker(crypto_pair: dict):

    try:
        cr_name = crypto_pair.get('pair_name').split('/')[1]
        fiat_name = crypto_pair.get('pair_name').split('/')[0]
    except:
        message = '<b>Отсутствуют активные предложения. Повторите позже.</b>'
        return message
    
    score_data = crypto_pair.get('owner_score')
    minAmount = '' if crypto_pair['min_amount'] == float(0) else f"Минимальная сумма: {crypto_pair['min_amount']} {cr_name}\n"
    sell_rate = crypto_pair.get('sell_rate')
    buy_rate = crypto_pair.get('buy_rate')
    banks = crypto_pair.get('banks')
    offer_name = crypto_pair.get('offer_name')
    message = (
        f'💱 <b>{offer_name} | сделок: {score_data["total_cr_transactions"]}</b>\n\n'
        f'<b>{crypto_pair["pair_name"]}</b>\n'
        f'Покупка: {sell_rate} {fiat_name} | Продажа: {buy_rate} {fiat_name}\n'
        f'{minAmount}'
        f'Банки: {banks}'
    )
    
    return message



async def min_cr_amount_error_msg_maker(offer_data):

    cr_name = offer_data.get('pair_name').split('/')[1]

    message = (
        '⚠️ Вы указали сумму меньше, чем минимальная сумма '
        'сделки, обозначенная обменником в данном объявлении.\n\n'
        '↩ Вы можете вернуться к выбору предложений и выбрать '
        'другой вариант или указать сумму в пределах:\n\n'
        f'💰 от <b>{offer_data["min_amount"]} {cr_name}</b>'
    )
    return message


async def show_user_buy_cr_amount(sellAmount, cr_exch_type, offer_data):

    cr_name = offer_data.get('pair_name').split('/')[1]
    fiat_name = offer_data.get('pair_name').split('/')[0]
    buy_rate = offer_data.get('buy_rate')
    sell_rate = offer_data.get('sell_rate')


    message_sell =(
        f'💸 Вы продаете: ⚡ {sellAmount} {cr_name}\n'
        f'💰 Вы получаете: ⚡ {round(sellAmount * buy_rate)} {fiat_name}\n\n'
        f'Хотите создать заявку?'
    )
   
    message_buy =(
        f'💸 Вы покупаете: ⚡ {sellAmount} {cr_name}\n'
        f'💰 Вы заплатите: ⚡ {round(sellAmount * sell_rate)} {fiat_name}\n\n'
        f'Хотите создать заявку?'
    )    
    return message_sell if cr_exch_type == 'sell' else message_buy


async def set_cr_amount_returned_msg_maker(offer_data):

    cr_name = offer_data.get('pair_name').split('/')[1]
    message = f'🔹 Введите новую сумму {cr_name} которую хотите обменять:'

    return message


async def create_new_crypto_order_success(response_data):
    order_id = response_data.get("id")
    pair_name = response_data.get('pair_name')

    message = (
        f'Заявка на обмен <b>{pair_name} | №{order_id}</b> успешно отправлена. '
        f'Скоро с вами свяжется менеджер для продолжения обмена.'
    )

    return message



async def staff_show_uncompleted_cr_transfers(order):

    id = order['id']
    sell_amount = order['sell_amount']
    buy_amount = order['buy_amount']
    rate = order['rate']
    order_type = order['order_type']
    cr_name = order["pair_name"].split("/")[1]
    fiat = order["pair_name"].split("/")[0]

    _1 = f'🔹 <b>Вам переведут {sell_amount} {cr_name}</b>\n' if order_type=='sell' else f'🔹 <b>Вам переведут {buy_amount} {fiat}</b>\n'
    _2 = f'🔹 <b>Вы переведете {buy_amount} {fiat}</b>\n' if order_type=='sell' else f'🔹 <b>Вы переведете {sell_amount} {cr_name}</b>\n'

    message = (
        '✅ <b>Новый крипто перевод!</b>\n\n'
        f'🔹 <b>ID {id}</b>\n'
        f'🔹 <b>{order_type} {cr_name}</b>\n'
        f'🔹 Курс {rate}\n\n'
        f'{_1}'
        f'{_2}'
    )

    return message