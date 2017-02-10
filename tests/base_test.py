"""
Goal: implement base class for tests using the database

@authors:
    Andrei Sura <sura.andrei@gmail.com>
"""

from unittest import TestCase  # noqa
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound  # noqa
from onefl.config import Config
from onefl.models import base
from onefl.utils import db
from sqlalchemy.orm.exc import MultipleResultsFound  # noqa
from onefl.models.partner_entity import PartnerEntity
from onefl.models.rule_entity import RuleEntity
from onefl.rules import RULE_CODE_F_L_D_R, RULE_CODE_F_L_D_S  # noqa

SETTINGS_FILE = 'config/test_settings_linker.py'


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
        self.config = config
        self.engine = db.get_db_engine(config)
        self.session = db.get_db_session(self.engine,
                                         create_tables=True)
        self.create_rules()
        self.create_partners()

    def create_rules(self):
        """ Create rule rows """
        added_date = datetime.now()

        # with self.assertRaises(NoResultFound):
        #     self.session.query(RuleEntity).filter_by(id=1).one()

        rule_r = self.session.query(RuleEntity).filter_by(
            rule_code=RULE_CODE_F_L_D_R).one_or_none()
        rule_g = self.session.query(RuleEntity).filter_by(
            rule_code=RULE_CODE_F_L_D_S).one_or_none()

        if rule_r is None:
            RuleEntity.create(
                rule_code=RULE_CODE_F_L_D_R,
                rule_description='First Last DOB Race',
                rule_added_at=added_date)

        if rule_g is None:
            RuleEntity.create(
                rule_code=RULE_CODE_F_L_D_S,
                rule_description='First Last DOB Sex',
                rule_added_at=added_date)

        # self.assertEquals(2, rule.id)
        cache = RuleEntity.get_rules_cache(self.session)
        self.assertIsNotNone(cache)
        print(cache)

    def create_partners(self):
        """ Verify we can store PARTNER rows """
        # added_date = utils.get_db_friendly_date_time()
        added_date = datetime.now()

        partner_ufh = self.session.query(PartnerEntity).filter_by(
            partner_code='UFH').one_or_none()

        if partner_ufh is None:
            partner_ufh = PartnerEntity.create(
                partner_code="UFH",
                partner_description="University of Florida",
                partner_added_at=added_date)

            print("Saved fresh row: {}\n".format(partner_ufh))
        self.assertEquals("UFH", partner_ufh.partner_code)

        partner_flm = self.session.query(PartnerEntity).filter_by(
            partner_code='FLM').one_or_none()

        if partner_flm is None:
            partner_flm = PartnerEntity.create(
                partner_code="FLM",
                partner_description="Florida Medicaid",
                partner_added_at=added_date)
            self.assertEquals("FLM", partner_flm.partner_code)

        # verify an error is raised if we try to to find one
        with self.assertRaises(MultipleResultsFound):
            self.session.query(PartnerEntity).filter(
                PartnerEntity.partner_description.like(
                    '%Florida%')).one()

    def tearDown(self):
        """ Drop the tables created """
        super(BaseTestCase, self).tearDown()
        base.metadata.drop_all(self.engine)
