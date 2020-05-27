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

def create_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width = 3)
    key1 = types.InlineKeyboardButton(text = "Client", callback_data = "Client")
    key2 = types.InlineKeyboardButton(text = "Manager", callback_data = "Manager")
    key3 = types.InlineKeyboardButton(text = "Admin", callback_data = "Admin") 
    keyboard.add(key1, key2, key3)
    return keyboard

@bot.callback_query_handler(func = lambda x: True)
def callback_handler(callback_query):
    message = callback_query.message
    text = callback_query.data
    if text == "Client":
        #Ticket.client_id = message.chat.id
        bot.send_message(message.chat.id, 'Вы зарегистрированы в системе как клиент.')
        bot.send_message(message.chat.id, 'Для дальнейшей работы воспользуйтесь командой /ticket_add.')
    if text == "Manager":
        bot.send_message(message.chat.id, 'Вы зарегистрированы в системе как менеджер.')
    if text == "Admin":
        bot.send_message(message.chat.id, 'Вы зарегистрированы в системе как администратор.')
    State.start = True
    State.add_ticket = False
    State.ask_question = False

@bot.message_handler(commands = ["start"])
def start_message(message):
    keyboard = create_keyboard()
    bot.send_message(message.chat.id, "Выберите свой статус:", reply_markup=keyboard)

#def get_updates():
    #r = requests.get(MAIN_URL + token + "/getUpdates" + "?offset=-10")
    #print(r.json())
    
@bot.message_handler(commands = ["ticket_add"])
def create_ticket(message):
    ticket = generate_ticket()
    if State.start == False:
        bot.send_message(message.chat.id, "Для того, чтобы задать вопрос, создайте тикет с помощью команды /start")
    else:
        State.add_ticket = True
        bot.send_message(message.chat.id, "Опишите Ваш вопрос:")
        
@bot.message_handler(content_types=['text'])
@bot.edited_message_handler(content_types = ['text'])
def handle_message(message):
    #тест, надо брать из бд
    if State.start == False:
        bot.send_message(message.chat.id, "Для начала работы воспользуйтесь командой /start.")
    elif State.add_ticket == False:
        bot.send_message(message.chat.id, "Для того, чтобы задать вопрос, создайте тикет с помощью команды /start")
    elif State.ask_question == False:
        State.ask_question = True
        bot.send_message(message.chat.id, "Ваш вопрос: \n" + message.text)
    else:
        bot.send_message(message.chat.id, "Echo")

bot.polling(none_stop=True)
