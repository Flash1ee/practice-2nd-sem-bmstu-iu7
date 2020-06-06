from models.DataBaseClasses import *

def init(bot):
    #Открытие нового тикета.
    @bot.message_handler(commands = ["ticket_add"])
    def create_ticket(message):
        user = message.user
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
        user = message.user
        bot.send_message(message.chat.id, "Отлично. Теперь опишите Ваш вопрос более детально: ")
        if Ticket.create(message.session, message.text, message.chat.id) == 1:
            bot.send_message(message.chat.id, user.name + ", извините, в системе нет ни одного менеджера. Пожалуйста, обратитесь спустя пару минут.")
        else:
            bot.register_next_step_handler(message, get_ticket_body)
    def get_ticket_body(message):
        user = message.user
        Message.add(message.session, message.text, user.get_active_tickets(message.session)[0].id, message.chat.id)
        Message.add(message.session, "/ticket_add", None, message.chat.id)
        bot.send_message(message.chat.id, "Ваш вопрос успешно отправлен. В ближайшем времени с Вами свяжется менеджер.")

    
