"""
Goal: Implement a helper class used for cleaning patient data
    elements before hashing (to increase the chance of a match)

Authors:
     Andrei Sura <sura.andrei@gmail.com>
"""
from onefl import utils


class NormalizedPatient():
    """
    Helper class used to normalize the strings by
    removing punctuation and transforming to lowercase.

    .. seealso::

        Called by :meth:`utils.prepare_for_hashing`
    """

    log = None

    @classmethod
    def configure_logger(cls, logger):
        cls.log = logger

    def __init__(self,  *args, **kwargs):
        self.patid = kwargs.get('patid')

        self.pat_first_name = utils.prepare_for_hashing(
            kwargs.get('pat_first_name')
        )
        self.pat_last_name = utils.prepare_for_hashing(
            kwargs.get('pat_last_name')
        )
        self.pat_birth_date = utils.format_date_as_string(
            kwargs.get('pat_birth_date'), utils.FORMAT_DATABASE_DATE
        )
        self.pat_sex = utils.prepare_for_hashing(
            kwargs.get('pat_sex')
        )
        self.pat_race = utils.prepare_for_hashing(
            kwargs.get('pat_race')
        )

    def has_all_data(self, required_attributes):
        """
        :return bool: `True` if all `required_attributes` have a
        non-empty value
        """
        # TODO: should we check for minimum length of each string?
        for attr in required_attributes:
            if not getattr(self, attr, None):
                NormalizedPatient.log.warning(
                    "--> Missing value for attr [{}]".format(attr))
                return False
        return True

    def __repr__(self):
        return "NormalizedPatient " \
            "<patid: {0.patid}, " \
            "pat_first_name: {0.pat_first_name}, " \
            "pat_last_name: {0.pat_last_name}, " \
            "pat_birth_date: {0.pat_birth_date}, " \
            "pat_sex: {0.pat_sex}, " \
            "pat_race: {0.pat_race}>".format(self)
