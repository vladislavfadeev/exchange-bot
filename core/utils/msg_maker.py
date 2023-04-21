from email import message
from core.middlwares.routes import r    # Dataclass whith all api routes
from core.api_actions.bot_api import SimpleAPI



async def offer_list_msg_maker(offers):
    

    messages = []

    for offer in offers:

        minAmount = 'Любая' if offer['minAmount'] == None else f"{offer['minAmount']} {offer['currency']}"
        maxAmount = 'Любая' if offer['maxAmount'] == None else f"{offer['maxAmount']} {offer['currency']}"
        
        banks = ''
        for bName in offer['banks']:
            banks += f'👉 {bName["name"]}\n'

        messages.append(
            f'💰 Обмен {offer["currency"]} 💰\n'
            f'💸 {offer["bannerName"]} 💸\n'
            f'💳 Банки, с которыми работает обменник:👇\n'
            f'{banks}\n'
            f'▶️ Минимальная сумма обмена: ⚡ {minAmount}\n'
            f'▶️ Максимальная сумма обмена: ⚡ {maxAmount}\n\n'
            f'🔥 Курс в MNT: ⚡ {offer["rate"]} \n'
        )

    return messages


async def set_amount_msg_maker(offerData):

    message = f'👌 Ваш выбор принят!\n👇 Введите сумму {offerData["currency"]} которую хотите продать: 👇'

    return message


async def set_amount_returned_msg_maker(offerData):

    message = f'👇 Введите новую сумму {offerData["currency"]} которую хотите продать: 👇'

    return message


async def min_amount_error_msg_maker(offerData):

    message = f'⚠️ Вы указали сумму меньше, чем минимальная сумма\
                \nсделки, обозначенная обменником в данном объявлении.\
                \n\n↩ Вы можете вернуться к выбору предложений и выбрать\
                \nдругой вариант или указать сумму равную или превышающую: \
                \n💰 {offerData["minAmount"]} {offerData["currency"]}'
    
    return message


async def max_amount_error_msg_maker(offerData):

    message = f'⚠️ Вы указали сумму больше, чем максимальная сумма\
                \nсделки, обозначенная обменником в данном объявлении.\
                \n\n↩ Вы можете вернуться к выбору предложений и выбрать\
                \nдругой вариант или указать сумму равную или менее: \
                \n💰 {offerData["maxAmount"]} {offerData["currency"]}'    

    return message


async def show_user_buy_amount(sellAmount, rate, currency):

    message = f'💸 Вы продаете: ⚡ {sellAmount} {currency}\
                \n💰 Вы получаете: ⚡ {sellAmount * rate} MNT'
    
    return message


async def set_sell_bank(currency):

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


async def complete_set_new_bank(allData):

    sellAmount = allData['sellAmount']
    offerData = allData['selectedOffer']

    detaillUrl = allData["sellBank"]
    account = await SimpleAPI.getDetails(r.userRoutes.changerBanks, detaillUrl)
    acc = account.json()

    message = f'👌 Ваши реквизиты приняты! 👌\
                \n\n👉 Теперь выполните перевод {sellAmount} {offerData["currency"]}\
                \nна счет обменника, по реквизитам ниже 👇\
                \n\n🏦 Банк: {acc["name"]}\
                \n💳 Счет: {acc["bankAccount"]}\
                \n\n⚠️ Обязательно! ⚠️\
                \n После перевода, ответным сообщением\
                \nпришлите скриншот / фото\
                \nэкрана (или чек) с информацией\
                \nо платеже ⚠️'
    
    return message


async def changer_inform(changerId, stateData):

    changer =  await SimpleAPI.getDetails(r.changerRoutes.changerProfile, changerId)
    c = changer.json()
    summ = stateData["sellAmount"] * stateData["selectedOffer"]["rate"]

    message = f'🔰 {c["name"]} здравствуйте!\
                \n\nВашим предложением по покупке {stateData["selectedOffer"]["currency"]}\
                \nзаинтересовался пользователь.\
                \n🏦 Сейчас он получил банковские реквизиты\
                \nдля перевода {stateData["selectedOffer"]["currency"]} {stateData["sellAmount"]} \
                \nна ваш счет.\
                \n\n⚠️ Ожидайте подтверждение перевода. ⚠️\
                \n\nПосле чего, вам придут реквизиты пользователя\
                \nна которые вы дожны будете перевести \
                \n💰 {summ} MNT в соответсвии с предложенным\
                \nранее вами курсом {stateData["selectedOffer"]["rate"]}'
    
    return message


async def accept_user_transfer():

    message = f'⚠️ Пользователь подтвердил перевод\
                \nданным файлом. Ознакомьтесь, и\
                \nесли данные корректны нажмите кнопку\
                \n➡️ подтвердить получение 👇'
    
    return message


async def user_inform(buyAmount):

    message = f'👌Мы отправили обменнику информацию\
                \nо совершенном вами платеже.\
                \n\n💰 Как только он подтвердит получение\
                \n денег, к вам придет сообщение об этом.\
                \n\n⚡ После этого обменник выполнит\
                \n перевод {buyAmount} MNT на указанные вами\
                \nреквизиты.\
                \n\n⚠️ Внимание! ⚠️\
                \nПосле получения денег не забудьте\
                \nнажать кнопку "Подтвердить получение"'
    
    return message


async def contact_to_admin():

    message = f'При возникновении внештатных ситуаций \
                \nпишите аккаунту @Dzmnd, вам обязательно\
                \nпомогут и проблема будет решена.'
    
    return message


async def accept_user_transfer2():

    message = f'👌 Обменник подтвердил получение\
                \nвашего перевода.\
                \n\n💸 Мы отправили ему ваши реквизиты\
                \nдля перевода. Ожидайте поступление\
                \nденежных средств. 💸\
                \n\n⚠️ После совешения перевода обменником\
                \nвам придет сообщение с подтверждением\
                \nоперации. После поступления денег\
                \nне забудьте нажать кнопку \
                \n"Подтвердить получение" ⚠️'
    
    return message


async def accept_changer_transfer(transfer):

    account = await SimpleAPI.getDetails(
        r.userRoutes.userBanks,
        transfer['userBank']
    )
    acc = account.json()

    message = f'👌 Ваше подтверждение принято! 👌\
                \n\n👉 Теперь выполните перевод {transfer["buyAmount"]} MNT\
                \nна счет пользователя, по реквизитам ниже 👇\
                \n\n🏦 Банк: {acc["name"]}\
                \n💳 Счет: {acc["bankAccount"]}\
                \n\n⚠️ Обязательно! ⚠️\
                \n После перевода, ответным сообщением\
                \nпришлите скриншот / фото\
                \nэкрана (или чек) с информацией\
                \nо платеже ⚠️'

    return message


async def decline_user_transfer():

    message = f'⚠️ К сожалению, обменник не подтвердил\
                \nперевод денег по своим реквизитам. ⚠️\
                \n\nАдминистратор уже получил уведомление\
                \nо внештатной ситауции и во всем разбирается.\
                \nВ ближайшее время он с вами свяжется'
    

async def accept_changer_proof(transferId):

    message = f'🔰 Заявка № {transferId} 🔰\
                \n\n⚠️ Обменник подтвердил перевод\
                \nданным файлом. Ознакомьтесь, если\
                \nданные корректны и деньги зачислены\
                \n➡️ нажмите подтвердить получение 👇'
    

async def changer_inform2(transferId):

    message = f'🔰 Заявка № {transferId} 🔰\
                \n👌Мы отправили пользователю информацию\
                \nо совершенном вами платеже.\
                \n\n💰 Как только он подтвердит получение\
                \n денег, к вам придет сообщение об этом.'
    
    return message


async def accept_changer_transfer2(transferId):

    message = f'🔰 Заявка № {transferId} 🔰\
                \n👌 Пользователь подтвердил получение\
                \nвашего перевода.\
                \n\n💸 Спасибо что вы с нами!'
    
    return message


async def accept_changer_transfer3(transferId):

    message = f'🔰 Заявка № {transferId} 🔰\
                \n👌 Ваше подтверждение принято! 👌\
                \n\n💸 Спасибо что вы с нами!'
    
    return message


async def decline_changer_transfer(transferId):

    message = f'🔰 Заявка № {transferId} 🔰\
                \n⚠️ К сожалению, пользователь не подтвердил\
                \nперевод денег по своим реквизитам. ⚠️\
                \n\nАдминистратор уже получил уведомление\
                \nо внештатной ситауции и во всем разбирается.\
                \nВ ближайшее время он с вами свяжется'
    
    return message
    

async def decline_changer_transfer2(transferId):

    message = f'🔰 Заявка № {transferId} 🔰\
                \n\nАдминистратор уже получил уведомление\
                \nо внештатной ситауции и во всем разбирается.\
                \nВ ближайшее время он с вами свяжется'
    
    return message



async def staff_welcome(transfers):

    # stuff_name = f'{response["name"]} {response["lastName"]}'
    value = len(transfers) if transfers else None
    alert = f'<b>У вас есть неотвеченный перевод!</b>\n\n' if value else '💰'

    message = (
        f'{alert}'
        f'💻 Личный кабинет.\n'
        f'Приветствую вас!\n'
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

        for account in accounts:
            currency = account['currency']['name']
            acc_input += f'\n⚡ {account["name"]}\n {currency} {account["bankAccount"]}\n'

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


async def staff_create_offer_show_final_text(post_data, banks_accounts):

    minAmount = 'Любая' if post_data['minAmount'] == None else f"{post_data['minAmount']} {post_data['currency']}"
    maxAmount = 'Любая' if post_data['maxAmount'] == None else f"{post_data['maxAmount']} {post_data['currency']}"
    
    banks = ''
    for bName in banks_accounts:
        banks += f'👉 {bName["name"]}\n'

    message = (
        f'💰 Обмен {post_data["currency"]} 💰\n'
        f'💸 {post_data["bannerName"]} 💸\n'
        f'💳 Банки, с которыми работает обменник:👇\n'
        f'{banks}\n'
        f'▶️ Минимальная сумма обмена: ⚡ {minAmount}\n'
        f'▶️ Максимальная сумма обмена: ⚡ {maxAmount}\n\n'
        f'🔥 Курс в MNT: ⚡ {post_data["rate"]} \n'
    )

    return message

async def staff_edit_offer_show(offer):

    minAmount = 'Любая' if offer['minAmount'] == None else f"{offer['minAmount']} {offer['currency']}"
    maxAmount = 'Любая' if offer['maxAmount'] == None else f"{offer['maxAmount']} {offer['currency']}"
    
    banks = ''
    for bName in offer['banks']:
        banks += f'👉 {bName["name"]}\n'

    message = (
        f'💰 Обмен {offer["currency"]} 💰\n'
        f'💸 {offer["bannerName"]} 💸\n'
        f'💳 Банки, с которыми работает обменник:👇\n'
        f'{banks}\n'
        f'▶️ Минимальная сумма обмена: ⚡ {minAmount}\n'
        f'▶️ Максимальная сумма обмена: ⚡ {maxAmount}\n\n'
        f'🔥 Курс в MNT: ⚡ {offer["rate"]} \n'
        f'\n<b>Выберете что будем редактировать?</b>'
    )

    return message