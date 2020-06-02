import telebot
import json
from db import session
from models.DataBaseClasses import User, Token
import string 
import random
import time
from telebot import apihelper
from telebot import types
from models.DataBaseClasses import *

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
    print(User.get_all_users_with_role(session, RoleNames.ADMIN.value))
    if not User.get_all_users_with_role(session, RoleNames.ADMIN.value):
        #если нет никого из юзеров и этого пользователя нет в бд - назначаем админом
        if User.find_by_conversation(session, chat_id) == None:
            cur_role = RoleNames.ADMIN.value
        #если нет админов, но есть другие юзеры, назначаем админом того, кто обратился.
        else:
            user = User.find_by_conversation(session, chat_id)
            user.role_id = 1
            cur_role = 1
            user.add(session)
    elif User.find_by_conversation(session, chat_id) == None:
        cur_role = RoleNames.CLIENT.value
    #если назначена новая роль
    if cur_role:
        #добавляем сведения в бд
        client = User()
        client.role_id = cur_role
        client.name = username
        client.conversation = chat_id
        client.add(session)
        bot.send_message(message.chat.id, "{}, Вы успешно зарегистрировались в системе.\nВаш статус - {}".format(username, RoleNames(cur_role).name))
    else:
        #пользователь уже зарегистрирован
        user = User.find_by_conversation(session, message.chat.id)
        if user.name.lower() != username.lower():
            user.change_name(session, username, user_id = chat_id)
        bot.send_message(message.chat.id, "{}, Вы уже зарегистрировались в системе.\nВаш статус - {}".format(username, RoleNames(user.role_id).name))

        


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
        my_token = Token.find(session, token_new)
        if my_token:
            user.appoint(session,my_token.role_id)
            my_token.activate(session, token_new)
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
        if user.role_id != 3:
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
def get_ticket_body(message):
    bot.send_message(message.chat.id, "Ваш запрос обрабатывается...")
    user = User.find_by_conversation(session, message.chat.id)
    ticket = user.get_active_tickets(session)[0]
    #теперь нужно назначить менеджера
    manager = User.get_free_manager(session)
    if manager:
        Message.add(session, message.text, ticket.id, message.chat.id)





#просмотр активных тикетов
@bot.message_handler(commands = ["ticket_list"])
def active_ticket_list(message):
    user = User.find_by_conversation(session, conversation = message.chat.id)
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
            ans += "Cleint_id: " + str(x.client_id) + '\n'
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
            ans += "Cleint_id: " + str(x.client_id) + '\n'
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
    else:
        bot.register_next_step_handler(message, switch_for_client)
        bot.send_message(message.chat.id, "Введите номер тикета, на который Вы хотите переключиться. Для просмотра активных "\
                         "тикетов Вы можете воспользоваться командой /ticket_list, а затем снова /ticket_id.")


def switch_for_client(message):
    if message.text == "/ticket_list":
        active_ticket_list(message)
    else:
        ticket_id = message.text
        #корректность тикета:
        all_tickets = session.query(Ticket).filter(Ticket.id == ticket_id).first()
        if all_tickets == None:
            bot.send_message(message.chat.id, "Введен некоторектный ticket_id. Пожалуйста, попробуйте еще раз.")
        else:
            user = User.find_by_conversation(session, message.chat.id)
            user.manager_id = all_tickets.manager_id
            bot.send_message(message.chat.id, "Тикет успешно выбран. В ближайшем времени с Вами свяжется менеджер.")
            #TODO торкнуть менеджера



@bot.message_handler(commands = ["ticket_close"])
def close_ticket(message):
    user = User.find_by_conversation(session, message.chat.id)
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
            "/manager create")
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





'''
#TODO TOMMOROW
@bot.message_handler(content_types = ['text'])
def confirm(args):
    print(args) 
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text = "Да", callback_data = 'yes')
    keyboard.add(key_yes)
    key_no = types.InlineKeyboardButton(text = "Нет", callback_data = 'no')
    keyboard.add(key_no)
    bot.send_message(args[0].chat.id, "Вы действительно хотите сделать это?", reply_markup=keyboard)
    @bot.callback_query_handler(func = lambda call: True)
    def caller_worker(call):
        if call.data == "yes":
            args[1].demote_manager(session)
            bot.send_message(args[0].chat.id, "Менеджер с id {} удалён".format(args[2]))
        elif call.data == "no":
            bot.send_message(args[0].chat.id, "Отменяем операцию удаления")
#удаление менеджера
@bot.message_handler(func=lambda message: " ".join(message.text.split()[0:2]) == '/manager remove')
def manager_remove(message):
    args = message.text.split()
    user = User.find_by_conversation(session, conversation = message.chat.id)
    if not user:
        bot.send_message(message.chat.id, "Сначала нужно зарегистрироваться, воспользуйтесь командой /start")
    elif len(args) != 3:
        bot.send_message(message.chat.id, "Неверное использование команды. Шаблон: /manager remove <manager id>")
    elif user.role_id != RoleNames.ADMIN.value:
        bot.send_message(message.chat.id,"Извините, эта команда доступна только для администраторов приложения.")
    else:
        manager_id = args[2]
        manager = User.find_by_conversation(session, manager_id)
        if not manager:
            bot.send_message(message.chat.it, "Менеджеров с таким id не найдено в базе данных.")
        else:
            bot.register_next_step_handler([message, manager, manager_id], confirm)
'''




#cоздание кастомной клавиатуры
def create_su_init_keyboard(buttons):
    keyboard = types.InlineKeyboardMarkup(row_width = 3)
    for x in buttons:
        keyboard.add(types.InlineKeyboardButton(text = x, callback_data = x))
    return keyboard




#TODO команды менеджера:
#отказ менеджера от тикета
@bot.message_handler(commands = ["ticket_refuse"])
def ticket_refuse(message):
    pass

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
