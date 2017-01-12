"""
Goal: implement base class for tests using the database

@authors:
    Andrei Sura <sura.andrei@gmail.com>
"""

from unittest import TestCase  # noqa
from onefl.config import Config
from onefl.models import base
from onefl.utils import db

SETTINGS_FILE = 'config/settings_tests.py'


class BaseTestCase(TestCase):
    """
    Tests for database interaction extend this class.
    @see http://docs.sqlalchemy.org/en/latest/orm/session_transaction.html#session-external-transaction  # noqa
    """

    def __init__(self, *args, **kwargs):
        super(BaseTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        """ Set the test database engine/session """

        super(BaseTestCase, self).setUp()
        config = Config(root_path='.', defaults={})
        config.from_pyfile(SETTINGS_FILE)
        self.engine = db.get_db_engine(config)
        self.session = db.get_db_session(self.engine,
                                         create_tables=True)

    def tearDown(self):
        """ Drop the tables created """
        super(BaseTestCase, self).tearDown()
        base.metadata.drop_all(self.engine)
