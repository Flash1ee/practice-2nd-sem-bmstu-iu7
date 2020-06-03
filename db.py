from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from pprint import pprint
from sqlalchemy.pool import NullPool
import json
from models.DataBaseClasses import *

config = json.load(open("./config.json"))
isdebug = config['debug']
engine = create_engine(config['database']['url'], echo=isdebug, poolclass=NullPool)
Session = sessionmaker(bind=engine)
session = Session()

# User.find_by_id(session, 1).name='Васёк'
# session.commit()


# session.connection()
# User.get_all_users_with_role(session, 2)
# User.find_by_id(session, 3).name='Васёк'
# session.commit()
# session.close()

# Base.metadata.create_all(engine)




# session.add_all([
#     # Ticket(manager_id=2, client_id=1, title='Первый тестовый'),
#     # Ticket(manager_id=5, client_id=1, title='Второй тестовый')
#     Message(ticket_id=6, sender_id=1, body="Писулькаю в 6-й тикет")
# ]
# # )

# User.find_by_id(session, 1).name='Васёк'
# session.commit()

# ticket_id = user.identify_ticket(session)

# print(ticket_id)

# session.commit()


# # chat_id = 339306576
# # username = 'Дмитрий'
# # import telebot
# # import json
# # from db import session 
# # from telebot import apihelper
# # from telebot import types
# # from models.DataBaseClasses import *

# # token = config['bot']['token']
# # bot = telebot.TeleBot(token)

# def start():
#     cur_role = None
#     #если еще нет администраторов - назначаем администратором
#     if not User.get_all_users_with_role(session, RoleNames.ADMIN.value):
#         cur_role = RoleNames.ADMIN.value
#     elif not User.find_by_conversation(session, chat_id):
#         cur_role = RoleNames.CLIENT.value
#     #если назначена новая роль
#     if cur_role:
#         #добавляем сведения в бд
#         User.add_several(session, [(chat_id, username, cur_role)])
#         print(f'{username}, Вы успешно зарегистрировались в системе.\nВаш статус - {RoleNames(cur_role).name}')
#         bot.send_message(chat_id, f'{username}, Вы успешно зарегистрировались в системе.\nВаш статус - {RoleNames(cur_role).name}')
#     else:
#         #пользователь уже зарегистрирован
#         user = User.find_by_conversation(session, chat_id)
#         cur_role = user.role_id
#         if user.name.lower() != username.lower():
#             user.change_name(session, username, chat_id)
#         print(f'{username}, Вы уже зарегистрировались в системе.\nВаш статус - {RoleNames(user.role_id).name}')
#         bot.send_message(chat_id, f'{username}, Вы уже зарегистрировались в системе.\nВаш статус - {RoleNames(user.role_id).name}')


# start()
# start()
# start()
# start()
# start()
# start()
# start()
# start()
# start()
# start()
# start()
# start()
# start()
# start()
# start()
# start()
# start()
# start()
# start()

# Role.init_roles(session)
# # user = User.find_by_conversation(session, )

# print(User.get_all_users_with_role(session, RoleNames.ADMIN.value))

# pprint(user)

# Message.add(session, 'Blah-blah-blah', 1, 202)
#Message.add(session, 'Blah-blah-blah', 1, 202)

# token_value = '0nLUJF4GPzRJ'

# find_token = Token.find(session, token_value)

# if find_token:
#     find_token.activate(session)
# else:
#     print("None")

#token = Token.generate(session, RoleNames.ADMIN.value)
#token2 = Token.generate(session, RoleNames.ADMIN.value)

#print(f'value: {token.value}, role: {token.role_id}')
#print(f'value: {token2.value}, role: {token2.role_id}')
#if find_token:
    #find_token.activate(session)
#else:
    #print("None")



# session.add_all([
#     Token(value='qW2dfglopsmk', expires_date=datetime.now(), role_id=RoleNames.ADMIN.value),
#     Token(value='qW2df7sf5df4', expires_date=datetime.now(), role_id=RoleNames.MANAGER.value),
#     Token(value='qW2sdflklkf3', expires_date=datetime.now(), role_id=RoleNames.ADMIN.value),
#     Token(value='qW2dfgldf6s4', expires_date=datetime.now(), role_id=RoleNames.MANAGER.value),
#     Token(value='qW2dfglopsfs', expires_date=datetime.now(), role_id=RoleNames.ADMIN.value)
#     ])

# User.add

# user1 = User.find_by_id(session, 7)
# User.change_name(session, 'NewName', user1.id)
# Token.garbage_collector(session)
# session.add_all([
#     Ticket(manager_id=3, client_id=7, title='Ticket3'),
#     Ticket(manager_id=3, client_id=6, title='Ticket2'),
#     Ticket(manager_id=4, client_id=8, title='Ticket4'),
#     Ticket(manager_id=4, client_id=9, title='Ticket5'),
#     Ticket(manager_id=4, client_id=10, title='Ticket6'),
#     Ticket(manager_id=5, client_id=6, title='Ticket7'),
#     Ticket(manager_id=5, client_id=7, title='Ticket8'),
#     Ticket(manager_id=5, client_id=8, title='Ticket9'),
    # Ticket(manager_id=3, client_id=9, title='Ticket10'),
#     Ticket(manager_id=3, client_id=10, title='Ticket11'),
#     Ticket(manager_id=3, client_id=6, title='Ticket12'),
#     Ticket(manager_id=4, client_id=7, title='Ticket13'),
#     Ticket(manager_id=4, client_id=8, title='Ticket14'),
#     Ticket(manager_id=5, client_id=7, title='Ticket14')
#     ])

# session.add_all([
#     Message(ticket_id=1, sender_id=7),
#     Message(ticket_id=1, sender_id=3),
#     Message(ticket_id=2, sender_id=6),
#     Message(ticket_id=2, sender_id=3),
#     Message(ticket_id=3, sender_id=8),
#     Message(ticket_id=3, sender_id=4),
#     Message(ticket_id=4, sender_id=9),
#     Message(ticket_id=4, sender_id=4),
#     Message(ticket_id=5, sender_id=10),
#     Message(ticket_id=5, sender_id=4),
#     Message(ticket_id=6, sender_id=6),
#     Message(ticket_id=7, sender_id=7),
#     Message(ticket_id=8, sender_id=8),
#     Message(ticket_id=9, sender_id=9),
#     Message(ticket_id=10, sender_id=10),
#     Message(ticket_id=11, sender_id=6),
#     Message(ticket_id=12, sender_id=7),
#     Message(ticket_id=13, sender_id=8),
#     Message(ticket_id=14, sender_id=7)
# ])



# ticket1 = session.query(Ticket).get(1)
# ticket1.close_date = datetime.now(offset)

# ticket2 = session.query(Ticket).get(2)
# ticket2.close_date = datetime.now(offset)

# ticket3 = session.query(Ticket).get(3)
# ticket3.close_date = datetime.now(offset)
# session.commit()

# session.add(Message(ticket_id=12, sender_id=3))
# session.commit()

# user = User.find_by_id(session, 1)

# print(Token.check_token(session, 'asdasda'))




# pprint(user)

# tickets1 = user.get_active_tickets(session)
# tickets2 = User.get_unprocessed_tickets(session, user.id)

# # # print(type(tickets2))

# for ticket in tickets1:
#     print(f'Title: {ticket.title}, Close_date: {ticket.close_date}')

# print('')

# # print(tickets2)

# for ticket in tickets2:
#     pprint(ticket.__dict__)










# Roles creation

#role_admin = Role(name="Admin")
#role_manager = Role(name='Manager')
#role_client = Role(name="Client")

# Users creation

#admin_vladimir = User(name='Vladimir_admin', conversation=597, role_id=1)
#manager_dima = User(name='Dmitry_manager', conversation=111, role_id=2)
#manager_polina = User(name='Polina_manager', conversation=124, role_id=2)
#client_demasek = User(name='Demasek_client', conversation=100, role_id=3)
#client_kalyan = User(name="Kalyan_client", conversation=196, role_id=3)

#Base.metadata.create_all(engine)
#session = Session()

# add users

#session.add(admin_vladimir)
#session.add(manager_dima)
#session.add(manager_polina)
#session.add(client_demasek)
#session.add(client_kalyan)

#session.commit()

# Tickets creation

#manager_dima = session.query(User).filter(User.name == "Dmitry_manager")[0]
#client_kalyan = session.query(User).filter(User.name == "Kalyan_client")[0]

# test_ticket = Ticket(manager_id=manager_dima.id, client_id=client_demasek.id, title= "НАДО РЕШАТЬ ПРОБЛЕМУ!")
# test_ticket1 = Ticket(manager_id=manager_polina.id, client_id=client_demasek.id, title='Проблема все еще есть!')
# test_ticket2 = Ticket(manager_id=manager_dima.id, client_id=client_kalyan.id, title='ЭЭЭ, а где вообще клиент ид')
# test_ticket3 = Ticket(manager_id=manager_polina.id, client_id=client_kalyan.id, title='Компьютер нападает на людей с ножом')
# test_ticket2 = session.query(Ticket).filter(Ticket.title=="ЭЭЭ, а где вообще клиент ид")[0]

# add tickets

#session.add(test_ticket)
#session.add(test_ticket1)
#session.add(test_ticket2)
#session.commit()

# Messages creation

#test_message1 = Message(ticket_id=test_ticket2.id, sender_id=test_ticket2.client_id, body='Дарова:^), Как делишки, парнишка?')
#test_message2 = Message(ticket_id=test_ticket2.id, sender_id=test_ticket2.client_id, body="Зачем игнорируешь, дорогой?")

# add messages

#session = Session()
#session.add(test_message2)
#session.commit()

# add roles

#if (not len(session.query(Role).all())):
#    print("Hello")
#    session.add_all([
#        role_admin,
#        role_manager,
#        role_client
#    ])
#session.commit()

# Tests

##test = session.query(Ticket).filter(Ticket.title == "НАДО РЕШАТЬ ПРОБЛЕМУ!")[0]
##test.close_date = None
##session.commit()
##
##print("GET ACTIVE TICKETS: TEST")
##for a in session.query(User):
##   a1 = a.get_active_tickets(session)
##   print(a1)
##print()
##
##print("ADD & APPOINT_TO_MANAGER: TEST")
##title = "Testing create_ticket"
##test_ticket4 = Ticket(client_id=client_kalyan.id, title=title)
##test_ticket4.add(session, manager_dima.id)
##print("added\n")
##
##test = session.query(Ticket).filter(Ticket.title == "Testing create_ticket")[0]
##print(test.id)
##print(test.client_id)
##print(test.manager_id)
##print(test.title)
##print(test.start_date)
##print()
##
##print("GET_ALL_MESSAGES: TEST")
##for t in session.query(Ticket):
##    messages = t.get_all_messages(session)
##    print(messages)
##print()
##
##print("PUT_REFUSE_DATA & REAPPOINT: TEST")
##reason = "Appoint to Polina"
##print("Before reassignment")
##print(test.manager_id)
##print()
##
##test.put_refuse_data(session, reason)
##refused_list = session.query(User).filter(User.id == test.manager_id).all()
##test.reappoint(session, refused_list)
##
##print("After reassignment")
##print(test.manager_id)
##print()
##
##print("CLOSE: TEST")
##for a in session.query(User):
##   a1 = a.get_active_tickets(session)
##   print(a1)
##print()
##print("First ticket closed")
##print()
##test = session.query(Ticket).filter(Ticket.title == "НАДО РЕШАТЬ ПРОБЛЕМУ!")[0]
##test.close(session)
##for a in session.query(User):
##   a1 = a.get_active_tickets(session)
##   print(a1)
##print()

#test_message4 = Message(ticket_id=20, sender_id=20, body='Test 1')
#test_message5 = Message(ticket_id=36, sender_id=20, body="Test 2")
#test_message6 = Message(ticket_id=18, sender_id=19, body='Test 3')
#test_message7 = Message(ticket_id=17, sender_id=19, body='Test 4')
#test_message8 = Message(ticket_id=17, sender_id=17, body='Test 5')
#test_message9 = Message(ticket_id=20, sender_id=18, body='Test 6')
#session.add(test_message8)
#session.add(test_message9)
#session.commit()

#print(Ticket.get_unprocessed_tickets(session, 17))
#print(Ticket.get_unprocessed_tickets(session, 18))
#Ticket.create(session, "Create_test_2", 100)
#Ticket.create(session, "Create_test_2", client_id=19)

