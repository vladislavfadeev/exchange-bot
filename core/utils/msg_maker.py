


async def request_msg_maker(request):
    request_id = request['id']
    message = f'Новая заявка!\n\
        \nid предложения: {request["id"]}\
        \nСумма на обмен: {request["amount"]}\
        \nКурс продавца: {request["sell_rate"]}\
        \nВалютная пара: {request["currency_pair"]["name"]}'
    return message, request_id


async def response_msg_maker(data_sr):
    data = data_sr['post']
    sum = data['buy_rate'] * data['amount']
    message = f'Поступил ответ на ваш запрос:\
        \nid предложения: {data["id"]}\
        \nВаш банк: {data["customer_bank"]}\
        \nВалютная пара: {data["currency_pair"]["name"]}\
        \nБанк обменника: {data["changer_bank"]}\
        \nПредложенный курс: {data["buy_rate"]}\
        \nИтоговая сумма на ваш счет: {sum}'
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