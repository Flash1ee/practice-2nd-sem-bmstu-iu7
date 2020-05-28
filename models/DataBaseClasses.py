from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Text
from sqlalchemy import ForeignKey, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import except_
from datetime import datetime, timezone, timedelta
from enum import Enum
from pprint import pprint
from sqlalchemy.sql import func

offset = timezone(timedelta(hours=3))

Base = declarative_base()

offset = timezone(timedelta(hours=3))


class RoleNames(Enum):
    ADMIN = 1
    MANAGER = 2
    CLIENT = 3
    BLOCKED_USER = 4


class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True)
    name = Column(String(12), unique=True)

    # Relationship
    users = relationship('User', order_by='User.role_id',
                         back_populates='role')
    tokens = relationship(
        'Token', order_by='Token.role_id', back_populates='role')

    @staticmethod
    def init_roles(session):
        '''
        Проводится только один раз - сразу после создания таблицы '__roles__'.
        Автокоммит - да.
        В случае повторной инициализации - no effect.
        '''
        if (not len(session.query(Role).all())):
            session.add_all([
                Role(name='Admin'),
                Role(name='Manager'),
                Role(name='Client'),
                Role(name='BlockedUser')])
            session.commit()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    conversation = Column(BigInteger, index=True)
    name = Column(String(20))
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)

    # Relationship
    role = relationship('Role', back_populates='users')

    ticket_manager = relationship('Ticket', order_by='Ticket.manager_id',
                                  back_populates='manager', foreign_keys='Ticket.manager_id')
    ticket_client = relationship('Ticket', order_by='Ticket.client_id',
                                 back_populates='client', foreign_keys='Ticket.client_id')
    messages = relationship(
        'Message', order_by='Message.sender_id', back_populates='sender')

    # Default methods

    def __repr__(self):
        return f'id: {self.id}; Name: {self.name}; Role: {self.role_id}\n'

    # Instance methods

    def get_active_tickets(self, session) -> list:
        '''
        Метод объекта класса User, который возвращает список активных тикетов.
        Для администратора возвращает все активные тикеты всех менеджеров (сортировка: Ticket.manager_id)
        Для менеджера возврашает все активные тикеты данного менеджера (сортировка: Ticket.start_date)
        Для клиента возвращает ве активные тикета данного клиента (сортировка: Ticket.start_date)
        '''
        if self.role_id == RoleNames.ADMIN.value:
            ans = session.query(Ticket).filter(
                Ticket.close_date.is_(None)).order_by(Ticket.manager_id).all()
        elif self.role_id == RoleNames.MANAGER.value:
            ans = session.query(Ticket).filter(Ticket.manager_id == self.id).filter(
                Ticket.close_date.is_(None)).order_by(Ticket.start_date).all()
        elif self.role_id == RoleNames.CLIENT.value:
            ans = session.query(Ticket).filter(Ticket.close_date.is_(None)).filter(
                Ticket.client_id == self.id).order_by(Ticket.start_date).all()

        return ans

    def appoint(self, session, role_id) -> None:
        '''param role_id: Role.(ADMIN/MANAGER/CLIENT/BLOCKED_USER).value '''
        self.role_id = role_id
        session.commit()

    def demote_manager(self, session) -> None:
        his_tickets = self.get_active_tickets(session)

        for ticket in his_tickets:
            new_manager = User.get_free_manager(session)
            ticket.appoint_to_manager(session, new_manager.id)

        self.role_id = RoleNames.CLIENT.value
        session.commit()

    def add(self, session) -> None:
        session.add(self)
        session.commit()

    def get_active_tickets(self, session) -> list:
        tickets = []
        if self.role_id == 1:
            tickets = session.query(Ticket).filter(
                Ticket.close_date == None).all()
        elif self.role_id == 2:
            tickets = session.query(Ticket).filter(
                Ticket.manager_id == self.id).filter(Ticket.close_date == None).all()
        elif self.role_id == 3:
            tickets = session.query(Ticket).filter(
                Ticket.client_id == self.id).filter(Ticket.close_date == None).all()
        else:
            print("Invalid user")
        return tickets

    # Static methods

    @staticmethod
    def add_several(session, users: list) -> None:
        '''
        param session: current session,
        param user: [ (conversation, name, role_id), ...]
        role_id: Role.(ADMIN/MANAGER/CLIENT/BLOCKED_USER).value
        '''
        for user in users:
            session.add(
                User(conversation=user[0], name=user[1], role_id=user[2]))
        session.commit()

    @staticmethod
    def get_all_users_with_role(session, role_id) -> list:
        '''param role_id: Role.(ADMIN/MANAGER/CLIENT/BLOCKED_USER).value '''
        return session.query(User).filter(User.role_id == role_id).all()

    @staticmethod
    def find_by_id(session, id: int) -> 'User':
        return session.query(User).get(id)

    @staticmethod
    def find_by_name(session, name: str) -> list:
        return session.query(User).filter(User.name == name).all()

    @staticmethod
    def find_by_conversation(session, conversation: int) -> 'User':
        return session.query(User).filter(User.conversation == conversation).first()

    @staticmethod
    def change_name(session, user_id=None, user_conversation=None, new_name: str) -> None:
        if user_id:
            User.find_by_id(session, user_id).name = new_name
        elif user_conversation:
            User.find_by_conversation(
                session, user_conversation).name = new_name
        session.commit()

    # TODO: UNTESTED
    @ staticmethod
    def get_free_manager(session) -> 'User':
        '''Поиск самого свободного менеджера'''
        all_managers = User.get_all_users_with_role(
            session, RoleNames.MANAGER.value)
        managers_factor = []

        for manager in all_managers:
            active_tickets = manager.get_active_tickets(session)
            unprocessed_tickets = Ticket.get_unprocessed_tickets(
                session, manager.id)
            lastWeekCloseTickets = Ticket.get_closed_tickets_by_time(
                session, manager_id, 7)
            lastWeekBlockedTickets = Ticket.blocked_tickets_by_time(
                session, manager_id, 7)

            k1 = len(unprocessed_tickets)
            k2 = len(active_tickets)
            k3 = len(lastWeekCloseTicket) / 7
            k4 = len(lastWeekBlockedTicket) / 7

            q1, q2, q3, q4 = 2, 1, 1, -1

            coef = k1 ** q1 + k2 ** q2 + k3 ** q3 + k4 ** q4

            managers_factor.append(coef)

        index = managers_factor.index(min(managers_factor))
        return all_managers[index]



class Ticket(Base):
    __tablename__ = 'tickets'

    id = Column(Integer, primary_key=True)
    manager_id = Column(Integer, ForeignKey('users.id'))
    client_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String(50))
    start_date = Column(DateTime, default=datetime.now(offset))
    close_date = Column(DateTime)

    # Relationship
    client = relationship('User', foreign_keys=[
        client_id], back_populates='ticket_client')
    manager = relationship('User', foreign_keys=[
        manager_id], back_populates='ticket_manager')

    isblocked = relationship(
        'BlockedTicket', order_by='BlockedTicket.ticket_id', back_populates='ticket')
    messages = relationship(
        'Message', order_by='Message.ticket_id', back_populates='ticket')

    def __repr__(self):
        return f'Title: {self.title}, manager_id={self.manager_id}'

    # TODO

    @staticmethod
    get_closed_tickets_by_time(session, manager_id, days: int):
        pass

    # TODO
    @staticmethod
    blocked_tickets_by_time(session, manager_id, days: int):
        pass

    # TODO
    # https://stackoverflow.com/questions/45775724/sqlalchemy-group-by-and-return-max-date
    # http://old.code.mu/sql/group-by.html
    # http://quabr.com:8182/58620448/sqlalchemy-how-to-use-group-by-correctly-only-full-group-by
    # https://stackoverflow.com/questions/34115174/error-related-to-only-full-group-by-when-executing-a-query-in-mysql
    @staticmethod
    def get_unprocessed_tickets(session, manager_id) -> list:
        joined = session.query(Ticket).join(Ticket.messages)

        maxdate = func.max(Message.date).label('maxdate')

        all_open_tickets = joined.filter(Ticket.close_date.is_(None)).filter(
            Ticket.manager_id == manager_id)

        return 'TODO'

    def appoint_to_manager(self, session, new_manager_id):
        manager = session.query(User).get(new_manager_id)
        if manager != None and manager.role_id == RoleNames.MANAGER.value:
            self.manager_id = new_manager_id
            return 0
        else:
            print("Manager not found")
            return 1

    def add(self, session, manager_id):
        if self.appoint_to_manager(session, manager_id) == 0:
            session.add(self)
            session.commit()
        else:
            print("Couldn't add the ticket")

    def get_all_messages(self, session):
        return session.query(Message).filter(Message.ticket_id == self.id).all()

    def put_refuse_data(self, session, reason):
        new_blocked = BlockedTicket(
            ticket_id=self.id, manager_id=self.manager_id, reason=reason)
        session.add(new_blocked)
        session.commit()

    def reappoint(self, session, refused_list):
        new_managers = User.get_free_managers(session)
        for man in new_managers:
            if man not in refused_list:
                self.appoint_to_manager(session, man.id)
                session.commit()
                return
        self.appoint_to_manager(session, new_managers[0].id)
        session.commit()

    def close(self, session):
        self.close_date = datetime.now(offset)
        session.commit()


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
    ticket = relationship('Ticket', back_populates='messages')
    sender = relationship('User', back_populates='messages')

    @ staticmethod
    def get(session, ticket_id: int, user_id: int):
        '''Получить список все сообщений user_id в данном ticket_id'''
        return session.query(Message).filter(Message.ticket_id == ticket_id).filter(Message.sender_id == user_id).all()


class Token(Base):
    __tablename__ = 'tokens'

    value = Column(Integer, primary_key=True)
    expires_date = Column(DateTime)
    role_id = Column(Integer, ForeignKey('roles.id'))

    # Relationship
    role = relationship('Role', back_populates='tokens')
