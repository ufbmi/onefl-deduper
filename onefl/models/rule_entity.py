"""
ORM for "rule" table

@authors:
    Andrei Sura <sura.andrei@gmail.com>

+------------------+------------------+------+-----+---------+
| Field            | Type             | Null | Key | Default |
+------------------+------------------+------+-----+---------+
| rule_id          | int(10) unsigned | NO   | PRI | NULL    |
| rule_code        | varchar(255)     | NO   | UNI | NULL    |
| rule_description | varchar(255)     | NO   |     | NULL    |
| rule_added_at    | datetime         | NO   |     | NULL    |
+------------------+------------------+------+-----+---------+
"""

import sqlalchemy as db
from onefl.models.base import DeclarativeBase
from onefl.models.crud_mixin import CRUDMixin

__all__ = ['RuleEntity']


class RuleEntity(CRUDMixin, DeclarativeBase):

    """ Store rules used by the partners sending us the data """
    __tablename__ = 'RULE'

    id = db.Column('RULE_ID', db.Integer, primary_key=True)
    rule_code = db.Column('RULE_CODE', db.Text(10),
                          nullable=False, unique=True)
    rule_description = db.Column('RULE_DESCRIPTION', db.Text(255),
                                 nullable=False)
    rule_added_at = db.Column('RULE_ADDED_AT', db.DateTime,
                              nullable=False)

    @staticmethod
    def get_rules_cache(session):
        """
        :return dictionary: with all available {rule_code -> rule.id} mappings
        """
        rules = session.query(RuleEntity).all()
        result = {rule.rule_code: rule.id for rule in rules}
        return result

    def __repr__(self):
        """ Return a friendly object representation """
        return "<RuleEntity(rule_id: {0.id}, "\
            "rule_code: {0.rule_code}, " \
            "rule_description: {0.rule_description}, " \
            "rule_added_at: {0.rule_added_at})>".format(self)
