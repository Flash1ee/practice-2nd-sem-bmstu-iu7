import telebot
import json
from db import session
from DataBaseClasses import User, Token
import string 
import random
import datetime
from telebot import apihelper
from telebot import types

cfg = json.load(open("config.json"))

token = cfg['bot']['token']
bot = telebot.TeleBot(token)

class State():
    start = False
    add_ticket = False
    ask_question = False

def generate_ticket(length = 6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for i in range(length))

def create_su_init_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width = 3)
    key1 = types.InlineKeyboardButton(text = "Manager", callback_data = "Manager")
    key2 = types.InlineKeyboardButton(text = "Admin", callback_data = "Admin") 
    keyboard.add(key1, key2)
    return keyboard

@bot.callback_query_handler(func = lambda x: True)
def callback_handler(callback_query):
    message = callback_query.message
    text = callback_query.data
    if text == "Manager":
        bot.send_message(message.chat.id, 'Введите Ваш идентификатор для входа в систему Менеджера:')
        #нужно состояние менеджера, ввел ли он идентификатор - люди с BD?
        #TODO показать панель менеджера, если он авторизовался(нужно состояние)
    elif text == "Admin":
        #если это первый суперюзер - идентифицировать - как?
        #если не второй:
        bot.send_message(message.chat.id, 'Введите Ваш идентификатор для входа в систему Администратора:')
        #нужно состояние админа, ввел ли он идентификатор - люди с BD?
        #TODO показать панель админа, если он авторизовался(нужно состояние)

@bot.message_handler(commands = ["start"])
def start_message(message):
    #TODO проверить, уникальный ли юзер? Может быть дублирование
    session.add(User(id = message.from_user.id, conversation = message.chat.id, name = message.from_user.first_name, role_id = 2))
    session.commit()
    bot.send_message(message.chat.id, "Добро пожаловать в систему <Name_bot>. Для начала работы воспользуйтесь" \
                     " командой /ticket_add.") 

#вход в систему: менеджер/админ
@bot.message_handler(commands = ["superuser_init"])
def superuser_init(message):
    keyboard = create_keyboard()
    bot.send_message(message.chat.id, "Добро пожаловать в систему. Выберите свой статус:", reply_markup=keyboard)
    
@bot.message_handler(commands = ["ticket_add"])
def create_ticket(message):
    ticket = generate_ticket()
    #нужно состояние, вошел ли пользователь в систему
    bot.send_message(message.chat.id, "Опишите Ваш вопрос:")
        
@bot.message_handler(content_types=['text'])
@bot.edited_message_handler(content_types = ['text'])
def handle_message(message):
    #тест, надо брать из бд
    #нужно состояние, вызвана ли команда /ticket_add, не задан ли вопрос от клиента, вошел ли пользователь в систему
    if State.start == False:
        bot.send_message(message.chat.id, "Чтобы войти в систему, воспользуйтесь командой /start.")
    elif State.add_ticket == False:
        bot.send_message(message.chat.id, "Для того, чтобы задать вопрос, создайте тикет с помощью команды /start")
    elif State.ask_question == False:
        State.ask_question = True
        bot.send_message(message.chat.id, "Опишите Ваш вопрос: \n" + message.text)
    else:
        bot.send_message(message.chat.id, "Echo")

#def get_updates():
    #r = requests.get(MAIN_URL + token + "/getUpdates" + "?offset=-10")
    #print(r.json())

bot.polling(none_stop=True)
