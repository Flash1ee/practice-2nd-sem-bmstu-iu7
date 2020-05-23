from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import exists
import json
import pymysql


from models.DataBaseClasses import Role, BlockedTicket, Token, Message, User, Ticket, Base


pymysql.install_as_MySQLdb()

config = json.load(open("./config.json"))
engine = create_engine(config['database']['url'], echo=False)
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
session = Session()


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

print(User.get_by_conversation(session, 13))
print(type(User.get_by_conversation(session, 13)))


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


# User.add(session, [
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



# for us in User.get_by_name(session, 'Demasek'):
#     print(f'ANSWER: {us}')