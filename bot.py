import telebot
import json

cfg = json.load(open("./config.json"))

token = cfg['bot']['token']
bot = telebot.TeleBot(token)


from telebot import apihelper


apihelper.proxy = cfg['proxy']

@bot.message_handler(commands = "superuser init")
def create_superuser(message):
    pass

@bot.message_handler()
def handle_message(message):
    print(message.text)

@bot.message_handler(commands = "manager create")
def create_manager(message):
    pass

@bot.message_handler(commands = "admin create")
def create_admin(message):
    pass
@bot.message_handler(commands = "manager remove")
def manager_remove(message):
    pass
@bot.message_handler(commands = "manager list")
def get_manager_list(message):
    pass
@bot.message_handler(commands = "ticket list")
def get_ticket_list(message):
    pass
@bot.message_handler(commands = "ticket")
def ticket_info(message):
    pass
@bot.message_handler(commands = "ticket close")
def close_ticket(message):
    pass

@bot.message_handler(commands = "cancel")
def cancel_operation(message):
    pass

@bot.message_handler(commands = "confirm")
def confirm_operation(message):
    pass





























if __name__ == "__main__":
    bot.polling(none_stop = True)