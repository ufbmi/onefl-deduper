"""
ORM for "partner" table

@authors:
    Andrei Sura <sura.andrei@gmail.com>
"""

import sqlalchemy as db
from onefl.models.base import DeclarativeBase
from onefl.models.crud_mixin import CRUDMixin


"""
+---------------------+------------------+------+-----+---------+
| Field               | Type             | Null | Key | Default |
+---------------------+------------------+------+-----+---------+
| partner_code        | varchar(3)       | NO   | UNI | NULL    |
| partner_description | varchar(255)     | NO   |     | NULL    |
| partner_added_at    | datetime         | NO   |     | NULL    |
+---------------------+------------------+------+-----+---------+
"""

__all__ = ['PartnerEntity']


class PartnerEntity(CRUDMixin, DeclarativeBase):

    """ Store partners sendig us the data """
    __tablename__ = 'PARTNER'

    partner_code = db.Column('PARTNER_CODE', db.Text(3), primary_key=True)
    partner_description = db.Column('PARTNER_DESCRIPTION', db.Text,
                                    nullable=False)
    partner_added_at = db.Column('PARTNER_ADDED_AT', db.DateTime,
                                 nullable=False)

    def __repr__(self):
        """ Return a friendly object representation """
        return "<PartnerEntity (partner_code: {0.partner_code}, " \
            "partner_description: {0.partner_description}, " \
            "partner_addded_at: {0.partner_added_at})>".format(self)
