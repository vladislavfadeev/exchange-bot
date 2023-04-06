


async def offer_list_msg_maker(offers):
    
    banks = ''
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


async def min_amount_error_msg_maker(offerData):

    message = f'⚠️ Вы указали сумму меньше, чем минимальная сумма сделки, \
                \nобозначенная обменником в данном объявлении.\
                \n\n↩ Вы можете вернуться к выбору предложений и выбрать\
                \nдругой вариант или указать сумму равную или превышающую: \
                \n💰 {offerData["minAmount"]} {offerData["currency"]}'
    
    return message


async def max_amount_error_msg_maker(offerData):

    message = f'⚠️ Вы указали сумму больше, чем максимальная сумма сделки, \
                \nобозначенная обменником в данном объявлении.\
                \n\n↩ Вы можете вернуться к выбору предложений и выбрать\
                \nдругой вариант или указать сумму равную или менее: \
                \n💰 {offerData["maxAmount"]} {offerData["currency"]}'    

    return message





async def choice_msg_maker(data_sr):
    data = data_sr['post']
    message = f'Выполните перевод по реквизитам:\
        \n{data["changer_bank"]}\
        \nСчет: {data["changer_bank_account"]}\n\
        \nПришлите скриншот перевода ответным сообщением.'
    return message


async def changer_transaction_msg_maker(bank, account):
    message = f'Выполните перевод по реквизитам:\
    \n{bank}\
    \nСчет: {account}\n\
    \nПришлите скриншот перевода ответным сообщением.'
    return message