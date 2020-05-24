from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
import pymysql
import sys
import time

from models.DataBaseClasses import Role, BlockedTicket, Token, Message, User, Ticket, Base

pymysql.install_as_MySQLdb()

config = json.load(open("./config.json"))
engine = create_engine(config['database']['url'], echo=False)
Session = sessionmaker(bind=engine)

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

Base.metadata.create_all(engine)
session = Session()

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
