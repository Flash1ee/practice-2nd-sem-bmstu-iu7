"""
    Файл основной логики бота 
"""
import json

import telebot
from telebot import apihelper
from telebot import types
from telegram_bot_pagination import InlineKeyboardPaginator

import ClientController
import CommonController
import ManagerController
from db import Session
from models.DataBaseClasses import *

cfg = json.load(open("config.json"))
token = cfg['bot']['token']
bot = telebot.TeleBot(token)

#if 'proxy' in cfg.keys():
#    apihelper.proxy = cfg['proxy_3']

apihelper.ENABLE_MIDDLEWARE = True


@bot.middleware_handler(update_types=['message'])
def session_middleware(bot_instance, message):
    """
        Установка сессии БД
    """
    print("session UPDATE")
    message.session = Session()


@bot.middleware_handler(update_types=['message'])
def auth_middleware(bot_instance, message):
    """
        Авторизация пользователя
    """
    chat_id = message.chat.id
    message.user = User.find_by_conversation(message.session, chat_id)
    if message.user:
        print(f"Conversation UPDATE: {chat_id}, {message.user.name}")


@bot.middleware_handler(update_types=['message'])
def set_empty_text_middleware(bot_instance, message):
    """
        Фиксим отсутствие поля text
    """
    if not message.text:
        message.text = ''


CommonController.init(bot)
ClientController.init(bot)
ManagerController.init(bot)


@bot.message_handler(commands = ["ticket_add"])
def create_ticket(message):
    """
        Открытие нового тикета
    """
    user = message.user
    if not user:
        bot.send_message(message.chat.id, "Для того, чтобы создать тикет, необходимо зарегистрироваться в " \
                        "системе. Воспользуйтесь командой /start.",reply_markup = types.ReplyKeyboardRemove())
    else:
        if user.role_id != RoleNames.CLIENT.value:
            bot.send_message(message.chat.id, "Комманда /ticket_add доступна только для клиентов.", reply_markup = types.ReplyKeyboardRemove())
            manager_answer(message)
        else:    
            bot.send_message(message.chat.id, user.name + ", для начала кратко сформулируйте Вашу проблему:")
            bot.register_next_step_handler(message, get_title)
def get_title(message):
    """
        Получение заголовка тикета
    """
    user = message.user
    if message.text == "Назад":
        bot.send_message(message.chat.id, "Отмена операции...")
        manager_answer(message)
        return
    bot.send_message(message.chat.id, "Ожидайте, ищем менеджера...")
    new_ticket = Ticket.create(message.session, message.text, message.chat.id)
    if not new_ticket:
        bot.send_message(message.chat.id, user.name + ", извините, в системе нет ни одного менеджера. Пожалуйста, обратитесь спустя пару минут.",reply_markup = types.ReplyKeyboardRemove())
        return
    bot.send_message(message.chat.id, "Отлично. Теперь опишите Ваш вопрос более детально: ")
    bot.register_next_step_handler(message, get_ticket_body, new_ticket.id)
def get_ticket_body(message, ticket_id: int):
    """
        Получение описания тикета
    """
    Message.add(message.session, message.text, ticket_id, message.chat.id)
    bot.send_message(message.chat.id, "Ваш вопрос успешно отправлен. В ближайшем времени с Вами свяжется менеджер.",reply_markup = types.ReplyKeyboardRemove())


# вход в систему менеджера/админа
@bot.message_handler(commands=["superuser_init"])
def create_superuser(message):
    """
        Добавление роли пользователю по токену
    """
    args = message.text.split()
    user = message.user
    user = User.find_by_conversation(message.session,message.chat.id)
    if not user:
        bot.send_message(message.chat.id, "Сначала нужно зарегистрироваться, воспользуйтесь командой /start.")
    elif len(args) != 2:
        bot.send_message(
            message.chat.id, "Неправильное использование команды superuser.\nШаблон:/superuser_init TOKEN")
    elif not Token.find(message.session, args[1]):
        bot.send_message(message.chat.id, "Данный токен не существует. Попробуйте еще раз.")
    else:
        token_new = args[1]
        my_token = Token.find(message.session, token_new)
        if my_token:
            user.appoint(message.session, my_token.role_id)
            my_token.activate(message.session)
            bot.send_message(
                message.chat.id, f"Токен успешно активирован, ваша роль {RoleNames(my_token.role_id).name}.")
        else:
            bot.send_message(
                message.chat.id, "Не удалось авторизоваться в системе. Попробуйте еще раз.")

# Просмотр активных тикетов.
@bot.message_handler(commands=["ticket_list"])
def active_ticket_list(message):
    user = message.user
    if user:
        message = bot.send_message(message.chat.id, "Формирую список тикетов...")
        send_active_ticket_list_paginator(message)
    else:
        bot.send_message(message.chat.id, "Для того, чтобы просмотреть список тикетов, необходимо зарегистрироваться в "
                                          "системе. Воспользуйтесь командой /start или /superuser_init.")

@bot.callback_query_handler(func=lambda call: call.data.split('#')[0]=='active_ticket')
def characters_page_callback(call):
    page = int(call.data.split('#')[1])
    send_active_ticket_list_paginator(call.message, page)

def send_active_ticket_list_paginator(message, page=1):
    ans = ''
    session = Session()
    user = User.find_by_conversation(session, message.chat.id)
    if RoleNames(user.role_id).name in ('CLIENT', "ADMIN"):
        all_tickets = user.get_all_tickets(session)
        all_tickets = sorted(all_tickets,
                                key=lambda x: x.close_date if x.close_date else datetime(year=2020, month=1, day=1))
    else:
        all_tickets = user.get_active_tickets(session)
        all_tickets = sorted(all_tickets, key=lambda w: w.get_wait_time(session), reverse=True)
    step = 3
    if all_tickets:
        paginator = InlineKeyboardPaginator(
            (len(all_tickets) - 1)// step + 1,
            current_page=page,
            data_pattern='active_ticket#{page}'
        )
        for i in range((page-1)*step + 1, page*step + 1):
            if i <= len(all_tickets):
                ticket = all_tickets[i - 1]
                ans += 'Ticket id: ' + str(ticket.id) + '\n'
                ans += 'Title: ' + ticket.title + '\n'
                ans += "Start date: " + str(ticket.start_date) + '\n'

                if RoleNames(user.role_id).name == "ADMIN":
                    ans += 'Manager_id: ' + str(ticket.manager_id) + '\n'
                    ans += "Client_id: " + str(ticket.client_id) + '\n'
                    ans += "Wait time: " + str(ticket.get_wait_time(session)) + "\n"

                if RoleNames(user.role_id).name == "MANAGER":
                    ans += "Client_id: " + str(ticket.client_id) + '\n'
                    ans += "Wait time: " + str(ticket.get_wait_time(session)) + "\n"

                if RoleNames(user.role_id).name in ('CLIENT', "ADMIN"):
                    ans += 'Status: '
                    if ticket.close_date:
                        ans += "Тикет закрыт.\nClose date: " + str(ticket.close_date) + '\n'
                    else:
                        ans += 'Тикет активен. \n'
                ans += '=' * 10 + '\n'

        ans = f'Тикеты {(page-1)*step + 1} - {min(page*step, len(all_tickets))}\n\n' + '=' * 10 + '\n' + ans
        bot.edit_message_text(
            ans,
            message.chat.id,
            message.message_id,
            reply_markup=paginator.markup  
        )
    else:
        if RoleNames(user.role_id).name == 'CLIENT':
            bot.edit_message_text("У вас нет тикетов. Для создания тикета воспользуйтесь кнопкой 'Создать тикет.'", 
                message.chat.id,
                message.message_id)
        else:
            bot.edit_message_text("За Вами еще не закреплен ни один тикет.", 
                message.chat.id,
                message.message_id)
    session.close()

@bot.message_handler(commands=["ticket_id"])
def chose_ticket(message):
    user = message.user
    if not user:
        bot.send_message(message.chat.id, "Для того, чтобы просмотреть список тикетов, необходимо зарегистрироваться в " \
                                          "системе. Воспользуйтесь командой /start или /superuser_init.")
    elif user.role_id == RoleNames.CLIENT.value:
        bot.send_message(message.chat.id,
                         "Введите номер тикета, на который Вы хотите переключиться. Чтобы посмотреть список " \
                         "активных тикетов, Вы можете воспользоваться командой /ticket_list, а затем снова /ticket_id.")
        bot.register_next_step_handler(message, switch_for_client)
    else:
        bot.send_message(message.chat.id, "Введите номер тикета, который Вы хотите просмотреть. Для просмотра активных " \
                                          "тикетов Вы можете воспользоваться кнопкой 'Список моих тикетов'.")
        bot.register_next_step_handler(message, switch_for_superuser)


def switch_for_client(message):
    if message.text == "/ticket_list":
        active_ticket_list(message)
    else:
        if Ticket.get_by_id(message.session, message.text) is None:
            bot.send_message(message.chat.id, "Введен некоторектный ticket_id. Пожалуйста, попробуйте еще раз.")
        else:
            bot.send_message(message.chat.id, "Тикет успешно выбран. В ближайшем времени с Вами свяжется менеджер.")


def switch_for_superuser(message):
    chat_id = message.chat.id
    if message.text == "/ticket_list":
        active_ticket_list(message)
    else:
        ticket = Ticket.get_by_id(message.session, message.text)
        if Ticket.get_by_id(message.session, message.text) is None:
            bot.send_message(message.chat.id, "Введен некорректный ticket_id. Пожалуйста, попробуйте еще раз.")
        else:
            ans = "Информация для ticket_id " + str(ticket.id) + ":\n\n"
            ans += 'Title: ' + ticket.title + '\n' + 'Manager_id: '
            if ticket.manager_id is None:
                ans += "Менеджер еще не найден. Поиск менеджера..." + '\n'
            else:
                ans += str(ticket.manager_id) + '\n'
            ans += "Client_id: " + str(ticket.client_id) + '\n'
            ans += "Start date: " + str(ticket.start_date) + '\n\n'
            bot.send_message(chat_id, ans)
            messages = ticket.get_all_messages(message.session, ticket.id)
            if not messages:
                bot.send_message(chat_id, "История переписки пустая.")
            ans = "История переписки:\n\n"
            for msg in messages:
                ans += str(msg.date) + "\n"
                role = User.find_by_id(message.session, msg.sender_id).role_id
                ans += RoleNames(role).name + ": " + msg.body + "\n\n"
                bot.send_message(chat_id, ans)
                ans = ''


'''
#Закрытие тикета.
'''


@bot.message_handler(commands=["ticket_close"])
def close_ticket(message):
    """
        Закрытие тикета клиентом
    """
    if not message.user:
        bot.send_message(message.chat.id, "Для того, чтобы закрыть тикет, необходимо зарегистрироваться в " \
                                          "системе. Воспользуйтесь командой /start или /superuser_init.")
    elif message.user.role_id == RoleNames.MANAGER.value:
        bot.send_message(message.chat.id, "Данная команда не предназначена для менеджеров. Воспользуйтесь командой " \
                                          "/help, чтобы просмотреть список возможных команд.")
    else:
        bot.send_message(message.chat.id, "Введите номер тикета, который Вы хотите закрыть.")
        bot.register_next_step_handler(message, ticket_close)


def ticket_close(message):
    """
        Обработка закрытия тикета
    """
    if message.text == "Назад":
        bot.send_message(message.chat.id, "Возвращаемся...")
        manager_answer(message)
        return
    ticket = Ticket.get_by_id(message.session, message.text)
    if not ticket or User.find_by_conversation(message.session, message.chat.id).id != ticket.client_id:
        bot.send_message(message.chat.id, "Введен некорректный номер тикета. Команда прервана.\nПовторите попытку.",reply_markup = types.ReplyKeyboardRemove())
    elif User.find_by_id(message.session, ticket.client_id).role_id == RoleNames.ADMIN.value:
        bot.send_message(message.chat.id,
                         f"Тикет {message.text} был закрыт по решению администратора. Для уточнения информации " \
                         "обратитесь к менеджеру.", reply_markup = types.ReplyKeyboardRemove())
    elif ticket.close_date:
        bot.send_message(message.chat.id, "Тикет уже закрыт.", reply_markup = types.ReplyKeyboardRemove())
    else:
        bot.send_message(message.chat.id, "Тикет успешно закрыт.", reply_markup = types.ReplyKeyboardRemove())
        ticket.close(message.session)


@bot.message_handler(commands=["manager_create"])
def create_manager(message):
    """
        Создание токена нового менеджера
    """
    args = message.text.split()
    user = message.user
    if not user:
        bot.send_message(
            message.chat.id, "Сначала нужно зарегистрироваться, воспользуйтесь командой /start.")
    elif (len(args)) != 1:
        bot.send_message(
            message.chat.id, "Много аргументов: команда должна быть /manager_create.")
    else:
        if user.role_id != RoleNames.ADMIN.value:
            bot.send_message(
                message.chat.id, f"Извините. У вас недостаточно прав, вы - {RoleNames(user.role_id).name}.")
        else:
            new_token = Token.generate(message.session, RoleNames.MANAGER.value)
            bot.send_message(
                message.chat.id, f"{new_token.value}\nТокен создан - срок действия 24 часа.")


@bot.message_handler(commands=["admin_create"])
def create_admin(message):
    """
        Создание токена нового админа
    """
    args = message.text.split()
    user = message.user
    if not user:
        bot.send_message(
            message.chat.id, "Сначала нужно зарегистрироваться, воспользуйтесь командой /start")
    elif (len(args)) != 1:
        bot.send_message(
            message.chat.id, "Много аргументов: команда должна выглядеть так /admin_create")
    else:
        if user.role_id != RoleNames.ADMIN.value:
            bot.send_message(
                message.chat.id, f"Извиите. У вас недостаточно прав, вы - {RoleNames(user.role_id).name}")
        else:
            new_token = Token.generate(message.session, RoleNames.ADMIN.value)
            bot.send_message(
                message.chat.id, f"{new_token.value}\nТокен создан - срок действия 24 часа")


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


@bot.message_handler(commands=["role"])
def check_role(message):
    """
        Команда выводит текущую роль пользователя
    """
    user = message.user
    if not user:
        bot.send_message(
            message.chat.id, "Сначала нужно зарегистрироваться, воспользуйтесь командой /start")
    else:
        bot.send_message(
            message.chat.id, f"Ваша текущая роль - {RoleNames(user.role_id).name}")


# удаление менеджера
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
        if not manager:
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
                    manager.demote_manager(message.session)
                    bot.send_message(
                        message.chat.id, f"Менеджер с id {manager_id} удалён")
                elif call.data == "no":
                    bot.send_message(
                        message.chat.id, "Отменяем операцию удаления.")


# отказ менеджера от тикета

def describe(message):
    if not message.text:
        bot.send_message(chat, "Описание отказа от тикета обязательно.\n \
            Опишите причину закрытия тикета\n")
        bot.register_next_step_handler(message, describe)
    else:
        global tick_id
        ticket = Ticket.get_by_id(session,tick_id)
        ticket.put_refuse_data(session, message.text)
        ticket.reappoint(session)
        bot.send_message(message.chat.id, f"Вы отказались от тикета {tick_id}\n"
        "Для проверки воспользуйтесь командой /ticket_list")

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
        Коммманда отказа менеджера от тикета
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


def write_message(message):
    ticket_id = message.text
    user = message.user
    try:
        ticket_id = int(ticket_id)
    except:
        if ticket_id == "Назад":
            bot.send_message(message.chat.id, "Возвращаемся...", reply_markup = types.ReplyKeyboardRemove())
        else:
            bot.send_message(message.chat.id, "Некорректный номер тикета.")
        manager_answer(message)
    else:
        ticket = Ticket.get_by_id(message.session, ticket_id)

        if message.session.query(BlockedTicket).get(ticket_id):
            bot.send_message(message.chat.id, "Извините, тикет уже закрыт.")
        elif ticket and ticket.client_id == user.id:
            bot.send_message(message.chat.id, "Хорошо, введите Ваше сообщение.",reply_markup = types.ReplyKeyboardRemove())
            bot.register_next_step_handler(message, append_message, ticket_id)
        else:
            bot.send_message(message.chat.id, "Тикет не найден. Попробуйте еще раз.")
            manager_answer(message)


def append_message(message, ticket_id):
    Message.add(message.session, message.text, ticket_id, message.chat.id)
    bot.send_message(message.chat.id, "Ваш вопрос успешно отправлен менеджеру, ожидайте.")
    manager_answer(message)

def worker(message):
    if message.user.role_id == RoleNames.CLIENT.value:
        if str(message.text) == "Добавить сообщение в тикет":
            bot.send_message(message.chat.id, "Для отмены операции можете воспользоваться кнопкой \"Назад\"", reply_markup = types.ReplyKeyboardRemove())
            bot.send_message(message.chat.id, "Введите ticket_id:", reply_markup=keyboard_back())
            bot.register_next_step_handler(message, write_message)

        elif str(message.text) == "Создать тикет":
            bot.send_message(message.chat.id, "Для отмены операции можете воспользоваться кнопкой \"Назад\"", reply_markup = keyboard_back())
            create_ticket(message)

        elif str(message.text) == "Список моих тикетов":
            bot.send_message(message.chat.id, "Хорошо, вывожу.", reply_markup=types.ReplyKeyboardRemove())
            active_ticket_list(message)

        elif str(message.text) == "Посмотреть историю тикета":
            bot.send_message(message.chat.id, "Для отмены операции можете воспользоваться кнопкой \"Назад\"", reply_markup = types.ReplyKeyboardRemove())
            bot.send_message(message.chat.id, "Введите ticket_id:", reply_markup=keyboard_back())
            bot.register_next_step_handler(message, history)

        elif str(message.text) == "Закрыть тикет":
            bot.send_message(message.chat.id, "Секундочку...", reply_markup=keyboard_back())
            close_ticket(message)

        elif str(message.text) == "Закрыть клавиатуру":
            bot.send_message(message.chat.id, "Закрываем клавиатуру...", reply_markup=types.ReplyKeyboardRemove())
            return
        else:
            bot.send_message(message.chat.id, "Вы выбрали несуществующую команду. Попробуйте снова", reply_markup=types.ReplyKeyboardRemove())
            return

    elif message.user.role_id == RoleNames.MANAGER.value:
        if str(message.text) == "Просмотреть историю сообщений тикета":
            bot.send_message(message.chat.id, "Для отмены операции можете воспользоваться кнопкой \"Назад\"", reply_markup = types.ReplyKeyboardRemove())
            bot.send_message(message.chat.id, "Введите ticket_id:", reply_markup=keyboard_back())
            bot.register_next_step_handler(message, history)

        elif str(message.text) == "Посмотреть активные тикеты":
            bot.send_message(message.chat.id, "Вывожу список активных тикетов\nСекундочку...", reply_markup=types.ReplyKeyboardRemove())
            active_ticket_list(message)

        elif str(message.text) == "Выбрать тикет для ответа":
            bot.send_message(message.chat.id, "Для отмены операции можете воспользоваться кнопкой \"Назад\"", reply_markup = types.ReplyKeyboardRemove())
            bot.send_message(message.chat.id, "Введите ticket_id:", reply_markup=keyboard_back())
            bot.register_next_step_handler(message, get_reply_id)

        elif str(message.text) == "Отказаться от тикета":
            bot.send_message(message.chat.id, "Для отмены операции можете воспользоваться кнопкой \"Назад\"", reply_markup = types.ReplyKeyboardRemove())
            bot.send_message(message.chat.id, "Введите ticket_id:", reply_markup=keyboard_back())
            bot.register_next_step_handler(message, get_refuse_id)

        elif str(message.text) == "Закрыть клавиатуру":
            bot.send_message(message.chat.id, "Закрываем клавиатуру...", reply_markup=types.ReplyKeyboardRemove())
            return
        else:
            bot.send_message(message.chat.id, "Вы выбрали несуществующую команду. Попробуйте снова", reply_markup=types.ReplyKeyboardRemove())
            return


# ответ менеджера на тикет
@bot.message_handler(commands=["message"])
def manager_answer(message):
    """
        ответ менеджера на тикет
    """
    user_role = message.user.role_id

    if user_role == RoleNames.CLIENT.value:
        bot.send_message(message.chat.id, "Что вы хотите сделать?", reply_markup=keyboard_client())
        bot.register_next_step_handler(message, worker)

    elif user_role == RoleNames.MANAGER.value:
        bot.send_message(message.chat.id, "Что Вы хотите сделать?", reply_markup=keyboard_manager())
        bot.register_next_step_handler(message, worker)


def history(message):
    """
        История тикета
    """
    ticket_id = message.text
    chat_id = message.chat.id
    try:
        ticket_id = int(ticket_id)
    except:
        if ticket_id == "Назад":
            bot.send_message(message.chat.id, "Возвращаемся...", reply_markup = types.ReplyKeyboardRemove())
        else:
            bot.send_message(message.chat.id, "Некорректный номер тикета.")
        manager_answer(message)
        return
    else:
        ticket = Ticket.get_by_id(message.session, ticket_id)
        user_id = User.find_by_conversation(message.session, chat_id).id
        messages = Ticket.get_all_messages(message.session, ticket_id)
        messages.reverse()

        if not (ticket and user_id in (ticket.client_id, ticket.manager_id)):
            bot.send_message(message.chat.id, f"Тикет с номером {ticket_id} не найден.\n")
            manager_answer(message)
            return
        else:
            ans = "История последних сообщений:\n\n"
            if len(messages) > 10:
                messages = messages[:11]
            for m in messages:
                ans += RoleNames(User.find_by_id(message.session, m.sender_id).role_id).name + '\n'
                ans += "Дата: " + str(m.date) + "\n"
                ans += "Сообщение: " + m.body + "\n"
                bot.send_message(chat_id, ans)
                ans = ''
            

            if not messages:
                bot.send_message(chat_id, "История сообщений пустая.", reply_markup = types.ReplyKeyboardRemove())
            manager_answer(message)


def get_reply_id(message):
    ticket_id = message.text
    chat_id = message.chat.id
    try:
        ticket_id = int(ticket_id)
    except:
        if ticket_id == "Назад":
            bot.send_message(message.chat.id, "Возвращаемся...", reply_markup = types.ReplyKeyboardRemove())
        else:
            bot.send_message(message.chat.id, "Тикет введен некорректно.")
        manager_answer(message)
        return
    else:
        user = message.user
        ticket = Ticket.get_by_id(message.session, ticket_id)
        user_id = User.find_by_conversation(message.session, chat_id).id

        if ticket and user_id in (ticket.client_id, ticket.manager_id):
            bot.send_message(message.chat.id, "Введите Ваш ответ:")
            bot.register_next_step_handler(message, get_reply, ticket_id)
        else:
            bot.send_message(message.chat.id, f"Тикет с номером {ticket_id} не найден.")
            manager_answer(message)
            return


def get_refuse_id(message):
    ticket_id = message.text
    try:
        ticket_id = int(ticket_id)
    except:
        if ticket_id == "Назад":
            bot.send_message(message.chat.id, "Возвращаемся...", reply_markup = types.ReplyKeyboardRemove())
        else:
            bot.send_message(message.chat.id, "Тикет введен некорректно.")
        manager_answer(message)
        return
    else:
        if not Ticket.get_all_messages(message.session, ticket_id):
            bot.send_message(message.chat.id, f"Тикет с номером {ticket_id} не найден.", reply_markup = types.ReplyKeyboardRemove())
            manager_answer(message)
            return
        else:
            user = User.find_by_conversation(message.session, message.chat.id)
            if user.role_id != RoleNames.MANAGER.value:
                bot.send_message(message.chat.id, f"Извините, ваша роль не позволяет воспользоваться командой, \
                    нужно быть manager/nВаша роль {RoleNames(User.find_by_conversation(message.session, message.chat.id).role_id).name}", reply_markup = types.ReplyKeyboardRemove())
                manager_answer(message)
                return
            else:
                global tic
                tic = ticket_id
                bot.send_message(message.chat.id, "Опишите причину закрытия тикета:\n")
                bot.register_next_step_handler(message, describe_refuse)


def describe_refuse(message):
    if not message.text:
        bot.send_message(message.chat.id, "Описание отказа от тикета обязательно.\n \
            Опишите причину закрытия тикета\n")
        bot.register_next_step_handler(message, describe_refuse)
    else:
        global tic
        ticket = Ticket.get_by_id(message.session, tic)
        ticket.put_refuse_data(message.session, message.text)
        ticket.reappoint(message.session)
        bot.send_message(message.chat.id, f"Вы отказались от тикета {tic}\n"
                                          "Для проверки воспользуйтесь командой /ticket_list.")


def get_reply(message, ticket_id):
    curr_ticket = Ticket.get_by_id(message.session, ticket_id)
    client_convers = User.find_by_id(message.session, curr_ticket.client_id).conversation
    reply = message.text
    Message.add(message.session, reply, ticket_id, message.chat.id)
    bot.send_message(client_convers, f"Вам ответил менеджер. Ticket #{curr_ticket.id}")
    bot.send_message(message.chat.id, "Ответ отправлен.", reply_markup=types.ReplyKeyboardRemove())
    manager_answer()



def keyboard_manager():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    key_history = types.KeyboardButton("Просмотреть историю сообщений тикета")
    markup.add(key_history)
    key_reply = types.InlineKeyboardButton("Выбрать тикет для ответа")
    markup.add(key_reply)
    key_show = types.InlineKeyboardButton("Посмотреть активные тикеты")
    markup.add(key_show)
    key_refuse = types.InlineKeyboardButton("Отказаться от тикета")
    markup.add(key_refuse)
    key_cancel = types.InlineKeyboardButton("Закрыть клавиатуру")
    markup.add(key_cancel)

    return markup


def keyboard_client():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    key_input = types.KeyboardButton("Добавить сообщение в тикет")
    markup.add(key_input)
    key_show = types.KeyboardButton("Посмотреть историю тикета")
    markup.add(key_show)
    key_list = types.KeyboardButton("Список моих тикетов")
    markup.add(key_list)
    markup.row(
        types.KeyboardButton("Создать тикет"),
        types.KeyboardButton("Закрыть тикет")
    )
    key_cancel = types.InlineKeyboardButton("Закрыть клавиатуру")
    markup.add(key_cancel)
    return markup
def keyboard_back():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    key_back = types.KeyboardButton("Назад")
    markup.add(key_back)
    return markup
@bot.message_handler(commands=["message"])
def manager_answer(message):
    """
        ответ менеджера на тикет
    """
    user_role = message.user.role_id

    if user_role == RoleNames.CLIENT.value:
        bot.send_message(message.chat.id, "Что вы хотите сделать?", reply_markup=keyboard_client())
        bot.register_next_step_handler(message, worker)

    elif user_role == RoleNames.MANAGER.value:
        bot.send_message(message.chat.id, "Что Вы хотите сделать?", reply_markup=keyboard_manager())
        bot.register_next_step_handler(message, worker)

if cfg['debug']:
    """
        Методы для тестирования
    """
    @bot.message_handler(commands=["debug"])
    def debug_info(message):
        bot.send_message(message.chat.id, "DEBUG")
    @bot.message_handler(commands=["debug_set_role_client"])
    def debug_set_role_client(message):
        User.find_by_conversation(message.session, message.chat.id).role_id = RoleNames.CLIENT.value
        message.session.commit()
        bot.send_message(message.chat.id, 'OK')
    
    @bot.message_handler(commands=["debug_set_role_manager"])
    def debug_set_role_manager(message):
        User.find_by_conversation(message.session, message.chat.id).role_id = RoleNames.MANAGER.value
        message.session.commit()
        bot.send_message(message.chat.id, 'OK')
    @bot.message_handler(commands=["debug_set_role_admin"])
    def debug_set_role_admin(message):
        User.find_by_conversation(message.session, message.chat.id).role_id = RoleNames.ADMIN.value
        message.session.commit()
        bot.send_message(message.chat.id, 'OK')


@bot.middleware_handler(update_types=['message'])
def close_session_middleware(bot_instance, message):
    """
       Завершение сессии БД
    """
    message.session.close()
    print("session CLOSE")


bot.polling(none_stop=True)
