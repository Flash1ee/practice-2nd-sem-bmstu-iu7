from models.DataBaseClasses import *
from telebot import apihelper
from telebot import types
from telegram_bot_pagination import InlineKeyboardPaginator
def init(bot):

    @bot.message_handler(commands=["manager_list"])
    def get_manager_list(message):
        """
            Получение списка менеджеров
        """
        args = message.text.split()
        user = message.user
        if not user:
            bot.send_message(
                message.chat.id, "Сначала нужно зарегистрироваться, воспользуйтесь командой /start")
        elif user.role_id != RoleNames.ADMIN.value:
            bot.send_message(
                message.chat.id, "Извините, эта команда доступна только для администраторов приложения.")
        else:
            managers = User.get_all_users_with_role(
                message.session, RoleNames.MANAGER.value)
            if not managers:
                bot.send_message(message.chat.id, "Менеджеры не найдены, для добавления воспользуйтесь командой"
                                                " /manager create")
            else:
                for number, manager in enumerate(managers, start=1):
                    bot.send_message(
                        message.chat.id, f"№{number} Имя - {manager.name}, id - {manager.conversation}")
    @bot.message_handler(commands=["manager_remove"])
    def manager_remove(message):
        """
            Удаление менеджера (разжалование)
        """
        args = message.text.split()
        user = message.user
        if not user:
            bot.send_message(
                message.chat.id, "Сначала нужно зарегистрироваться, воспользуйтесь командой /start")
        elif len(args) != 2:
            bot.send_message(
                message.chat.id, "Неверное использование команды. Шаблон: /manager_remove <manager id>")
        elif user.role_id != RoleNames.ADMIN.value:
            bot.send_message(
                message.chat.id, "Извините, эта команда доступна только для администраторов приложения.")
        else:
            """
                Что тут происходит?
                Красота
            """
            global manager_id
            manager_id = args[1]
            manager = User.find_by_conversation(message.session, manager_id)
            if not manager or manager.role_id != RoleNames.MANAGER.value:
                bot.send_message(
                    message.chat.id, "Менеджеров с таким id не найдено в базе данных.")
            else:
                keyboard = types.InlineKeyboardMarkup()
                key_yes = types.InlineKeyboardButton(
                    text="Да", callback_data='yes')
                keyboard.add(key_yes)
                key_no = types.InlineKeyboardButton(text="Нет", callback_data='no')
                keyboard.add(key_no)
                bot.send_message(
                    message.chat.id, "Вы действительно хотите сделать это?", reply_markup=keyboard)

                @bot.callback_query_handler(func=lambda call: True)
                def caller_worker(call):
                    global manager_id
                    manager = User.find_by_conversation(message.session, manager_id)
                    if call.data == "yes":
                        bot.edit_message_text(chat_id = call.message.chat.id,
                            message_id=call.message.message_id, text="Принято, ожидайте!\nИдёт перераспределение тикетов.")
                        if manager.demote_manager(message.session) == -1:
                            bot.send_message(message.chat.id,
                            f"Мы не можем удалить менеджера\n с id {manager_id}\nОн единственный =>\n"
                            "распределить его тикеты\nнекому. ")
                        else:
                            bot.send_message(
                            message.chat.id, f"Менеджер с id {manager_id} удалён")
                    elif call.data == "no":
                        bot.edit_message_text(chat_id = call.message.chat.id, message_id=call.message.message_id, text="Принято!")
                        bot.send_message(
                            message.chat.id, "Отменяем операцию удаления.")

    def describe(message):
        """
            Описание причины отказа от тикента менеджера
        """
        if not message.text:
            bot.send_message(message.chat.id, "Описание отказа от тикета обязательно.\n \
                Опишите причину закрытия тикета\n")
            bot.register_next_step_handler(message, describe)
        else:
            global tick_id
            ticket = Ticket.get_by_id(message.session, tick_id)
            ticket.put_refuse_data(message.session, message.text)
            ticket.reappoint(message.session)
            bot.send_message(message.chat.id, f"Вы отказались от тикета {tick_id}\n")


    @bot.message_handler(commands=["ticket_refuse"])
    def ticket_refuse(message):
        """
            Команда отказа менеджера от тикета
        """
        args = message.text.split()
        user = message.user
        chat = message.chat.id
        if len(args) != 2:
            bot.send_message(
                chat, "Неверное использование команды. Шаблон: /ticket_refuse <ticket id>")
        elif user.role_id != RoleNames.MANAGER.value:
            bot.send_message(chat, f"Извините, ваша роль не позволяет воспользоваться командой, \
                нужно быть manager/nВаша роль {RoleNames(User.find_by_conversation(message.session, chat).role_id).name}")
        elif not Ticket.get_by_id(message.session, args[1]):
            bot.send_message(chat, "Извините, номер данного тикета не найден в базе")
        else:
            global tick_id
            tick_id = args[1]
            bot.send_message(chat, "Опишите причину закрытия тикета\n")
            bot.register_next_step_handler(message, describe)

        return markup

