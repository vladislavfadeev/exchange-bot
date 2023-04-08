

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
                \nперевести 💸 {currency} 👇'
    
    return message


async def choose_user_bank_from_db():

    message = f'⚠️ Ранее вы указывали следующие счета для\
                \nMNT за проданную валюту. Вы можете выбрать\
                \nодин из них либо указать новый. 👇'
    
    return message