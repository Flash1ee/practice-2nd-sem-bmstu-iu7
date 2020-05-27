from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import json
import pymysql
from pprint import pprint


from models.DataBaseClasses import *


pymysql.install_as_MySQLdb()

config = json.load(open("./config.json"))
engine = create_engine(config['database']['url'], echo=True)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
session = Session()


# session.add_all([
#     Ticket(manager_id=3, client_id=7, title='Ticket3'),
#     Ticket(manager_id=3, client_id=6, title='Ticket2'),
#     Ticket(manager_id=4, client_id=8, title='Ticket4'),
#     Ticket(manager_id=4, client_id=9, title='Ticket5'),
#     Ticket(manager_id=4, client_id=10, title='Ticket6'),
#     Ticket(manager_id=5, client_id=6, title='Ticket7'),
#     Ticket(manager_id=5, client_id=7, title='Ticket8'),
#     Ticket(manager_id=5, client_id=8, title='Ticket9'),
#     Ticket(manager_id=3, client_id=9, title='Ticket10'),
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

session.add(Message(ticket_id=12, sender_id=3))
session.commit()

user = User.find_by_id(session, 3)

tickets1 = user.get_active_tickets(session)
tickets2 = User.get_unprocessed_tickets(session, user.id)

# # print(type(tickets2))

for ticket in tickets1:
    print(f'Title: {ticket.title}, Close_date: {ticket.close_date}')

print('')

# print(tickets2)

for ticket in tickets2:
    pprint(ticket.__dict__)















# User.add_several(session, [
#     (101, 'test_admin1', RoleNames.ADMIN.value),
#     (102, 'test_admin2', RoleNames.ADMIN.value),[]
#     (201, 'Manager1', RoleNames.MANAGER.value),
#     (202, 'Manager2', RoleNames.MANAGER.value),
#     (203, 'Manager3', RoleNames.MANAGER.value),
#     (301, 'Client1', RoleNames.CLIENT.value),
#     (302, 'Client2', RoleNames.CLIENT.value),
#     (303, 'Client3', RoleNames.CLIENT.value),
#     (304, 'Client4', RoleNames.CLIENT.value),
#     (305, 'Client5', RoleNames.CLIENT.value),
#     (401, 'Blocked1', RoleNames.BLOCKED_USER.value)
# ])




# manager_vladimir = User(name='Vladimir_manager', conversation=597, role_id=1)
# client_demasek = User(name='Demasek_client', conversation=100, role_id=2)
# test_ticket1 = Ticket(manager_id=manager_vladimir.id, client_id=client_demasek.id, title='Вова Проблема все еще есть!')

# # client_dima = User(id=46, name='Dmirty_client', conversation=111, role_id=2)
# # test_ticket = Ticket(manager_id=manager_vladimir.id, title= НАДО РЕШАТЬ ПРОБЛЕМУ!')
# # # # test_ticket2 = Ticket(manager_id=manager_vladimir.id, client_id=client_demasek.id, title='ЭЭЭ, а где вообще клиент ид')
# session.add(Ticket(manager_id=1, client_id=2, title='Тест 3'))
# session.commit()

# test_message = Message(ticket_id=test_ticket2.id, sender_id=test_ticket2.client_id, body='Дарова:^), Как делишки, парнишка?')
# blocked = BlockedTicket(id=12, ticket_id=test_ticket2.id, manager_id=manager_vladimir.id, reason=' )



# session.add(role_manager)
# session.add(role_сlient)s
# session.add(manager_vladimir)
# # session.add(client_dima)
# session.add(client_demasek)
# # session.add(test_ticket)
# session.add(test_ticket2)
# # session.add(test_message)
# session.add(blocked)

# print(User.get_by_conversation(session, 13))
# print(type(User.get_by_conversation(session, 13)))


# managers = User.get_all_managers(session)
# manager = managers[0]
# print(manager.name)

# # print(managers)
# 


# session.commit()

# Role.init_roles(session)

# User.add(session, [(1433, 'Petya', 1), (31, 'Ivan', 3)])

# User.add_user(session,'Vladimir_manager', 597, 2)
# User.add_user(session,'Demasek', 593, 3)
# User.add_user(session,'Kolyasek', 592, 3)


# User.add_several(session, [
#     (13, 'Demasek', 1),
#     (14, 'Dema', 2),
#     (12, 'Debil', 3),
#     (11, 'Danil', 2),  
# ])


# print(f"MAN: {User.get_all_managers(session)}\n")
# print(f"MAN: {User.get_all_administrators(session)}\n")
# print(f"MAN: {User.get_all_clients(session)}\n")

# print(User.get_by_name(session, 'Demasek')[0])

# print(User.get_by_id(session, 2))

# dema = User.find_by_name(session, 'Demasek')[0]
# tickets = dema.get_active_tickets(session)
# print("All tickets: ", tickets)

# for us in User.get_by_name(session, 'Demasek'):
#     print(f'ANSWER: {us}')