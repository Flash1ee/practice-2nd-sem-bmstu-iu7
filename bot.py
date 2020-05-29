import telebot
import json
from db import session
from DataBaseClasses import User, Token
import string 
import random
import time

cfg = json.load(open("config.json"))


token = cfg['bot']['token']
bot = telebot.TeleBot(token)


def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


from telebot import apihelper
from telebot import types
'''
@bot.message_handler(commands = ["start"])
def keyboard(message):
    keyboard = types.ReplyKeyboardMarkup(row_width = 1)
    itembtn1 = types.KeyboardButton('Admin')
    itembtn2 = types.KeyboardButton('Manager')
    itembtn3 = types.KeyboardButton("Client")
    keyboard.add(itembtn1, itembtn2, itembtn3)
    bot.send_message(message.chat.id, "Выберите свой статус.", reply_markup=keyboard)
    print(message)
'''


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
    if (len(args)) != 3:
        bot.send_message(message.chat.id, "Неправильное использование команды superuser\nШаблон:/superuser init TOKEN")
        return
    elif len(args[2]) != 6):
        bot.send_message(message.chat.id, "Неправильный размер токена")
    else:
        token_new = args[2]
        # if not Token.check_token: #Проверки + привязка юзера к новой роли 
        #      cur_time =  time.strftime('%Y-%m-%d %H:%M:%S')
        #     token_in_table = Token(value = token_new, expires_date =cur_time, role_id =  )
        #     session.add()
        #     

    
'''
@bot.message_handler(content_types=["text"])
def handle_message(message):
    print(message.text)
    bot.send_message(message.chat.id, message.text)
'''
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
    
@bot.message_handler(commands = ["manager remove"])
def manager_remove(message):
    pass


@bot.message_handler(commands = ["manager list"])
def get_manager_list(message):
    managers = User.get_all_managers(session)
    if not managers:
        bot.send_message(message.chat.id,"Менеджеры не найдены, для добавления воспользуйтесь командой" \
            "/manager create")
    else:
        bot.send_message(message.chat.id, "\n".join(managers))
    


@bot.message_handler(commands = ["ticket list"])
def active_ticket_list(message):
    pass
@bot.message_handler(commands = ["ticket"])
def ticket_info(message):
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
