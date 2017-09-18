"""
ORM for "linkage" table

@authors:
    Andrei Sura <sura.andrei@gmail.com>
"""
import sqlalchemy as db
import binascii
from onefl import utils
from onefl.models.base import DeclarativeBase
from onefl.models.crud_mixin import CRUDMixin
from onefl.models.partner_entity import PartnerEntity
from onefl.models.rule_entity import RuleEntity  # noqa

"""
+------------------+---------------------+------+-----+---------+
| Field            | Type                | Null | Key | Default |
+------------------+---------------------+------+-----+---------+
| linkage_id       | bigint(20) unsigned | NO   | PRI | NULL    |
| partner_code     | varchar(3)          | NO   | MUL | NULL    |
| rule_id          |                     | NO   | MUL | NULL    |
| linkage_patid    | varchar(64)         | NO   | MUL | NULL    |
| linkage_flag     | int                 | NO   | MUL | NULL    |
| linkage_uuid     | varchar(32)         | NO   | MUL | NULL    |
| linkage_hash     | binary(32)          | NO   | MUL | NULL    |
| linkage_added_at | datetime            | NO   | MUL | NULL    |
+------------------+---------------------+------+-----+---------+
"""

FLAG_HASH_NOT_FOUND = 0  # 'hash not found'
FLAG_HASH_FOUND = 1  # 'hash found'
FLAG_SKIP_MATCH = 2  # flag rows which should not participate in matching


__all__ = ['LinkageEntity']


class LinkageEntity(CRUDMixin, DeclarativeBase):

    """ Maps the UUIDs to "hashed chunks" """
    __tablename__ = 'LINKAGE'

    id = db.Column('LINKAGE_ID', db.Integer, primary_key=True)
    partner_code = db.Column('PARTNER_CODE', db.Text(3),
                             db.ForeignKey('PARTNER.PARTNER_CODE'),
                             nullable=False)

    rule_id = db.Column('RULE_ID', db.Integer,
                        db.ForeignKey('RULE.RULE_ID'), nullable=False)

    # This column stores the original (unscrambled) patid
    linkage_patid = db.Column('LINKAGE_PATID', db.Text(64), nullable=False)
    linkage_flag = db.Column('LINKAGE_FLAG', db.Integer, nullable=False)

    # The generated ID that de-duplicates records
    linkage_uuid = db.Column('LINKAGE_UUID', db.Text(32), nullable=False)

    # The hashed representation of the patient data
    # We create UUIDs for patients without any hashes
    # TODO: decide if we would allow to update the hash from NULL to some value
    linkage_hash = db.Column('LINKAGE_HASH', db.Binary(32), nullable=True)

    # timestamp
    linkage_added_at = db.Column('LINKAGE_ADDED_AT', db.DateTime,
                                 nullable=False)

    # @OneToOne
    partner = db.orm.relationship(PartnerEntity, uselist=False, lazy='joined')
    rule = db.orm.relationship(RuleEntity, uselist=False, lazy='joined')

    @staticmethod
    def short_hash(val):
        return val[:8]

    def friendly_hash(self):
        return utils.hexlify(self.linkage_hash)

    def needs_to_skip_match_for_partner(self, partner_code):
        """
        Note: This functions is used to insure that ambiguous hashes
        are ignored, which results in a reduction of de-duplication rate.
        """
        if (self.partner_code == partner_code or
                self.linkage_flag == FLAG_SKIP_MATCH):
            return True
        return False

    @staticmethod
    def init_hash_uuid_lut(session, hashes):
        """
        From the list [x, y, z] of hashes return
        a dictionary which tells if a chunk was `linked` or not:
            {x: LinkageEntity, y: LinkageEntity, z: None}
        """
        # Note: unhexlify is necessary since the database stores
        # binary representations of the hashes
        bin_hashes = [binascii.unhexlify(ahash.encode('utf-8'))
                      for ahash in hashes]
        links = session.query(LinkageEntity).filter(
            LinkageEntity.linkage_hash.in_(bin_hashes)).all()
        links_cache = {link.friendly_hash(): link for link in links}

        lut = {}

        # Extra loop so we can provide an entry for hashes not found in the db
        for ahash in hashes:
            lut[ahash] = links_cache.get(ahash, None)

        return lut

    def __repr__(self):
        """ Return a friendly object representation """

        return "<LinkageEntity (linkage_id: {0.id}, "\
            "partner_code: {0.partner_code}, " \
            "rule_id: {0.rule_id}, "\
            "linkage_patid: {0.linkage_patid}, "\
            "linkage_flag: {0.linkage_flag}, "\
            "linkage_uuid: {0.linkage_uuid}, "\
            "linkage_hash: {1}, "\
            "linkage_addded_at: {0.linkage_added_at})>".format(
                self,
                binascii.hexlify(self.linkage_hash)
            )
