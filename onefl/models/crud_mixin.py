"""
Goal: simplify the code when interacting with entities
"""
from onefl.models.base import get_session


class CRUDMixin():
    """ Helper class sqlalchemy entities """
    __table_args__ = {'extend_existing': True}

    # id = db.Column(db.Integer, primary_key=True)

    @classmethod
    def get_by_id(cls, id):
        if any(
            (isinstance(id, str) and id.isdigit(),
             isinstance(id, (int, float))),):
            session = get_session()
            # return cls.query.get(int(id))
            # return session.query(cls).filter_by(id=int(id)).one()
            return session.query(cls).get(int(id))
        return None

    @classmethod
    def create(cls, **kwargs):
        """ Helper for add() + commit() """
        instance = cls(**kwargs)
        return instance.save()

    def update(self, commit=True, **kwargs):
        """ update object instance """
        for attr, value in kwargs.items():
            setattr(self, attr, value)
        return self.save() if commit else self

    def save(self, commit=True):
        """ save object instance """
        session = get_session()
        session.add(self)

        if commit:
            session.commit()
        return self

    def delete(self, commit=True):
        """ delete object instance """
        session = get_session()
        session.delete(self)
        return commit and session.commit()
