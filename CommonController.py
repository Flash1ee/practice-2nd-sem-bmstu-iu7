"""
    Контроллер общих функций бота 
"""

from models.DataBaseClasses import *
def init(bot):
    @bot.message_handler(commands = ["help"])
    def help(message):
        """
            Вывод сообщения помощи
        """
        user = message.user
        if not user:
            bot.send_message(message.chat.id, "Перед использованием /help нужно зарегистрироваться.")
            return
        commands = "Привет! Вам доступны следующие комманды:\n\n"
        commands += "/help - Вызов данного сообщения.\n\n"
        commands += "/start - вход в систему\n\n"
        if RoleNames(user.role_id).name == "CLIENT":
            commands += "/ticket_add - Создать новый тикет, с помощью которого Вы сможете описать задать Ваш вопрос менеджерам приложения.\n\n"\
                "/ticket_id - Выбрать тикет для переписки. Внимание: После вызова этой команды следующим сообщением необходимо указать"\
                "номер нужного тикета.\n\n"\
                "/ticket_list - Посмотреть список активных тикетов и краткую информацию по ним.\n\n"\
                "/ticket_close - Закрыть тикет в случае, когда Ваша проблема решена.\n\n"\
                "Что такое тикет?\n Тикет - это идентификационный номер Вашего вопроса, с помощью которого приложение будет с ним работать."
        elif RoleNames(user.role_id).name == "MANAGER":
            commands += "/superuser init <TOKEN> - регистрация в системе по идентификационному номеру(токену). Чтобы получить "\
                "токен, обратитесь к администратору приложения.\n\n"\
                "/manager_init <TOKEN> - Регистрация в системе.\n\n"\
                "/message <ticket_id> - Ответить на выбранный тикет.\n\n"\
                "/ticket_id - Просмотреть историю переписки и информацию о выбранном тикете.  "\
                "Внимание: После вызова этой команды следующим сообщением необходимо указать номер нужного тикета.\n\n"\
                "/ticket_list - Посмотреть список активных тикетов, прикепленных к Вам, и краткую информацию по ним.\n\n"\
                "/ticket_refuse <ticket_id> <reason> - Отказ от тикета. Внимание: необходимо соблюдать форму шаблона команды, в которой "\
                "<ticket_id> - id тикета, от которого Вы отказываетесь, <reason> - соответственно причина отказа.\n\n"\
                "Справка: будьте внимательны при соблюдении шаблона команды. В противном случае команда недействительна."
        elif RoleNames(user.role_id).name == "ADMIN":
            commands += "/superuser_init <TOKEN> - регистрация в системе по идентификационному номеру(токену). Чтобы получить "\
                "токен, обратитесь к администратору приложения.\n\n"\
                "/manager_list - Просмотр списка менеджеров.\n\n"\
                "/manager_create - Создать токен для подключения к менеджера системе.\n\n"\
                "/manager remove <manager_id> - Удаление менеджера. Данная операция происходит с подтверждением, при удалении "\
                "менеджера все его открытые тикеты передаются другим менеджерам.\n\n"\
                "/ticket_id - Просмотреть историю переписки и информацию о выбранном тикете.  "\
                "Внимание: После вызова этой команды следующим сообщением необходимо указать номер нужного тикета.\n\n"\
                "/ticket close - Закрытие тикета.\n\n"\
                "/ticket_list - Посмотреть список активных тикетов и краткую информацию по ним.\n\n"\
                "/confirm - Подтверждение удаление менеджера.\n\n"\
                "/cancel - Отмена операции /confirm.\n\n"\
                "Справка: будьте внимательны при соблюдении шаблона команды. В противном случае команда недействительна."
        bot.send_message(message.chat.id, commands)
    
    @bot.message_handler(commands = ["start"])
    def start(message):
        """
            Обработка входа в систему.
        """
        username = message.chat.first_name
        chat_id = message.chat.id
        cur_role = None
        if not message.user:
            cur_role = RoleNames.CLIENT.value
            if not User.get_all_users_with_role(message.session, RoleNames.ADMIN.value):
                cur_role = RoleNames.ADMIN.value
        if cur_role and not User.find_by_conversation(message.session, message.chat.id):
            User.add(message.session, chat_id, username, cur_role)
            bot.send_message(chat_id, f'{username}, Вы успешно зарегистрировались в системе.\nВаш статус - {RoleNames(cur_role).name}')
        else:
            user = message.user
            cur_role = user.role_id
            if user.name.lower() != username.lower():
                user.change_name(message.session, username, chat_id)
            bot.send_message(chat_id, f'{username}, Вы уже зарегистрировались в системе.\nВаш статус - {RoleNames(user.role_id).name}')

