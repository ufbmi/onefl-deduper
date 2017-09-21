"""
Goal: implement tests for database models

@authors:
    Andrei Sura <sura.andrei@gmail.com>
"""
import unittest
import binascii
from datetime import datetime
from sqlalchemy.orm.exc import MultipleResultsFound  # noqa
from sqlalchemy.orm.exc import NoResultFound  # noqa

from base_test import BaseTestCase
from onefl import utils
from onefl.models.partner_entity import PartnerEntity  # noqa
from onefl.models.linkage_entity import LinkageEntity
from onefl.models.rule_entity import RuleEntity
from onefl.rules import RULE_CODE_F_L_D_R, RULE_CODE_F_L_D_S  # noqa


class TestModels(BaseTestCase):

    def setUp(self):
        super(TestModels, self).setUp()

    def create_links(self):
        """ Verify we can store LINKAGE rows """
        cache = RuleEntity.get_rules_cache(self.session)
        added_date = datetime.now()
        ahash = binascii.unhexlify(
            '2B2D67AED8D511E6A41AF45C898E9B67'.encode())
        rule_id = cache.get(RULE_CODE_F_L_D_R)
        uuid_list = [utils.get_uuid(), utils.get_uuid()]

        links = []

        for uuid in uuid_list:
            link = LinkageEntity.create(
                partner_code='UFH',
                rule_id=rule_id,
                linkage_patid='123',
                linkage_flag=0,
                linkage_uuid=uuid,
                linkage_hash=ahash,
                linkage_added_at=added_date)
            self.assertIsNotNone(link.id)
            links.append(link)
            print(link)

        # Search links matching a hash
        links_by_hash = self.session.query(LinkageEntity).filter_by(
            linkage_hash=ahash).all()
        self.assertIsNotNone(links_by_hash)
        self.assertTrue(len(links_by_hash) == 2)

        unique = LinkageEntity.get_unique_uuids(links, links_by_hash)
        self.assertTrue(len(unique) == 2)
        print(unique)

    def test_it(self):
        self.create_links()


if __name__ == '__main__':
    unittest.main()
