'''
Messages for 'home' module
'''
user_not_loggin = 'Вы не авторизованы'
start_message = 'Рады приветствовать вас!\nУ нас вы можете обменять валюту онлайн.\n\n\
Для получения справки воспользуйтесь соответствующей кнопкой ниже.'
start_help_message = 'Тут будет справка о правилах пользования сервисом на стартовом экране'
start_work_mode_info = 'Тут информация о режиме работы'
staff_hello = 'Добро пожаловать!'
staff_404 = 'Вход разрешен только сотрудникам'
staff_islogin = 'Вы уже вошли в систему как зарегистрированный пользователь'


'''
Messages for 'user' module
'''
zero_offer = 'К сожалению, сейчас нет предложений для обмена по выбранной вами валюте'
currency_choice_1 = 'Какую валюту вы хотите продать?'
type_error_msg = 'Вы ввели некорректное значение. Корректный пример: 25000'
enter_user_bank_name = (
    'Вы впервые производите обмен в нашей системе, у вас нет сохранившихся счетов'
    '🏦 Выберите название банка, куда вы ходите получить 💸 MNT за проданную валюту: 👇'
)
user_empty_event = 'У вас нет новых сообщений'
user_transfer_claims_message = (
    'Мы оповестили администратора'
    'о возникшей ситуации,'
    'Ожидайте обратной связи.\n\n'
    'Еслу у вас не отвеченные события -\n'
    'продолжайте на них отвечать.\n'
)


'''
Messages for 'admin' module
'''




'''
Messages for 'changers' module
'''
stuff_zero_offer = 'К сожалению, у вас нет созданных предложений для обмена по выбранной вами валюте'
staff_zero_banks = 'К сожалению, у вас неуказанно ни одного банковского счета для работы с с выбранной валютой. Обратитесь к администратору для добавления счетов'

staff_will_set_amount = (
    'Хотите установить минимальную и\n'
    'макимальную сумму для данного\n'
    'предложения?\n'
)

staff_will_set_name = (
    'Хотите указать комментарий к\n'
    'вашему предложению?\n'
    'Он будет размещен в самом верху\n'
    'текста вашего объявения.\n'
    'Например, тут можно указать о\n'
    'вашем быстром ответе на входящие\n'
    'переводы пользователей, это выгодно\n'
    'выделит вас на фоне остальных обменников\n'
)

staff_set_offer_name = (
    'Укажите комментарий с длиной не\n'
    'более 50 символов:\n'
)

staff_create_new_offer_succes = (
    '⚡ Вы успешно добавили новое\n'
    'предложение на обмен валюты!\n\n'
    'При необходимости, вы можете\n'
    'отредактировать все параметры\n'
    'данного предложения в соответствующем\n'
    'разделе меню <b>"Мои предложения</b>"\n'
    'вашего личного кабинета\n'
)

staff_create_new_offer_succes_non_active = (
    '⚡ Вы успешно добавили новое\n'
    'предложение на обмен валюты!\n\n'
    '<b>Предложение сохранено, но не опубликованно!</b>\n'
    '<b>Активировать публикацию можно в </b>\n'
    '<b>разделе "Мои предложения">"Не активные"</b>\n\n'
    'При необходимости, вы можете\n'
    'отредактировать все параметры\n'
    'данного предложения в соответствующем\n'
    'разделе меню <b>"Мои предложения">"Редактировать"</b>\n'
    'вашего личного кабинета\n'
)

staff_edit_offer_success = (
    'Указанное вами значение отредатировано!'
)

staff_edit_offer_new_rate = (
    'Укажите новый курс обмена'
)
staff_edit_offer_new_rate_error = (
    'Вы указали не корректное значение.'
    'Пример правильно введенного'
    'значения 52,7 или 52.7'
)
staff_delete_offer_success = (
    'Выбранное вами предложение удалено!'
)
staff_edit_offer_banks_success = (
    'Привязанные к предложению банковские\n'
    'счета изменены успешно\n'
)
staff_show_banks_account = (
    'К сожалению у вас не зарегистрированно\n'
    'ни одного банковского счета!\n\n'
    'Обратитесь к администратору.\n'
)
staff_empty_uncompleted_transfers = (
    'На данный момент неотвечанные переводы отсутствуют'
)
staff_get_proof_success = (
    'Файл принят, на жмите на кнопку "Подтвердить"'
)
staff_transfer_claims_message = (
    'Мы уже оповестили администратора\n'
    'о возникшей ситуации.\n'
    'Он получил информацию по\n'
    'данному переводу и во всем разбирается.\n'
    'Ожидайте обратной связи.\n\n'
    'Еслу у вас есть не отвеченные переводы -\n'
    'продолжайте на них отвечать.\n'
)
staff_transfer_accept_success = (
    'Ваше подтверждение принято!\n'
    'Еслу у вас не отвеченные переводы -\n'
    'продолжайте на них отвечать.\n'
)


separator = '🔰🔰🔰🔰🔰🔰🔰🔰🔰🔰'

decline_message = 'Запрос отменен.'
chr_enter_rate = 'Укажите курс в MNT, по которому готовы производить обмен:'
chr_choose_bank = 'Выберите банк, на который готовы принять деньги от пользователя'
chr_send_response = 'Ваш ответ отправлен пользователю'