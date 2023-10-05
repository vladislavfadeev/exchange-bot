'''
Messages for 'home' module
'''
user_not_loggin = 'Вы не авторизованы'
error_msg = 'Возникла техническая ошибка. Повторите попытку позже'
support_us_message = (
    '<b>Спасибо за интерес к нашему проекту!</b>\n\n'
    'На разработку и поддержку данного сервиса уходит '
    'много времени, усилий и денег, поэтому мы будем рады, '
    'если вы решите поддержать наш проект финансово.\n\n'
    '<b>Реквизиты:</b>\n'
    '<b>MNT</b> - TDB-bank: <code>821012795</code>\n'
    '<b>RUB</b> - Sberbank: <code>5469 1800 1197 4675</code>\n'
)
staff_hello = 'Добро пожаловать!'
staff_404 = 'Вход разрешен только сотрудникам'
staff_islogin = 'Вы уже вошли в систему как зарегистрированный пользователь'
type_error_message = '⚠️ Этот тип данных не поддерживается ⚠️'
help_message = (
    '<b>Данный бот предоставляет платформу для обмена денежных средств различных валют.</b>\n\n'
    '<b>Примечание:</b> У каждого продавца есть свое рабочее время, и если продавец не находится '
    'в режиме "Онлайн", то доступных заявок не будет. Если обменник находится в сети, то '
    'заявки будут активны в любое время.\n\n'
    '<b>Стандартное рабочее время обменников: 10:00 - 20:00 (GMT+8).</b>\n\n'
    'Чтобы произвести обмен необходимо выполнить последовательность действий:\n'
    '1. Выберите "Обменять валюту" в главном меню.\n'
    '2. Откроется список доступных валют и операций.\n' 
    '3. В зависимости от того, что вы хотите купить или продать, выберите соответствующую кнопку.\n'
    '4. Бот выполнит поиск в базе данных и покажет все доступные предложения от обменников. Если предложений нет, бот сообщит об этом.\n'
    '5. Выберите предложение, которое вам подходит, нажав кнопку "Обменять здесь".\n'
    '6. Затем отправьте боту сообщение с указанием суммы (только цифры, без пробелов или других символов).\n'
    '7. Бот сообщит вам расчетную сумму.\n'
    '8. После вашего согласия вам потребуется указать ваш банк, куда будут отправлены средства от продавца.\n'
    '9. Если счет используется впервые, вам нужно будет ввести его вручную. Если это не первый раз, будет предоставлена опция выбора счета.\n'
    '10. На последнем шаге выполните перевод денежных средств продавцу и ОБЯЗАТЕЛЬНО прикрепите в сообщении к боту '
    'документ-подтверждение, например, скриншот из мобильного банка или СМС.\n'
    '11. После прикрепления подтверждения продавец получит уведомление о вашем переводе, и вам нужно будет ожидать '
    'ответного сообщения от продавца на главной странице в разделе "Мои сообщения".\n'
    '12. Когда продавец отправит денежные средства и приложит скрин подтверждения, у вас появится новое сообщение.\n'
    '13. Если сделка прошла успешно, просим вас подтвердить ее.\n\n'
    '<b>В случае возникновения спорных моментов</b>, требующих дополнительного вмешательства, '
    'воспользуйтесь кнопкой <b>"Связаться с админом"</b>.\n\n'
    '<b>ВАЖНО!</b> Пожалуйста, не игнорируйте подтверждающие документы, поскольку они являются '
    'основой для разрешения возможных спорных ситуаций.'
)



'''
Messages for 'user' module
'''
zero_offer = 'К сожалению, сейчас нет предложений для обмена по выбранной вами валюте'
currency_choice_1 = '⬇ Выберите действие: ⬇'
type_error_msg = 'Вы ввели некорректное значение. Корректный пример: 25000'
user_empty_event = 'У вас нет новых сообщений'
user_transfer_claims_message = (
    '✅ Мы оповестили администратора '
    'о возникшей ситуации. '
    'Ожидайте обратной связи.\n\n'
    'Если у вас новые входящие сообщения -\n'
    'продолжайте на них отвечать.\n'
)
account_value_error = (
    'Счет должен собержать только цифры. '
    'Без букв, знаков препинания и пробелов.\n\n'
    '<b>Поробуйте снова.</b>'
)
account_exception = (
    '<b>Данный тип данных не поддерживется.</b>\n\n'
    'Пожалуйста, укажите корректное значение. '
    'Счет должен собержать только цифры, '
    'без букв, знаков препинания и пробелов.'
)
create_account_error = (
    '<b>Указанный вами номер счета уже существует!</b>\n\n'
    'Попробуйте снова, возможно вы допустили ошибку. '
    'Если проблемма повторится - свяжитесь с '
    'администратором для решения данной проблеммы.'
)
timeout_claims_proof_message = (
    '✅ Отправье боту подтверждение вашего перевода. Например:\n'
    '- скриншот с платежной информацией\n'
    '- чек из вашего банковского приложения\n'
)
user_success_claims_message = (
    '✅ Мы уже оповестили администратора '
    'о возникшей ситуации.\n'
    'Он получил информацию по '
    'данному переводу и во всем разбирается.\n\n'
    'Ожидайте обратной связи.'
)
'''
Messages for 'admin' module
'''




'''
Messages for 'changers' module
'''
stuff_zero_offer = (
    'Предложения отсутствуют'
    )
staff_zero_banks = (
    'К сожалению, у вас отсутствуют банковские счета '
    'для работы с выбранной валютой. '
    'Обратитесь к администратору для их добавления.'
    )

staff_will_set_amount = (
    '✅ Хотите установить минимальную и '
    'максимальную сумму обмена для данного '
    'предложения?'
)

staff_will_set_name = (
    '✅ <b>Хотите указать комментарий к '
    'вашему предложению?</b>\n'
    'Он будет размещен в самом верху '
    'текста вашего объявления.\n\n'
    'Например, тут можно указать о '
    'вашем быстром ответе на входящие '
    'переводы пользователей, это выгодно '
    'выделит вас на фоне остальных обменников.'
)

staff_set_offer_name = (
    '✅ Укажите комментарий с длиной не '
    'более 50 символов:\n'
)

staff_create_new_offer_succes = (
    '✅ <b>Вы успешно добавили новое '
    'предложение на обмен валюты!</b>\n\n'
    'При необходимости, вы можете '
    'отредактировать все параметры '
    'данного предложения в соответствующем '
    'разделе меню <b>Мои предложения</b> '
    'вашего личного кабинета.'
)

staff_create_new_offer_succes_non_active = (
    '✅ <b>Вы успешно добавили новое '
    'предложение на обмен валюты!</b>\n\n'
    '<b>Предложение сохранено, но не опубликованно!</b>\n'
    'Активировать публикацию можно в '
    'разделе <b>Мои предложения</b> > <b>Не активные</b>\n\n'
    'При необходимости, вы можете '
    'отредактировать все параметры '
    'данного предложения в соответствующем '
    'разделе меню <b>Мои предложения</b> > <b>Редактировать</b> '
    'вашего личного кабинета'
)

staff_edit_offer_success = (
    '✅ Указанное вами значение отредатировано!'
)

staff_edit_offer_new_rate = (
    'Укажите новый курс обмена: '
)
staff_edit_offer_new_rate_error = (
    '<b>Вы указали не корректное значение.</b>\n\n'
    'Пример правильно введенного'
    'значения 52,7 или 52.7'
)
staff_delete_offer_success = (
    '✅ Выбранное вами предложение удалено!'
)
staff_edit_offer_banks_success = (
    '✅ Привязанные к предложению банковские '
    'счета изменены успешно'
)
staff_show_banks_account = (
    'К сожалению, у вас не зарегистрировано '
    'ни одного банковского счета!\n\n'
    'Обратитесь к администратору.'
)
staff_empty_uncompleted_transfers = (
    'На данный момент не отвеченные переводы отсутствуют'
)
staff_get_proof_success = (
    '✅ Файл принят, на жмите на кнопку <b>Подтвердить</b>'
)
staff_transfer_claims_message = (
    '✅ <b>Мы уже оповестили администратора'
    'о возникшей ситуации.</b> '
    'Он получил информацию по '
    'данному переводу и во всем разбирается.\n\n'
    'Ожидайте обратной связи.\n\n'
    'Если у вас есть новые входящие переводы - '
    'продолжайте на них отвечать.'
)
staff_transfer_accept_success = (
    '✅ <b>Ваше подтверждение принято!</b>\n'
    'Если у вас новые входящие переводы - '
    'продолжайте на них отвечать.\n'
)


separator = 11 * '🔸'

decline_message = 'Запрос отменен.'
chr_enter_rate = 'Укажите курс в MNT, по которому готовы производить обмен:'
chr_choose_bank = 'Выберите банк, на который готовы принять деньги от пользователя'
chr_send_response = 'Ваш ответ отправлен пользователю'