"""
Goal: implement the base class for models
"""
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext import declarative

# http://docs.sqlalchemy.org/en/latest/orm/session_basics.html
maker = sessionmaker(autoflush=True,
                     autocommit=False,
                     expire_on_commit=True)
DBSession = scoped_session(maker)
session = None


def init(engine):
    """
    Call this method before using any of the ORM classes.

    :seealso: :meth:get_db_session()
    """
    DBSession.configure(bind=engine)


def get_session():
    global session
    if session is None:
        session = DBSession()
    return session

DeclarativeBase = declarative.declarative_base()
metadata = DeclarativeBase.metadata
