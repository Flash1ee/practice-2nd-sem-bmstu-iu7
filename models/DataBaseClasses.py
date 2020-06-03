from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Text
from sqlalchemy import ForeignKey, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import except_
from datetime import datetime, timezone, timedelta
from enum import Enum
from pprint import pprint
from sqlalchemy.sql import func
import random
import string

Base = declarative_base()


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

    def appoint(self, session, role_id: int) -> None:
        '''param role_id: Role.(ADMIN/MANAGER/CLIENT/BLOCKED_USER).value 
            Autocommit = ON
        '''
        self.role_id = role_id
        session.commit()
        
    def demote_manager(self, session) -> None:
        '''Разжаловать менеджера до статуса клиента.
        Все тикеты бывшего менеджера автоматически будут распределены между остальными
        '''
        his_tickets = self.get_active_tickets(session)

        for ticket in his_tickets:
            ticket.reappoint(session)

        self.role_id = RoleNames.CLIENT.value
        session.commit()

    def add(self, session) -> None:
        '''Autocommit = ON'''
        session.add(self)
        session.commit()

    def get_all_tickets(self, session) -> list:
        if self.role_id == RoleNames.ADMIN.value:
            tickets = session.query(Ticket).all()
        elif self.role_id == RoleNames.MANAGER.value:
            tickets = session.query(Ticket).filter(
                Ticket.manager_id == self.id).all()
        elif self.role_id == RoleNames.CLIENT.value:
            tickets = session.query(Ticket).filter(
                Ticket.client_id == self.id).all()
        return tickets

    def identify_ticket(self, session) -> int:
        last_message = session.query(Message).filter_by(sender_id = self.id).order_by(desc(Message.date)).first()
        last_ticket_id = last_message.ticket_id
        return last_ticket_id


    # Static methods

    @staticmethod
    def add_several(session, users: list) -> None:
        '''
        param session: current session,
        param user: [ (conversation, name, role_id), ... ]
        role_id: Role.(ADMIN/MANAGER/CLIENT/BLOCKED_USER).value
        Autocommit = ON
        '''
        for user in users:
            session.add(User(conversation=user[0], name=user[1], role_id=user[2]))
        session.commit()

    @staticmethod
    def get_all_users_with_role(session, role_id: int) -> list:
        '''param role_id: Role.(ADMIN/MANAGER/CLIENT/BLOCKED_USER).value 
        (В случае, если нет ни одного User, вернет пустой list)
        '''
        return session.query(User).filter_by(role_id = role_id).all()

    @staticmethod
    def find_by_id(session, id: int) -> 'User or None':
        return session.query(User).get(id)

    @staticmethod
    def find_by_name(session, name: str) -> list:
        '''Если не найдено ни одного пользователя - пустой список'''
        return session.query(User).filter(User.name == name).all()

    @staticmethod
    def find_by_conversation(session, user_conversation: int) -> 'User or None':
        return session.query(User).filter_by(conversation = user_conversation).first()

    @staticmethod
    def change_name(session, new_name, user_conversation) -> None:
        '''Ответственность за наличие пользователя с данным 
            user_conversation в БД на вызывающей стороне
            Autocommit = ON
        '''
        User.find_by_conversation(session, user_conversation).name = new_name
        session.commit()

    @ staticmethod
    def _get_free_manager(session, refusal_list) -> 'User or None':
        '''Не должна использоваться никем, кроме как отвечающими за БД
        Возвращает самого свободного менеджера, отсутствующего в refusal_list
        В случае, если все менеджеры есть в refusal_list, возвращает None'''
        all_managers = dict.fromkeys(User.get_all_users_with_role(
            session, RoleNames.MANAGER.value), None)

        for manager in all_managers:
            if manager.id in refusal_list:
                continue

            active_tickets = manager.get_active_tickets(session)
            unprocessed_tickets = Ticket.get_unprocessed_tickets(
                session, manager.id)
            lastWeekCloseTickets = Ticket.get_closed_tickets_by_time(
                session, manager.id, 7)
            lastWeekBlockedTickets = Ticket.get_blocked_tickets_by_time(
                session, manager.id, 7)

            k1 = len(unprocessed_tickets)
            k2 = len(active_tickets)
            k3 = len(lastWeekCloseTickets) / 7
            k4 = len(lastWeekBlockedTickets) / 7

            q1, q2, q3 = 2, 1, 1

            coef = k1 ** q1 + k2 ** q2 + k3 ** q3

            if k4 > 1: 
                coef /= k4

            all_managers[manager] = coef

        all_managers = {key: val for key,
                        val in all_managers.items() if val != None}

        if not len(all_managers):
            return None

        return sorted(all_managers, key=all_managers.get)[0]


class Ticket(Base):
    __tablename__ = 'tickets'

    id = Column(Integer, primary_key=True)
    manager_id = Column(Integer, ForeignKey('users.id'))
    client_id = Column(Integer, ForeignKey('users.id'))
    title = Column(String(50))
    start_date = Column(DateTime, default=datetime.now())
    close_date = Column(DateTime, default=None)

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

    # TODO UNTESTED
    @staticmethod
    def get_closed_tickets_by_time(session, manager_id, days: int) -> list:
        curr_date = datetime.now()
        key_time = curr_date.time()
        key_date = curr_date.fromordinal(curr_date.date().toordinal() - days)
        key_date = datetime.combine(key_date, key_time)
        return session.query(Ticket).filter(Ticket.manager_id == manager_id).filter(
            Ticket.close_date > key_date).all()

    # TODO UNTESTED
    @staticmethod
    def get_blocked_tickets_by_time(session, manager_id, days: int) -> list:
        curr_date = datetime.now()
        key_time = curr_date.time()
        key_date = curr_date.fromordinal(curr_date.date().toordinal() - days)
        key_date = datetime.combine(key_date, key_time)
        return session.query(BlockedTicket).filter(BlockedTicket.manager_id == manager_id).filter(
            BlockedTicket.date > key_date).all()

    # TODO
    # https://stackoverflow.com/questions/45775724/sqlalchemy-group-by-and-return-max-date
    # http://old.code.mu/sql/group-by.html
    # http://quabr.com:8182/58620448/sqlalchemy-how-to-use-group-by-correctly-only-full-group-by
    # https://stackoverflow.com/questions/34115174/error-related-to-only-full-group-by-when-executing-a-query-in-mysql
    @staticmethod
    def get_unprocessed_tickets(session, manager_id) -> list:
        #joined = session.query(Message).join(Ticket.messages)
        #print(joined[1].id, joined[1].ticket_id, joined[1].date, joined[1].sender_id, joined[1].body)
        #print(joined[1].ticket.id, joined[1].ticket.client_id, joined[1].ticket.manager_id, joined[1].ticket.title, joined[1].ticket.start_date)
        #message = session.query(Message).filter(Message.id == 7)[0]
        #print(message.ticket.id, message.ticket.client_id, message.ticket.manager_id, message.ticket.title, message.ticket.start_date)
        # print(message.ticket.manager_id)

        res = session.query(Message.ticket_id, func.max(
            Message.date)).group_by(Message.ticket_id).all()
        ticks = []
        for a in res:
            message = session.query(Message).filter(
                Message.ticket_id == a[0]).filter(Message.date == a[1])[0]
            if message.sender_id != manager_id and message.ticket.manager_id == manager_id:
                ticks.append(message.ticket_id)

        # all_open_tickets = joined.filter(Ticket.close_date.is_(None)).filter(
        #    Ticket.manager_id == manager_id)

        return ticks

    def get_all_messages(self, session):
        return session.query(Message).filter(Message.ticket_id == self.id).all()

    def put_refuse_data(self, session, reason):
        '''
        Метод создает новый объект класса BlockedTicket, в котором содержится информация
        об отказе от текущего тикета
        '''
        new_blocked = BlockedTicket(
            ticket_id=self.id, manager_id=self.manager_id, reason=reason)
        session.add(new_blocked)
        session.commit()

    # UNTESTED
    def reappoint(self, session):
        '''
        Метод получает список менеджеров, уже отказавшихся от данного тикета,
        получает наиболее свободного менеджера, который еще не отказывался от тикета,
        с помощью метода User.get_free_manager и переназначает тикет на него. Если все
        зарегистрированные менеджеры отказались от тикета, метод принудительно назначает 
        его на самого незагруженного менеджера и возвращает 1. В иных случаях возвращается 0.
        '''
        refusal_list = [bt.manager_id for bt in session.query(BlockedTicket).filter(
            BlockedTicket.ticket_id == self.id).all()]

        rc = 0
        new_manager = User._get_free_manager(session, refusal_list)

        if new_manager is None:
            new_manager = User._get_free_manager(session, [])
            rc = 1    # подаем сигнал админу, что от этого тикета уже все отказались

        self.manager_id = new_manager.id
        session.commit()
        return rc

    def close(self, session):
        self.close_date = datetime.now()
        session.commit()

    # TODO: UNTESTED
    @staticmethod
    def create(session, title, conversation):
        '''
        Метод создает новый объект класса Ticket с заголовком title, находит client_id
        по переданному параметру conversation, находит manager_id как наиболее свободного менеджера 
        (метод User.get_free_manager) и созданный объект помещает в базу данных.
        Возвращает 0, если процесс выполнен успешно, и 1, если в базе данных нет менеджера.
        '''
        new_ticket = Ticket(title=title)

        client = session.query(User).filter(User.conversation == conversation)[0]
        new_ticket.client_id = client.id
            
        manager = User._get_free_manager(session, [])
        # если менеджеров нет вообще
        if manager is None:
            return 1
        new_ticket.manager_id = manager.id
        session.add(new_ticket)
        session.commit()
        return 0

    @staticmethod
    def get_by_id(session, ticket_id):
        return session.query(Ticket).get(ticket_id)


class BlockedTicket(Base):
    __tablename__ = 'blocked_tickets'

    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey('tickets.id'))
    manager_id = Column(Integer, ForeignKey('users.id'))
    reason = Column(String(50))
    date = Column(DateTime, default=datetime.now())

    # Relationship
    ticket = relationship('Ticket', back_populates='isblocked')


class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey('tickets.id'))
    sender_id = Column(Integer, ForeignKey('users.id'))
    body = Column(Text)
    date = Column(DateTime, default=datetime.now())

    # Relationship
    ticket = relationship('Ticket', back_populates='messages')
    sender = relationship('User', back_populates='messages')

    @staticmethod
    def get(session, ticket_id: int, user_id: int):
        '''Получить список всеx сообщений user_id в данном ticket_id'''
        return session.query(Message).filter(
            Message.ticket_id == ticket_id).filter(Message.sender_id == user_id).all()

    @staticmethod
    def add(session, body: str, ticket_id: int, sender_conversation: int):
        '''Добавить сообщение в базу'''

        sender_id = User.find_by_conversation(session, sender_conversation).id

        session.add(Message(ticket_id=ticket_id, sender_id=sender_id, body=body))
        session.commit()
    


class Token(Base):
    __tablename__ = 'tokens'

    value = Column(String(12), primary_key=True, autoincrement=False)
    expires_date = Column(
        DateTime, default=datetime.now() + timedelta(days=1))
    role_id = Column(Integer, ForeignKey('roles.id'))

    # Relationship
    role = relationship('Role', back_populates='tokens')

    # Instance methods

    def activate(self, session) -> None:
        '''Активирует токен. (Удаляет из БД)
        Ответственность за наличие токена в базе лежит на 
        вызывающей стороне
        '''
        session.delete(self)
        session.commit()

    # Static methods

    @staticmethod
    def generate(session, role_id) -> 'Token':
        '''Генерирует новый токен'''
        LENGTH = 12
        token_value = ''.join(random.choice(
            string.ascii_letters + string.digits) for i in range(LENGTH))
        new_token = Token(value=token_value, role_id=role_id)
        session.add(new_token)
        session.commit()
        return new_token

    @staticmethod
    def find(session, token_value: str) -> 'Token or None':
        '''Внимание: перед попыткой обратиться к полям полученного объекта,
        необходимо обязательно сделать проверку на None'''

        token = session.query(Token).get(token_value)
        if token and token.expires_date > datetime.now():
            return token
        return None


    @staticmethod
    def garbage_collector(session) -> None:
        '''Удаляет все токены из БД, срок которых истек'''
        tokens = session.query(Token).filter(
            Token.expires_date < datetime.now()).all()
        for token in tokens:
            session.delete(token)
        session.commit()
