import telebot
import json
from db import session
from DataBaseClasses import User, Token
import string 
import random
import time
from telebot import apihelper
from telebot import types


cfg = json.load(open("config.json"))
token = cfg['bot']['token']
bot = telebot.TeleBot(token)


#это по идее не нужно
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
#формирование тикета:
def generate_ticket(length = 6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for i in range(length))
#формирование токена: больше запас цифр для надежности(мнимой).
def generate_token(length = 10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for i in range(length))



#cоздание кастомной клавиатуры
def create_su_init_keyboard(buttons):
    keyboard = types.InlineKeyboardMarkup(row_width = 3)
    for x in buttons:
        keyboard.add(types.InlineKeyboardButton(text = x, callback_data = x))
    return keyboard



@bot.message_handler(commands = ["start"])
def start_message(message):
    client = session.query(User).filter(User.id == message.from_user.id)
    if not client:
        session.add(User(id = message.from_user.id, conversation = message.chat.id, name = message.from_user.first_name, role_id = 3))
        session.commit()
        bot.send_message(message.chat.id, "Добро пожаловать в систему <Name_bot>. Для начала работы воспользуйтесь" \
                     " командой /ticket_add.")
    else:
        bot.send_message(message.chat.id, "Вы уже зарегистрированы в системе.  Для начала работы вы можете воспользоваться"\
                         "командой /ticket_add для создания тикета или /ticket_list для просмотра истории Ваших тикетов." )




#вход в систему: менеджер/админ
@bot.message_handler(commands = ["superuser_init"])
def superuser_init(message):
    user = session.query(User).filter(User.id == message.from_user.id)
    keyboard = create_keyboard("Manager", "Admin")
    bot.send_message(message.chat.id, "Добро пожаловать в систему. Выберите свой статус:", reply_markup=keyboard)
    
#это именно вход, не инициализация
#TODO должна быть другая функция декоратора, потому что будет несколько клавиатур
@bot.callback_query_handler(func = lambda x: True)
def callback_handler(callback_query):
    message = callback_query.message
    text = callback_query.data
    if text == "Manager":
        manager = session.query(User).filter(User.id == message.from_user.id)
        if not manager:
            bot.send_message(message.chat.id, "Для начала работы необходимо зарегистрироваться "\
                             "в системе с помощью команды /start."
        elif manager != 2:
            bot.send_message(message.chat.id, "Вы не значитесь в списке менеджеров. Для регистрации в системе " \
                             "в качестве менеджера воспользуйтесь командой /superuser_init.")
        else:
            #А вдруг он уже вошел и пытается войти еще раз?
            bot.send_message(message.chat.id, 'Введите Ваш идентификатор для входа в систему Менеджера:')
    elif text == "Admin":
        #если это первый суперюзер - присвоить случайный токен. Действуем по принципу "кто успеет" (?)
        admin = session.query(User).filter(User.id == message.from_user.id)
        if not admin:
            #Значит администратор первый. Присваиваем случайно токен.
            token = generate_token()
            session.add(Token(value = token, expires_date = time.strftime('%Y-%m-%d %H:%M:%S'), role_id = 1))
            session.add(User(id = message.from_user.id, conversation = None, name = message.from_user.first_name, role_id = 1))
            session.commit()
        elif admin.role_id != 1:
            bot.send_message(message.chat.id, "Вы не значитесь в списке администраторов. Для регистрации в системе " \
                             "в качестве администратора воспользуйтесь командой /superuser_init.")
        else:
            bot.send_message(message.chat.id, 'Введите Ваш идентификатор для входа в систему Администратора:')
        #TODO нужно это как-то отловить из бд messages ответ на это сообщение либо придумать какую-то форму ввода



            
        
#открытие нового тикета
@bot.message_handler(commands = ["ticket_add"])
def create_ticket(message):
    #я не знаю, правильно ли это работает с точки зения бд. Пока так
    #Обатите внимание на title в ticket
    user = User()
    init = session.query(User).filter(User.id == message.chat.id)
    if not init:
        bot.send_message(message.chat.id, "Для того, чтобы создать тикет, необходимо зарегистрироваться в " \
                         "системе. Воспользуйтесь командой /start.")
    else:
        if user.role_id != 1:
            bot.send_message(message.chat.id, "Комманда /ticket_add доступна только для клиентов.")
        else:    
            ticket = generate_ticket()
            bot.send_message(message.chat.id, Person.name + ", опишите ваш вопрос:")
            session.add(Ticket(id = ticket, manager_id = None, client_id = message.from_user.id, \
                               title = "Зачем он нужен? Дальше сообщение ловить надо.", \
                               start_date = time.strftime('%Y-%m-%d %H:%M:%S'), close_date = None))
            session.commit()




#просмотр активных тикетов
@bot.message_handler(commands = ["ticket_list"])
def active_ticket_list(message):
    user = session.query(User).filter(User.id == message.from_user.id)
    if not user:
        bot.send_message(message.chat.id, "Для того, чтобы просмотреть список тикетов, необходимо зарегистрироваться в " \
                         "системе. Воспользуйтесь командой /start или /superuser_init.")
    else:
        bot.send_message(message.chat.id, "Список активных тикетов:\n" + "\n".join(user.get_active_tickets))




@bot.message_handler(commands = ["ticket"])
def chose_ticket(message):
    user = session.query(User).filter(User.id == message.from_user.id)
    if not user:
        bot.send_message(message.chat.id, "Для того, чтобы просмотреть список тикетов, необходимо зарегистрироваться в " \
                         "системе. Воспользуйтесь командой /start или /superuser_init.")
    else:
        bot.send_message(message.chat.id, "Введите номер тикета, на который Вы хотите переключиться.Для просмотра активных "\
                         "тикетов Вы можете воспользоваться командой /ticket_list."
        #TODO Как отловить это сообщение?



#(версия /manager_list Полины) Возможно, это не работает, не тестила на бд, но логика примерно такая
#TODO помещение команд в messages?
@bot.message_handler('/manager_list' in message.text)
def get_manager_list(message):
    admin = User()
    admin = session.query(User).filter(User.id == message.from_user.id)
    if not admin:
        bot.send_message(message.chat.id, "Для того, чтобы воспользоваться командой, необходимо зарегистрироваться в " \
                         "системе. Воспользуйтесь командой /superuser_init.")
    elif admin.role_id != 1:
        bot.send_message(message.chat.id, "Извините, эта команда доступна только для администраторов приложения.")
    else:
        if message.text != "/manager_list":
        bot.send_message(message.chat.id, "Запрос должен состоять только из команды '/manager_list'. Пожалуйста,"\
                         " оформите Ваш запрос корректно.")
        return 
        managers = admin.get_all_managers(session)
        if not managers:
            bot.send_message(message.chat.id,"Менеджеры не найдены. Для добавления воспользуйтесь командой" \
                "/manager create")
        else:
            bot.send_message(message.chat.id, "\n".join(managers))

#(Версия /manager_list Димы)
@bot.message_handler(commands = ["manager list"])
def get_manager_list(message):
    managers = User.get_all_managers(session)
    if not managers:
        bot.send_message(message.chat.id,"Менеджеры не найдены, для добавления воспользуйтесь командой" \
            "/manager create")
    else:
        bot.send_message(message.chat.id, "\n".join(managers))





#Обработка входа в систему.
'''
@bot.message_handler(commands =["start"])
def start(message):
    username = message.from_user.first_name
    user_id = message.from_user.id
    if not User.find_by_conversation(session):
        client = User(name = username, conversation=user_id, role_id=1)
        session.add(client)
        bot.send_message(message.chat.id, "Вы успешно зарегистрировались в системе, {}".format(name))
    else:
        if not User.find_by_conversation(user_id).lower() != username.lower():
            pass
        # Надо изменить имя в БД
        bot.send_message(message.chat.id, "Вы уже зарегистрировались в системе, {}".format(name))
'''



    
@bot.message_handler(func=lambda message: " ".join(message.text.split()[0:2]) == '/superuser init')
def create_superuser(message):
    args = message.text.split()
    if len(args) != 3:
        bot.send_message(message.chat.id, "Неправильное использование команды superuser\nШаблон:/superuser init TOKEN")
        return
    elif len(args[2]) != 6:
        bot.send_message(message.chat.id, "Неправильный размер токена")
    else:
        token_new = args[2]
        # if not Token.check_token: #Проверки + привязка юзера к новой роли 
        #      cur_time =  time.strftime('%Y-%m-%d %H:%M:%S')
        #     token_in_table = Token(value = token_new, expires_date =cur_time, role_id =  )
        #     session.add()


    
@bot.message_handler(func=lambda message: " ".join(message.text.split()[0:2]) == '/manager create')
def create_manager(message):
    if (len(args)) != 2:
        bot.send_message(message.chat.id, "Много аргументов: команда должна быть /manager create")
        return
    token = id_generator()
    bot.send_message(message.chat.id, token)
    cur_time = time.strftime('%Y-%m-%d %H:%M:%S')
    new_token = Token(value = token, role_id = 2, expires_date = cur_time)
    session.add(new_token)
    bot.send_message(message.chat.id, "Токен создан - срок действия 24 часа")




@bot.message_handler(func=lambda message: " ".join(message.text.split()[0:2]) == '/admin create')
def create_admin(message):
    if (len(args)) != 2:
        bot.send_message(message.chat.id, "Много аргументов: команда должна быть /admin create")
        return
        token = id_generator()
        bot.send_message(message.chat.id, token)
        cur_time = time.strftime('%Y-%m-%d %H:%M:%S')
        new_token = Token(value = token, role_id = 1, expires_date = cur_time)
        session.add(new_token)
        bot.send_message(message.chat.id, "Токен создан - срок действия 24 часа")



@bot.message_handler(commands = ["manager_remove"])
def manager_remove(message):
    pass

@bot.message_handler(commands = ["ticket close"])
def close_ticket(message):
    pass

@bot.message_handler(commands = ["cancel"])
def cancel_operation(message):
    pass

@bot.message_handler(commands = ["confirm"])
def confirm_operation(message):
    pass

bot.polling(none_stop=True)
