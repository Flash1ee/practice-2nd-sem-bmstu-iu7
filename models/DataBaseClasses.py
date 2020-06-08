
from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from sqlalchemy import ForeignKey, desc, Text, asc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timedelta
from enum import Enum
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
    def init(session) -> None:
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
        if len(User.get_all_users_with_role(session, 2)) < 2:
            print("COUNT MANAGERS IS {len(User.get_all_users_with_role(session, 2))}")
            return -1
        his_tickets = self.get_active_tickets(session)
        self.role_id = RoleNames.CLIENT.value
        for ticket in his_tickets:
            ticket.reappoint(session)
        
        session.commit()

    def get_all_tickets(self, session) -> list:
        
        tickets = session.query(Ticket)

        if self.role_id == RoleNames.MANAGER.value:
            tickets = tickets.filter(Ticket.manager_id == self.id)

        elif self.role_id == RoleNames.CLIENT.value:
            tickets = tickets.filter(Ticket.client_id == self.id)

        return tickets.all()

    def identify_ticket(self, session) -> int:
        last_message = session.query(Message).filter_by(
            sender_id=self.id).filter(Message.ticket_id).order_by(desc(Message.date)).first()

        if not last_message:
            return None

        last_ticket_id = last_message.ticket_id
        return last_ticket_id

    # Static methods

    @staticmethod
    def add(session, conversation: int, name: str, role_id: int) -> 'User':
        '''
        Добавляет нового пользователя в базу.
        Возвращаемое значение: новый пользователь или старый, если пользователь уже есть в базе.
        role_id: Role.(ADMIN/MANAGER/CLIENT/BLOCKED_USER).value
        Autocommit = ON
        '''
        check_user = User.find_by_conversation(session, conversation)
        if check_user:
            return check_user

        new_user = User(conversation=conversation, name=name, role_id=role_id)
        session.add(new_user)
        session.commit()

        return new_user

    @staticmethod
    def get_messages(session, conversation: int) -> list:
        '''
            Возврашает все сообщения пользователя с chat_id == conversation
            Сортировка: сначала новые.
        '''
        user = User.find_by_conversation(session, conversation)

        return session.query(Message).filter(Message.sender_id == user.id).order_by(desc(Message.date)).all()

    @staticmethod
    def get_all_users_with_role(session, role_id: int) -> list:
        '''param role_id: Role.(ADMIN/MANAGER/CLIENT/BLOCKED_USER).value 
        (В случае, если нет ни одного User, вернет пустой list)
        '''
        return session.query(User).filter_by(role_id=role_id).all()

    @staticmethod
    def find_by_id(session, id: int) -> 'User or None':
        return session.query(User).get(id)

    @staticmethod
    def find_by_name(session, name: str) -> list:
        '''Если не найдено ни одного пользователя - пустой список'''
        return session.query(User).filter(User.name == name).all()

    @staticmethod
    def find_by_conversation(session, user_conversation: int) -> 'User or None':
        return session.query(User).filter(User.conversation == user_conversation).first()

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
            unprocessed_tickets = Ticket.get_unprocessed_tickets(
                session, manager.id)
            # active_tickets = manager.get_active_tickets(session)
            lastWeekCloseTickets = Ticket.get_closed_tickets_by_time(
                session, manager.id, 7)
            lastWeekBlockedTickets = Ticket.get_blocked_tickets_by_time(
                session, manager.id, 7)

            k1 = len(unprocessed_tickets)
            k2 = session.query(Ticket).filter(Ticket.manager_id == manager.id, Ticket.close_date.is_(None)).count() 
            # k2 = len(active_tickets)
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
    start_date = Column(DateTime, nullable=False,
                        server_default=func.current_timestamp())
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

    @staticmethod
    def get_closed_tickets_by_time(session, manager_id, days: int) -> list:
        curr_date = datetime.now()
        key_time = curr_date.time()
        key_date = curr_date.fromordinal(curr_date.date().toordinal() - days)
        key_date = datetime.combine(key_date, key_time)
        return session.query(Ticket).filter(Ticket.manager_id == manager_id).filter(
            Ticket.close_date > key_date).all()

    @staticmethod
    def get_blocked_tickets_by_time(session, manager_id, days: int) -> list:
        curr_date = datetime.now()
        key_time = curr_date.time()
        key_date = curr_date.fromordinal(curr_date.date().toordinal() - days)
        key_date = datetime.combine(key_date, key_time)
        return session.query(BlockedTicket).filter(BlockedTicket.manager_id == manager_id).filter(
            BlockedTicket.date > key_date).all()

    @staticmethod
    def get_unprocessed_tickets(session, manager_id) -> list:

        res = session.query(Message.ticket_id, func.max(Message.date)).filter(
            Message.ticket_id != None).group_by(Message.ticket_id).all()
        ticks = []

        for a in res:
            msg = session.query(Message).filter(Message.ticket_id != None).filter(
                Message.ticket_id == a[0]).filter(Message.date == a[1])[0]
            if msg.sender_id != manager_id and msg.ticket.manager_id == manager_id:
                ticks.append(msg.ticket_id)

        return ticks

    def get_wait_time(self, session) -> 'Timedelta or None':
        '''
            Возвращает wait_time текущего тикета или None, если
            последнее сообщение в тикете было от менеджера
        '''
        last_manager_message = session.query(Message).filter(
            Message.ticket_id == self.id, Message.sender_id == self.manager_id).order_by(desc(Message.date)).first()

        if not last_manager_message:
            first_client_message = session.query(Message).filter(
                Message.ticket_id == self.id, Message.sender_id == self.client_id).order_by(asc(Message.date)).first()
        else:
            first_client_message = session.query(Message).filter(
                Message.ticket_id == self.id, Message.sender_id == self.client_id, Message.date > last_manager_message.date).order_by(asc(Message.date)).first()

        if not first_client_message:
            return timedelta(microseconds=0)
        
        diff = datetime.now() - first_client_message.date

        return diff - timedelta(microseconds=diff.microseconds)

        
    @staticmethod
    def get_all_messages(session, ticket_id: int, sender_id: int = None) -> list:
        messages = session.query(Message).filter(Message.ticket_id == ticket_id).order_by(desc(Message.date))

        if sender_id:
            messages = messages.filter(Message.sender_id == sender_id)

        return messages.all()

    def put_refuse_data(self, session, reason):
        '''
        Метод создает новый объект класса BlockedTicket, в котором содержится информация
        об отказе от текущего тикета
        '''
        new_blocked = BlockedTicket(
            ticket_id=self.id, manager_id=self.manager_id, reason=reason)
        session.add(new_blocked)
        session.commit()

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
        return rc

    def close(self, session):
        self.close_date = datetime.now()
        session.commit()

    @staticmethod
    def create(session, title: str, conversation: str) -> 'Ticket or None':
        '''
        Метод создает новый объект класса Ticket с заголовком title, находит client_id
        по переданному параметру conversation, находит manager_id как наиболее свободного менеджера 
        (метод User.get_free_manager) и созданный объект помещает в базу данных.
        Возвращает Ticket, если процесс выполнен успешно, и None, если в базе данных нет менеджера.
        '''
        new_ticket = Ticket(title=title)

        client = session.query(User).filter(User.conversation == conversation).first()
        new_ticket.client_id = client.id

        manager = User._get_free_manager(session, [])

        # если менеджеров нет вообще
        if not manager:
            return None

        new_ticket.manager_id = manager.id

        session.add(new_ticket)
        session.commit()

        return new_ticket

    @staticmethod
    def get_by_id(session, ticket_id) -> 'Ticket or None':
        return session.query(Ticket).get(ticket_id)


class BlockedTicket(Base):
    __tablename__ = 'blocked_tickets'

    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey('tickets.id'))
    manager_id = Column(Integer, ForeignKey('users.id'))
    reason = Column(String(50))
    date = Column(DateTime, nullable=False,
                  server_default=func.current_timestamp())

    # Relationship
    ticket = relationship('Ticket', back_populates='isblocked')


class Message(Base):
    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey('tickets.id'))
    sender_id = Column(Integer, ForeignKey('users.id'))
    body = Column(Text)
    date = Column(DateTime, nullable=False,
                  server_default=func.current_timestamp())

    # Relationship
    ticket = relationship('Ticket', back_populates='messages')
    sender = relationship('User', back_populates='messages')

    @staticmethod
    def add(session, body: str, ticket_id: int, sender_conversation: int) -> None:
        '''Добавить сообщение в базу'''

        sender_id = User.find_by_conversation(session, sender_conversation).id

        session.add(Message(ticket_id=ticket_id,
                            sender_id=sender_id, body=body))
        session.commit()


class Token(Base):
    __tablename__ = 'tokens'
    value = Column(String(12), primary_key=True, autoincrement=False)
    date = Column(DateTime, nullable=False,
                  server_default=func.current_timestamp())
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
        if token and token.date + timedelta(days=1) > datetime.now():
            return token
        return None

    @staticmethod
    def garbage_collector(session) -> None:
        '''Удаляет все токены из БД, срок которых истек'''
        tokens = session.query(Token).filter(
            func.ADDDATE(Token.date, 1) < datetime.now()).all()
        for token in tokens:
            session.delete(token)
        session.commit()
