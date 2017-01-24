"""
Goal: implement tests for database models

@authors:
    Andrei Sura <sura.andrei@gmail.com>
"""

import unittest
import binascii
from datetime import datetime
from sqlalchemy.orm.exc import MultipleResultsFound
from sqlalchemy.orm.exc import NoResultFound

from base_test import BaseTestCase
from onefl import utils
from onefl.models.partner_entity import PartnerEntity
from onefl.models.linkage_entity import LinkageEntity
from onefl.models.rule_entity import RuleEntity
from onefl.rules import RULE_CODE_F_L_D_R, RULE_CODE_F_L_D_G  # noqa


class TestModels(BaseTestCase):

    def setUp(self):
        super(TestModels, self).setUp()

    def create_rules(self):
        """ Create rule rows """
        added_date = datetime.now()

        with self.assertRaises(NoResultFound):
            self.session.query(RuleEntity).filter_by(id=1).one()

        rule = RuleEntity.create(
            rule_code=RULE_CODE_F_L_D_R,
            rule_description='First Last DOB Race',
            rule_added_at=added_date)
        print(rule)
        self.assertEquals(1, rule.id)
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

    def create_links(self):
        """ Verify we can store LINKAGE rows """
        pers_uuid = utils.get_uuid_bin()

        # For the real code we cun just copy the
        ahash = binascii.unhexlify('2B2D67AED8D511E6A41AF45C898E9B67'.encode())
        added_date = datetime.now()

        link = LinkageEntity.create(
            partner_code='UFH',
            linkage_patid='123',
            linkage_uuid=pers_uuid,
            linkage_hash=ahash,
            linkage_added_at=added_date)
        self.assertIsNotNone(link.id)

        print(link)

        # Search links matching a hash -- should return at most one row
        links_by_hash = self.session.query(LinkageEntity).filter_by(
            linkage_hash=ahash).all()
        self.assertIsNotNone(links_by_hash)

    def test_it(self):
        self.create_partners()
        self.create_links()


if __name__ == '__main__':
    unittest.main()
