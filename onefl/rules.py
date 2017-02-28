"""
Goal: Store the rules by which we pick the elements of patient data before
    computing the hashed string.

Authors:
     Andrei Sura <sura.andrei@gmail.com>
"""

# TODO: research the claim from
# L. Sweeney. k-anonymity: a model for protecting privacy.
# International Journal on Uncertainty, Fuzziness and Knowledge-based Systems
#
# "...87% (216 million of 248 million) of the population in the
#   United States had reported characteristics that likely made them
#   unique based only on {5-digit ZIP, sex, date of birth}."

from onefl import utils  # noqa
from onefl.normalized_patient import NormalizedPatient  # noqa


# Last Name + First Name + DOB + Race
RULE_CODE_F_L_D_R = 'F_L_D_R'

# First Name + Last Name + DOB + Sex
RULE_CODE_F_L_D_S = 'F_L_D_S'

# For patients without hashes
RULE_CODE_NO_HASH = 'NO_HASH'


# In order to guarantee correctness we will allow the partners
# to add to the configuration only values from the map below.
# If we add new rules then we will ask the partners to download a new version
# of the client software.
AVAILABLE_RULES_MAP = {

    RULE_CODE_F_L_D_S: {
        'required_attr': ['pat_first_name', 'pat_last_name', 'pat_birth_date', 'pat_sex'],  # NOQA
        'pattern': '{0.pat_first_name}{0.pat_last_name}{0.pat_birth_date}{0.pat_sex}',  # NOQA
    },
    RULE_CODE_F_L_D_R: {
        'required_attr': ['pat_first_name', 'pat_last_name', 'pat_birth_date', 'pat_race'],  # NOQA
        'pattern': '{0.pat_last_name}{0.pat_first_name}{0.pat_birth_date}{0.pat_race}',  # NOQA
    },
}
