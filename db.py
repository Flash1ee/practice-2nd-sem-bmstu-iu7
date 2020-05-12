from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import pymysql
import json
import sys

sys.path.append("./models/")
from DataBaseClasses import Role, BlockedTicket, Token, Message, User, Ticket, Base


pymysql.install_as_MySQLdb()

config = json.load(open(".\config.json"))
engine = create_engine(config['database']['url'], echo=True)
Session = sessionmaker(bind=engine)


role_manager = Role(name='Менеджер')
role_сlient = Role(name='Клиент')


manager_vladimir = User(name='Vladimir_manager', conversation=597, role_id=1)
client_demasek = User(name='Demasek_client', conversation=100, role_id=2)
test_ticket1 = Ticket(manager_id=manager_vladimir.id, client_id=client_demasek.id, title='Вова  Проблема все еще есть!')

# client_dima = User(id=46, name='Dmirty_client', conversation=111, role_id=2)
# test_ticket = Ticket(manager_id=manager_vladimir.id, title= НАДО РЕШАТЬ ПРОБЛЕМУ!')
# # test_ticket2 = Ticket(manager_id=manager_vladimir.id, client_id=client_demasek.id, title='ЭЭЭ, а где вообще клиент ид')
# test_ticket2 = Ticket(id=12, manager_id=manager_vladimir.id, client_id=client_dima.id, title='ЭЭЭ, а где вообще клиент ид')

# test_message = Message(ticket_id=test_ticket2.id, sender_id=test_ticket2.client_id, body='Дарова:^), Как делишки, парнишка?')
# blocked = BlockedTicket(id=12, ticket_id=test_ticket2.id, manager_id=manager_vladimir.id, reason=' )


Base.metadata.create_all(engine)
session = Session()
session.add(role_manager)
session.add(role_сlient)
session.add(manager_vladimir)
# session.add(client_dima)
session.add(client_demasek)
# session.add(test_ticket)
session.add(test_ticket1)
# session.add(test_message)
# session.add(blocked)

session.commit()

