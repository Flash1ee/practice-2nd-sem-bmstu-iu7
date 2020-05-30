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

class Person:
    def __init__(self):
        self.Start = False
        self.Ticket_add = False
        self.Ticket_add_answer = False
        self.Ticket_list = False
        self.Ticket_close = False
        self.ticket = []
        self.id = -1
        self.name = -1
        self.conversation = -1
        self.role_id = -1   
    def start_update(data):
        self.Start = True
        self.id = data[0]
        self.name = data[1]
        self.conversation = data[2]
        self.role_id = data[3]
    def ticket_add(self, ticket):
        self.ticket.append(ticket)

def generate_ticket(length = 6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for i in range(length))

def create_su_init_keyboard(buttons):
    keyboard = types.InlineKeyboardMarkup(row_width = 3)
    for x in buttons:
        keyboard.add(types.InlineKeyboardButton(text = x, callback_data = x))
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
        
        #если не первый:
        bot.send_message(message.chat.id, 'Введите Ваш идентификатор для входа в систему Администратора:')
        #нужно состояние админа, ввел ли он идентификатор - люди с BD?
        #TODO показать панель админа, если он авторизовался(нужно состояние)

@bot.message_handler(commands = ["start"])
def start_message(message):
    #TODO проверить, уникальный ли юзер? Может быть дублирование
    #Добавление в бд: (пока непонятно, кто этим занимается. Навеное, должен быть метод)
    #session.add(User(id = message.from_user.id, conversation = message.chat.id, name = message.from_user.first_name, role_id = 2))
    #session.commit()
    #Это багофича(инициализурую пока, как могу. В идеале нужны методы с бд):
    Person.start_update([message.from_user.id, message.chat.id, message.from_user.first_name, 2])
    bot.send_message(message.chat.id, "Добро пожаловать в систему <Name_bot>. Для начала работы воспользуйтесь" \
                     " командой /ticket_add.")
    #test = session.query(User)[0]
    #print(test.id)

#вход в систему: менеджер/админ
@bot.message_handler(commands = ["superuser_init"])
def superuser_init(message):
    keyboard = create_keyboard("Manager", "Admin")
    bot.send_message(message.chat.id, "Добро пожаловать в систему. Выберите свой статус:", reply_markup=keyboard)
    
@bot.message_handler(commands = ["ticket_add"])
def create_ticket(message):
    if Person.Start == True:
        Person.Ticket_add = True
        ticket = generate_ticket()
        bot.send_message(message.chat.id, Person.name + ", пишите ваш вопрос:")
        Person.ticket_add(ticket)
    else:
        bot.send_message(message.chat.id, "Для того, чтобы создать тикет, необходимо зарегистрироваться в " \
                         "системе. Воспользуйтесь командой /start.")

@bot.message_handler(commands = ["ticket_close"])
def create_ticket(message):
    bot.send_message(message.chat.id, "TODO:")

@bot.message_handler(commands = ["ticket_id"])
def create_ticket(message):
    bot.send_message(message.chat.id, "TODO:")

@bot.message_handler(commands = ["ticket_list"])
def create_ticket(message):
    bot.send_message(message.chat.id, "TODO:")
        
@bot.message_handler(content_types=['text'])
@bot.edited_message_handler(content_types = ['text'])
def handle_message(message):
    #тест, надо брать из бд
    #нужно состояние, вызвана ли команда /ticket_add, не задан ли вопрос от клиента, вошел ли пользователь в систему и тд
    if Person.Start == False:
        bot.send_message(message.chat.id, "Чтобы войти в систему, воспользуйтесь командой /start.")
    elif Person.Ticket_add == False:
        bot.send_message(message.chat.id, "Для того, чтобы задать вопрос, создайте тикет с помощью команды /start")
    elif Prson.Ticket_add_answer == False:
        Prson.Ticket_add_answer = True
        bot.send_message(message.chat.id, "Опишите Ваш вопрос: \n" + message.text)
    else:
        bot.send_message(message.chat.id, "Echo")

#def get_updates():
    #r = requests.get(MAIN_URL + token + "/getUpdates" + "?offset=-10")
    #print(r.json())

bot.polling(none_stop=True)
