import telebot
import json

#cfg = json.load(open("config.json"))

token = cfg['bot']['token']
bot = telebot.TeleBot(token)
class States():
    START = "0"
    COMMANDS = "1"
    PROCESS = "2"


from telebot import apihelper
from telebot import types
@bot.message_handler(commands = ["start"])
def keyboard(message):
    keyboard = types.ReplyKeyboardMarkup(row_width = 1)
    itembtn1 = types.KeyboardButton('Admin')
    itembtn2 = types.KeyboardButton('Manager')
    itembtn3 = types.KeyboardButton("Client")
    keyboard.add(itembtn1, itembtn2, itembtn3)
    bot.send_message(message.chat.id, "Выберите свой статус.", reply_markup=keyboard)

#apihelper.proxy = cfg['proxy']

@bot.message_handler(commands = ["superuser init"])
def create_superuser(message):
    pass

@bot.message_handler(content_types=["text"])
def handle_message(message):
    print(message.text)
    bot.send_message(message.chat.id, message.text)

@bot.message_handler(commands = ["manager create"])
def create_manager(message):
    pass

@bot.message_handler(commands = ["admin create"])
def create_admin(message):
    pass
@bot.message_handler(commands = ["manager remove"])
def manager_remove(message):
    pass
@bot.message_handler(commands = ["manager list"])
def get_manager_list(message):
    pass
@bot.message_handler(commands = ["ticket list"])
def get_ticket_list(message):
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
