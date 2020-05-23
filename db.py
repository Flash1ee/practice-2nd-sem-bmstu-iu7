from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
import pymysql
import sys

from models.DataBaseClasses import Role, BlockedTicket, Token, Message, User, Ticket, Base


pymysql.install_as_MySQLdb()

config = json.load(open("./config.json"))
engine = create_engine(config['database']['url'], echo=False)
Session = sessionmaker(bind=engine)

#role_admin = Role(name="Admin")
#role_manager = Role(name='Manager')
#role_client = Role(name="Client")

#admin_vladimir = User(name='Vladimir_admin', conversation=597, role_id=1)
#manager_dima = User(name='Dmitry_manager', conversation=111, role_id=2)
#manager_polina = User(name='Polina_manager', conversation=124, role_id=2)
#client_demasek = User(name='Demasek_client', conversation=100, role_id=3)
#client_kalyan = User(name="Kalyan_client", conversation=196, role_id=3)

#test_message = Message(ticket_id=test_ticket2.id, sender_id=test_ticket2.client_id, body='Дарова:^), Как делишки, парнишка?')
#blocked = BlockedTicket(id=12, ticket_id=test_ticket2.id, manager_id=manager_vladimir.id, reason=' ')

Base.metadata.create_all(engine)
session = Session()

#session.add(admin_vladimir)
#session.add(manager_dima)
#session.add(manager_polina)
#session.add(client_demasek)
#session.add(client_kalyan)

#session.commit()

#session = Session()

#test_ticket = Ticket(manager_id=manager_dima.id, client_id=client_demasek.id, title= "НАДО РЕШАТЬ ПРОБЛЕМУ!")
#test_ticket1 = Ticket(manager_id=manager_polina.id, client_id=client_demasek.id, title='Проблема все еще есть!')
#test_ticket2 = Ticket(manager_id=manager_dima.id, client_id=client_kalyan.id, title='ЭЭЭ, а где вообще клиент ид')
#test_ticket3 = Ticket(manager_id=manager_polina.id, client_id=client_kalyan.id, title='Компьютер нападает на людей с ножом')

#session.add(test_ticket)
#session.add(test_ticket1)
#session.add(test_ticket2)
#session.add(test_ticket3)
#session.add(test_message)
#session.add(blocked)

#if (not len(session.query(Role).all())):
#    print("Hello")
#    session.add_all([
#        role_admin,
#        role_manager,
#        role_client
#    ])
#session.commit()

#IDs = [u for u in session.query(User)]
#for instance, in session.query(User.name).filter(User.name == 'Demasek_client'):
#    print('ALL NAMES:', instance)

#for a in IDs:
 #   a1 = a.get_active_tickets(session)
 #   print(a1)