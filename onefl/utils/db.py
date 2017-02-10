"""
Goal: store utility functions for database interaction

@authors:
    Andrei Sura <sura.andrei@gmail.com>
"""
# import sys
import sqlalchemy as db
from onefl.models import base
from onefl import logutils
log = logutils.get_a_logger(__file__)


DB_TYPE_MSSQL = 'MSSQL'
DB_TYPE_MYSQL = 'MYSQL'
DB_TYPE_TEST = 'TEST'

# try:
#     from config.settings import DB_USER, DB_PASS, DB_NAME, DB_HOST, DB_PORT
# except:
#     sys.exit("Please create the config/settings.py file. \n"
#              "  $ cp config/settings.py.example config/settings.py \n")

DB_POOL = None


def get_db_url_sqlserver(config):
    """
    Helper function for creating the "pyodbc" connection string.

    @see http://docs.sqlalchemy.org/en/latest/dialects/mssql.html
    @see https://code.google.com/p/pyodbc/wiki/ConnectionStrings
    """
    from urllib import parse
    params = parse.quote(
        "Driver={{FreeTDS}};Server={};Port={};"
        "Database={};UID={};PWD={};"
        .format(config['DB_HOST'], config['DB_PORT'], config['DB_NAME'],
                config['DB_USER'], config['DB_PASS']))
    return 'mssql+pyodbc:///?odbc_connect={}'.format(params)


def get_db_url_mysql(config):
    """
    Format the configuration parameters to build the connection string
    """
    if 'DB_URL_TESTING' in config:
        return config['DB_URL_TESTING']

    return 'mysql+mysqlconnector://{}:{}@{}/{}' \
           .format(config['DB_USER'],
                   config['DB_PASS'],
                   config['DB_HOST'],
                   config['DB_NAME'])


def get_db_url(config):
    """
    Pick a database url based on DATABASE_TYPE
    """
    db_type = config.get('DB_TYPE').upper()

    if DB_TYPE_MSSQL == db_type:
        url = get_db_url_sqlserver(config)
    elif DB_TYPE_MYSQL == db_type:
        url = get_db_url_mysql(config)
    elif DB_TYPE_TEST == db_type:
        # to use memory: "sqlite:///:memory:"
        url = 'sqlite:///sqlite.db'
    else:
        raise Exception("Unexpected config value for 'DB_TYPE': {}"
                        .format(db_type))
    return url


def get_db_engine(config):
    """
    @see http://docs.sqlalchemy.org/en/latest/core/connections.html
    """
    url = get_db_url(config)

    try:
        engine = db.create_engine(url,
                                  pool_size=10,
                                  max_overflow=5,
                                  pool_recycle=3600,
                                  echo=False)
    except TypeError as exc:
        log.warning("Got exc from db.create_engine(): {}".format(exc))
        engine = db.create_engine(url, echo=False)

    return engine


def get_db_session(engine, create_tables=False):
    """
    Connect to the database and return a Session object

    :param create_tables: boolean used to request table creation
    """
    log.debug("Call get_db_session()")
    base.init(engine)
    session = base.DBSession()

    if create_tables:
        base.metadata.create_all(engine)

    return session

# def get_db_url(db_host, db_port, db_name, db_user, db_pass):
#     """
#     Helper function for creating the "pyodbc" connection string.
#
#     @see http://docs.sqlalchemy.org/en/latest/dialects/mssql.html
#     @see https://code.google.com/p/pyodbc/wiki/ConnectionStrings
#     """
#     params = parse.quote(
#         "Driver={{FreeTDS}};Server={};Port={};"
#         "Database={};UID={};PWD={};"
#         .format(db_host, db_port, db_name, db_user, db_pass))
#     return 'mssql+pyodbc:///?odbc_connect={}'.format(params)
#
#
# def get_db_engine():
#     """
#     Create the database engine connection.
#     @see http://docs.sqlalchemy.org/en/latest/core/engines.html
#
#     :return: Dialect object which can either be used directly
#             to interact with the database, or can be passed to
#             a Session object to work with the ORM.
#     """
#     global DB_POOL
#
#     if DB_POOL is None:
#         url = get_db_url(db_host=DB_HOST, db_port=DB_PORT, db_name=DB_NAME,
#                          db_user=DB_USER, db_pass=DB_PASS)
#         DB_POOL = db.create_engine(url,
#                                    pool_size=10,
#                                    max_overflow=5,
#                                    pool_recycle=3600)
#
#     try:
#         DB_POOL.execute("USE {db}".format(db=DB_NAME))
#     except db.exc.OperationalError:
#         log.error('Database {db} does not exist.'.format(db=DB_NAME))
#
#     return DB_POOL
