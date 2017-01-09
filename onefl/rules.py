"""
Goal: Store logic related to hashing data according to
predefined rules.

Authors:
     Andrei Sura <sura.andrei@gmail.com>
"""

# TODO: research the claim from
# L. Sweeney. k-anonymity: a model for protecting privacy.
# International Journal on Uncertainty, Fuzziness and Knowledge-based Systems
#
# "...87% (216 million of 248 million) of the population in the
#   United States had reported characteristics that likely made them
#   unique based only on {5-digit ZIP, gender, date of birth}."

from onefl import utils
from onefl import NormalizedPatient


# _1 First Name + Last Name + DOB + Gender
RULE_CODE_F_L_D_G = 'F_L_D_G'

# _2 Last Name + First Name + DOB + Race
RULE_CODE_F_L_D_R = 'F_L_D_R'


# In order to guarantee correctness we will allow the partners
# to add to the configuration only values from the map below.
# If we add new rules then we will ask the partners to download a new version
# of the client software.
AVAILABLE_RULES_MAP = {

    RULE_CODE_F_L_D_G: {
        'required_attr': ['pat_first_name', 'pat_last_name', 'pat_birth_date', 'pat_gender'],  # NOQA
        'pattern': '{0.pat_first_name}{0.pat_last_name}{0.pat_birth_date}{0.pat_gender}',  # NOQA
    },
    RULE_CODE_F_L_D_R: {
        'required_attr': ['pat_first_name', 'pat_last_name', 'pat_birth_date', 'pat_race'],  # NOQA
        'pattern': '{0.pat_last_name}{0.pat_first_name}{0.pat_birth_date}{0.pat_racep}',  # NOQA
    },
}


class Rules():
    log = None

    @classmethod
    def configure_logger(cls, logger):
        cls.log = logger

    @classmethod
    def get_hashes(cls, patient, hashing_rules, salt):
        """
        Get a dictionary of unhexlified hashes for a patient.
        The number of entries in the dictionary depends on the
        "number of rules that can be applied" to a specific patient

        :param hashing_rules: a list of hashing rules codes
        :rtype dict

        .. seealso::

            Called by :meth:`...`

        """
        hashes = {}
        count = 0

        for rule in hashing_rules:
            rule_data = AVAILABLE_RULES_MAP.get(rule)
            pattern = rule_data['pattern']
            required_attr = rule_data['required_attr']

            if not patient.has_all_data(required_attr):
                cls.log.debug("Skip hashing patient [{}] due to missing data"
                              "for rule [{}]".format(patient.id, rule))
                continue
            raw = pattern.format(patient) + salt
            chunk = utils.apply_sha256(raw)
            cls.log.debug("Rule {} raw data: {}, hashed: {}"
                          .format(rule, raw, chunk))
            hashes[str(count)] = chunk
            count = count + 1

        return hashes

    @classmethod
    def prepare_patients(cls, patients, hashing_rules, salt):
        """
        Calculate hashes for patients.

        :param patients: a list of patients for which we need
                        to retrieve `linkage_uuid` from OLASS server
        :rtype tuple(dict, dict)
        :return two data dictionaries:
            - lut_patient_id structure:
                {0 => pat_id, 1 => pat_id...}
            - lut_patient_hashes structure:
                {0 => {'0' => 'sha_rule_1', '1' => 'sha_rule_2', ...},
                {1 => {'0' => 'sha_rule_1', '1' => 'sha_rule_2', ...},
                ...
                }

        .. seealso::

            Called by :meth:`...`

        """
        lut_patient_hashes = {}
        lut_patient_id = {}

        for count, patient in enumerate(patients):
            norm_patient = NormalizedPatient(patient)
            pat_hashes = cls.get_hashes(norm_patient, hashing_rules, salt)
            lut_patient_hashes[str(count)] = pat_hashes
            lut_patient_id[str(count)] = patient.id
            cls.log.debug("Hashing: {} \n{}".format(norm_patient, pat_hashes))

        return lut_patient_id, lut_patient_hashes
