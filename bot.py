import json
from db import session 
from models.DataBaseClasses import *
import telebot
from telebot import types

cfg = json.load(open("config.json"))
token = cfg['bot']['token']
bot = telebot.TeleBot(token)


#Обработка входа в систему.
@bot.message_handler(commands = ["start"])
def start(message):
    username = message.chat.first_name
    chat_id = message.chat.id
    cur_role = None
    #если еще нет администраторов - назначаем администратором
    if not User.get_all_users_with_role(session, RoleNames.ADMIN.value):
        cur_role = RoleNames.ADMIN.value
    elif not User.find_by_conversation(session, chat_id):
        cur_role = RoleNames.CLIENT.value
    #если назначена новая роль
    if cur_role:
        #добавляем сведения в бд
        User.add_several(session, [(chat_id, username, cur_role)])
        bot.send_message(chat_id, f'{username}, Вы успешно зарегистрировались в системе.\nВаш статус - {RoleNames(cur_role).name}')
    else:
        #пользователь уже зарегистрирован
        user = User.find_by_conversation(session, chat_id)
        cur_role = user.role_id
        if user.name.lower() != username.lower():
            user.change_name(session, username, chat_id)
        bot.send_message(chat_id, f'{username}, Вы уже зарегистрировались в системе.\nВаш статус - {RoleNames(user.role_id).name}')

        


#вход в систему менеджера/админа
@bot.message_handler(func=lambda message: " ".join(message.text.split()[0:2]) == '/superuser init')
def create_superuser(message):
    args = message.text.split()
    if not User.find_by_conversation(session, message.chat.id):
        bot.send_message(message.chat.id, "Сначала нужно зарегистрироваться, воспользуйтесь командой /start.")
    elif len(args) != 3:
        bot.send_message(message.chat.id, "Неправильное использование команды superuser.\nШаблон:/superuser init TOKEN")
    elif not Token.find(session, args[2]):
        bot.send_message(message.chat.id, "Данного токена нет, возможно, вы ошиблись.")
    else:
        token_new = args[2]
        user = User.find_by_conversation(session,message.chat.id)
        my_token = Token.find(session, token_new)
        if my_token:
            user.appoint(session,my_token.role_id)
            my_token.activate(session)
            bot.send_message(message.chat.id, "Токен успешно активирован, ваша роль {}.".format(RoleNames(my_token.role_id).name))
        else:
            bot.send_message(message.chat.id, "Не удалось авторизоваться в системе. Попробуйте еще раз.")





#открытие нового тикета
@bot.message_handler(commands = ["ticket_add"])
def create_ticket(message):
    user = User.find_by_conversation(session, message.chat.id)
    if not user:
        bot.send_message(message.chat.id, "Для того, чтобы создать тикет, необходимо зарегистрироваться в " \
                         "системе. Воспользуйтесь командой /start.")
    else:
        if user.role_id != RoleNames.CLIENT.value:
            bot.send_message(message.chat.id, "Комманда /ticket_add доступна только для клиентов.")
        else:    
            bot.send_message(message.chat.id, user.name + ", для начала кратко сформулируйте Вашу проблему:")
            bot.register_next_step_handler(message, get_title)
def get_title(message):
    bot.send_message(message.chat.id, "Отлично. Теперь опишите Ваш вопрос более детально: ")
    title = message.text
    conversation = message.chat.id
    Ticket.create(session, title, conversation)
    bot.register_next_step_handler(message, get_ticket_body)
# TODO: Переделать функцию. Ticket.create уже назначил тикет на менеджера.
# TODO: (В случае, если все менеджеры отказались, тикет был назначен на самого свободного и метод вернул 1)
# def get_ticket_body(message):
#     bot.send_message(message.chat.id, "Ваш запрос обрабатывается...")
#     user = User.find_by_conversation(session, message.chat.id)
#     ticket = user.get_active_tickets(session)[0]
#     #теперь нужно назначить менеджера
#     manager = User.get_free_manager(session, [])
#     if manager:
#         Message.add(session, message.text, ticket.id, message.chat.id)
#         bot.send_message(message.chat.id, "Ваш вопрос отправлен менеджеру, спасибо.")
#     else:
#         bot.send_message(message.chat.id, "Извините, свободных менеджеров нет, повторите попытку позже.")

        



#просмотр активных тикетов
@bot.message_handler(commands = ["ticket_list"])
def active_ticket_list(message):
    user = User.find_by_conversation(session, message.chat.id)
    if user == None:
        bot.send_message(message.chat.id, "Для того, чтобы просмотреть список тикетов, необходимо зарегистрироваться в " \
                         "системе. Воспользуйтесь командой /start или /superuser_init.")
    elif user.role_id == 3:
        #для клиента - вывод активных тикетов(или всех?TODO)
        ans = ''
        for x in user.get_active_tickets(session):
            ans += 'Ticket id: ' + str(x.id) + '\n'
            ans += 'Title: ' + x.title + '\n' + 'Manager_id: '
            if x.manager_id == None:
                ans += "Менеджер еще не найден. Поиск менеджера..." + '\n'
            else:
                ans += "Manager_id: " + str(x.manager_id) + '\n'
            ans += "Start data: " + str(x.start_date) + '\n\n'
        bot.send_message(message.chat.id, "Список активных тикетов:\n\n" + ans)
    elif user.role_id == 2:
        #для менеджера - активные прикрепленные тикеты + client_id
        ans = ''
        for x in user.get_active_tickets(session):
            ans += 'Ticket id: ' + str(x.id) + '\n'
            ans += 'Title: ' + x.title + '\n' + 'Manager_id: '
            ans += "Client_id: " + str(x.client_id) + '\n'
            ans += "Start data: " + str(x.start_date) + '\n\n'
        bot.send_message(message.chat.id, "Список активных тикетов:\n\n" + ans)
    else:
        #для администратора - активные тикеты всех менеджеров(видимо)
        ans = ''
        for x in user.get_active_tickets(session):
            ans += 'Ticket id: ' + str(x.id) + '\n'
            ans += 'Title: ' + x.title + '\n' + 'Manager_id: '
            if x.manager_id == None:
                ans += "Менеджер еще не найден. Поиск менеджера..." + '\n'
            else:
                ans += str(x.manager_id) + '\n'
            ans += "Client_id: " + str(x.client_id) + '\n'
            ans += "Start data: " + str(x.start_date) + '\n\n'
        bot.send_message(message.chat.id, "Список активных тикетов:\n\n" + ans)





@bot.message_handler(commands = ["ticket_id"])
def chose_ticket(message):
    user = User.find_by_conversation(session, message.chat.id)
    if user == None:
        bot.send_message(message.chat.id, "Для того, чтобы просмотреть список тикетов, необходимо зарегистрироваться в " \
                         "системе. Воспользуйтесь командой /start или /superuser_init.")
    elif user.role_id == 3:
        #для клиента - это выбор тикета для переписки
        bot.send_message(message.chat.id, "Введите номер тикета, на который Вы хотите переключиться. Чтобы посмотреть список "\
                         "активных тикетов, Вы можете воспользоваться командой /ticket_list.")
        bot.register_next_step_handler(message, switch_for_client)
    elif user.role_id == 2:
        #для менеджера - информация о тикете и история переписки
        bot.send_message(message.chat.id, "Введите номер тикета, который Вы хотите просмотреть. Чтобы посмотреть список "\
                         "активных тикетов, Вы можете воспользоваться командой /ticket_list.")
        bot.register_next_step_handler(message, switch_for_superuser)
    else:
        bot.send_message(message.chat.id, "Введите номер тикета, на который Вы хотите переключиться. Для просмотра активных "\
                         "тикетов Вы можете воспользоваться командой /ticket_list, а затем снова /ticket_id.")
        bot.register_next_step_handler(message, switch_for_superuser)
def switch_for_client(message):
    if message.text == "/ticket_list":
        active_ticket_list(message)
    else:
        if Ticket.get_by_id(session, message.text) == None:
            bot.send_message(message.chat.id, "Введен некоторектный ticket_id. Пожалуйста, попробуйте еще раз.")
        else:
            #User.find_by_conversation(session, message.chat.id).manager_id = ticket.manager_id
            bot.send_message(message.chat.id, "Тикет успешно выбран. В ближайшем времени с Вами свяжется менеджер.")
            #TODO торкнуть менеджера
def switch_for_superuser(message):
    if message.text == "/ticket_list":
        active_ticket_list(message)
    else:
        ticket = Ticket.get_by_id(session, message.text)
        if Ticket.get_by_id(session, message.text) == None:
            bot.send_message(message.chat.id, "Введен некорректный ticket_id. Пожалуйста, попробуйте еще раз.")
        else:
            ans = "Информация для ticket_id " + str(ticket.id) + ":\n\n"
            ans += 'Title: ' + ticket.title + '\n' + 'Manager_id: '
            if ticket.manager_id == None:
                ans += "Менеджер еще не найден. Поиск менеджера..." + '\n'
            else:
                ans += str(ticket.manager_id) + '\n'
            ans += "Client_id: " + str(ticket.client_id) + '\n'
            ans += "Start data: " + str(ticket.start_date) + '\n\n'
            ans += "История переписки:\n\n"
            all_messages = ticket.get_all_messages(session)
            for x in all_messages:
                ans += str(x.date) + "\n"
                role = User.find_by_id(session, x.sender_id)
                ans += RoleNames(role).name + ": " + x.body + "\n\n"
            bot.send_message(message.chat.id, ans)





@bot.message_handler(commands = ["ticket_close"])
def close_ticket(message):
    user = User.find_by_id(session, message.from_user.id)
    # user = session.query(User).filter(User.id == message.from_user.id)
    if not user:
        bot.send_message(message.chat.id, "Для того, чтобы закрыть тикет, необходимо зарегистрироваться в " \
                         "системе. Воспользуйтесь командой /start или /superuser_init.")
    elif user.role_id == 2:
        bot.send_message(message.chat.id, "Данная команда не предназначена для менеджеров. Воспользуйтесь командой "\
                         "/show_panel, чтобы просмотреть список возможных команд.")
        #соответственно сделать эту панель
    else:
        bot.send_message(message.chat.id, "Введите номер тикета, которвый Вы хотите закрыть. Для просмотра активных "\
                         "тикетов Вы можете воспользоваться командой /ticket_list.")
        #TODO Как отловить это сообщение?

    
@bot.message_handler(func=lambda message: " ".join(message.text.split()[0:2]) == '/manager create')
def create_manager(message):
    args = message.text.split()
    user = User.find_by_conversation(session, message.chat.id)
    if not user:
        bot.send_message(message.chat.id, "Сначала нужно зарегистрироваться, воспользуйтесь командой /start")
    elif (len(args)) != 2:
        bot.send_message(message.chat.id, "Много аргументов: команда должна быть /manager create")
    else:
        if user.role_id != RoleNames.ADMIN.value:
            bot.send_message(message.chat.id, "Извините. У вас недостаточно прав, вы - {}".format(RoleNames(user.role_id).name))
        else:
            new_token = Token.generate(session, RoleNames.MANAGER.value)
            bot.send_message(message.chat.id, "{}\nТокен создан - срок действия 24 часа".format(new_token.value))




@bot.message_handler(func=lambda message: " ".join(message.text.split()[0:2]) == '/admin create')
def create_admin(message):
    args = message.text.split()
    user = User.find_by_conversation(session, message.chat.id)
    print(user)
    if not user:
        bot.send_message(message.chat.id, "Сначала нужно зарегистрироваться, воспользуйтесь командой /start")
    elif (len(args)) != 2:
       bot.send_message(message.chat.id, "Много аргументов: команда должна выглядеть так /admin create")
    else:
        if user.role_id != RoleNames.ADMIN.value:
            bot.send_message(message.chat.id, "Извиите. У вас недостаточно прав, вы - {}".format(RoleNames(user.role_id).name))
        else:
            new_token = Token.generate(session, RoleNames.ADMIN.value)
            print("GGG")
            bot.send_message(message.chat.id, "{}\nТокен создан - срок действия 24 часа".format(new_token.value))


@bot.message_handler(func=lambda message: " ".join(message.text.split()[0:2]) == '/manager list')
def get_manager_list(message):
    args = message.text.split()
    user = User.find_by_conversation(session, message.chat.id)
    if not user:
        bot.send_message(message.chat.id, "Сначала нужно зарегистрироваться, воспользуйтесь командой /start")
    elif len(args) != 2:
        bot.send_message(message.chat.id, "Неверное использование команды. Шаблон: /manager list")
    elif user.role_id != RoleNames.ADMIN.value:
        bot.send_message(message.chat.id,"Извините, эта команда доступна только для администраторов приложения.")
    else:
        managers = User.get_all_users_with_role(session, RoleNames.MANAGER.value)
        if not managers:
            bot.send_message(message.chat.id,"Менеджеры не найдены, для добавления воспользуйтесь командой" \
            " /manager create")
        else:
            for i in enumerate(managers):
                bot.send_message(message.chat.id, "№{} Имя - {}, id - {}".format(i[0] + 1,i[1].name, i[1].conversation))

@bot.message_handler(commands = ["role"])
def check_role(message):
    user = User.find_by_conversation(session, message.chat.id)
    if not user:
        bot.send_message(message.chat.id, "Сначала нужно зарегистрироваться, воспользуйтесь командой /start")
    else:
        bot.send_message(message.chat.id, "Ваша текущая роль - {}".format(RoleNames(user.role_id).name)) 


#TODO TOMMOROW
#удаление менеджера
@bot.message_handler(func=lambda message: " ".join(message.text.split()[0:2]) == '/manager remove')
def manager_remove(message):
    args = message.text.split()
    user = User.find_by_conversation(session, message.chat.id)
    if not user:
        bot.send_message(message.chat.id, "Сначала нужно зарегистрироваться, воспользуйтесь командой /start")
    elif len(args) != 3:
        bot.send_message(message.chat.id, "Неверное использование команды. Шаблон: /manager remove <manager id>")
    elif user.role_id != RoleNames.ADMIN.value:
        bot.send_message(message.chat.id,"Извините, эта команда доступна только для администраторов приложения.")
    else:
        global manager_id
        manager_id = args[2]
        manager = User.find_by_conversation(session, manager_id)
        if not manager:
            bot.send_message(message.chat.id, "Менеджеров с таким id не найдено в базе данных.")
        else:
            keyboard = types.InlineKeyboardMarkup()
            key_yes = types.InlineKeyboardButton(text = "Да", callback_data = 'yes')
            keyboard.add(key_yes)
            key_no = types.InlineKeyboardButton(text = "Нет", callback_data = 'no')
            keyboard.add(key_no)
            bot.send_message(message.chat.id, "Вы действительно хотите сделать это?", reply_markup=keyboard)
            @bot.callback_query_handler(func = lambda call: True)
            def caller_worker(call):
                global manager_id
                manager = User.find_by_conversation(session, manager_id) 
                if call.data == "yes":
                    manager.demote_manager(session)
                    bot.send_message(message.chat.id, "Менеджер с id {} удалён".format(manager_id))
                elif call.data == "no":
                    bot.send_message(message.chat.id, "Отменяем операцию удаления")

#TODO команды менеджера:
#отказ менеджера от тикета
@bot.message_handler(func=lambda message: " ".join(message.text.split()[0:2]) == '/ticket refuse')
def ticket_refuse(message):
    args = message.text.split()
    if len(args) != 3:
        bot.send_message(message.chat.id, "Неверное использование команды. Шаблон: /ticket refuse <ticket id>")
    elif User.find_by_conversation(session, message.chat.id).role_id != RoleNames.MANAGER.value:
        bot.send_message(message.chat.id, "Извините, ваша роль не позволяет воспользоваться командой, \
            нужно быть manager/nВаша роль {}".format(RoleNames(User.find_by_conversation(session, message.chat.id).role_id)).name)
    elif not Ticket.get_by_id(session, args[2]):
        bot.send_message(message.chat.id, "Извините, номер данного тикета не найден в базе")

    else:
        user = User.find_by_conversation(session, message.chat.id)


#ответ менеджера на тикет
@bot.message_handler(commands = ["message"])
def manager_answer(message):
    pass

#Команды адмиинистратора:


#отмена операции(удаления менеджера)
@bot.message_handler(commands = ["cancel"])
def cancel(message):
    pass

bot.polling(none_stop=True)
