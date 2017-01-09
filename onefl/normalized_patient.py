"""
Goal: Implement a helper class used for cleaning patient data
    elements before hashing (to increase the chance of a match)

Authors:
     Andrei Sura <sura.andrei@gmail.com>
"""
from onefl import utils


class NormalizedPatient():
    log = None

    @classmethod
    def configure_logger(cls, logger):
        cls.log = logger

    """
    Helper class used to normalize the strings by
    removing punctuation and transforming to lowercase.

    .. seealso::

        Called by :meth:`utils.prepare_for_hashing`
    """
    def __init__(self, pat):
        self.id = pat.id

        self.pat_gender = utils.prepare_for_hashing(
            pat.pat_gender
        )
        self.pat_birth_date = utils.format_date_as_string(
            pat.pat_birth_date, utils.FORMAT_DATABASE_DATE
        )
        self.pat_first_name = utils.prepare_for_hashing(
            pat.pat_first_name
        )
        self.pat_last_name = utils.prepare_for_hashing(
            pat.pat_last_name
        )
        self.pat_race = utils.prepare_for_hashing(
            pat.pat_race
        )

    def has_all_data(self, required_attributes):
        """
        :return bool: `True` if all `required_attributes` have a
        non-empty value
        """
        # TODO: should we check for minimum length of each string?
        for attr in required_attributes:
            if not getattr(self, attr, None):
                self.log.debug("--> Missing value for attr [{}]".format(attr))
                return False
        return True

    def __repr__(self):
        return "NormalizedPatient " \
            "<pat_gender: {0.pat_gender}, " \
            "pat_birth_date: {0.pat_birth_date}, " \
            "pat_first_name: {0.pat_first_name}, " \
            "pat_last_name: {0.pat_last_name}, " \
            "pat_race: {0.pat_race}>".format(self)
