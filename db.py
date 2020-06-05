from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from json import load
from models.DataBaseClasses import *

config = load(open("./config.json"))
engine = create_engine(config['database']['url'], echo=config['debug'], poolclass=NullPool)
Session = sessionmaker(bind=engine)


if 'create' in config['database'].keys() and config['database']['create']:
    Base.metadata.create_all(engine)
    Roles.init(session)


# session = Session()