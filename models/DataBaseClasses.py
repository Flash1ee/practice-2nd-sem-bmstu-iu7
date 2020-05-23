from sqlalchemy import ForeignKey, Column, Integer, String, DateTime, BigInteger, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, timedelta

offset = timezone(timedelta(hours=3))

Base = declarative_base()


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(10))

    # Relationship
    users = relationship('User', order_by='User.role_id', back_populates='role')
    tokens = relationship('Token', order_by='Token.role_id', back_populates='role')

    def init_roles(session):
        if (not len(session.query(Role).all())):
            print("Hello")
            session.add_all([
                Role(name='Admin'),
                Role(name='Manager'),
                Role(name='Client')
            ])
            session.commit()


class User(Base):
    __tablename__  = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation = Column(BigInteger, index=True)
    name = Column(String(20))
    role_id = Column(Integer, ForeignKey('roles.id'))
    
    # Relationship
    role = relationship('Role', back_populates='users')
    
    ticket_manager = relationship('Ticket', order_by='Ticket.manager_id', back_populates='manager', foreign_keys='Ticket.manager_id')
    ticket_client = relationship('Ticket', order_by='Ticket.client_id', back_populates='client', foreign_keys='Ticket.client_id')
    message = relationship('Message', order_by='Message.sender_id', back_populates='sender')

    def __repr__(self):
        return f'id: {self.id}; Name: {self.name}; Role: {self.role_id}\n'

    def get_all_administrators(session) ->list:
        return session.query(User).filter(User.role_id == 1).all()

    def get_all_managers(session) ->list:
        return session.query(User).filter(User.role_id == 2).all()

    def get_all_clients(session) ->list:
        return session.query(User).filter(User.role_id == 3).all()

    def add(session, users: list) ->None:
        '''
        param session: current session,
        param user: [ (conversation, name, role_id), ...]
        '''
        for user in users:
            session.add(User(conversation=user[0], name=user[1], role_id=user[2]))
        session.commit()

    def get_by_id(session, id: int) ->'User':
        return session.query(User).get(id)

    def get_by_name(session, name: str) ->list:
        return session.query(User).filter(User.name == name).all()

    def get_by_conversation(session, convers: str) -> 'User':
        return session.query(User).filter(User.conversation == convers)[0]
    


class Ticket(Base):
    __tablename__ = 'tickets'

    id = Column(Integer, primary_key=True)
    manager_id = Column(Integer, ForeignKey('users.id'))
    client_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String(50))
    start_date = Column(DateTime, default=datetime.now(offset))
    close_date = Column(DateTime)

    # Relationship
    client = relationship('User', foreign_keys=[client_id], back_populates='ticket_client')
    manager = relationship('User', foreign_keys=[manager_id], back_populates='ticket_manager')

    isblocked = relationship('BlockedTicket', order_by='BlockedTicket.ticket_id', back_populates='ticket')
    message = relationship('Message', order_by='Message.ticket_id', back_populates='ticket')


class BlockedTicket(Base):
    __tablename__ = 'blocked_tickets'

    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey('tickets.id'))
    manager_id = Column(Integer, ForeignKey('users.id'))
    reason = Column(String(50))

    # Relationship
    ticket = relationship('Ticket', back_populates='isblocked')


class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey('tickets.id'))
    sender_id = Column(Integer, ForeignKey('users.id'))
    body = Column(Text)
    date = Column(DateTime)

    # Relationship
    ticket = relationship('Ticket', back_populates='message')
    sender = relationship('User', back_populates='message')


class Token(Base):
    __tablename__ = 'tokens'

    value = Column(Integer, primary_key=True)
    expires_date = Column(DateTime)
    role_id = Column(Integer, ForeignKey('roles.id'))

    # Relationship
    role = relationship('Role', back_populates='tokens')