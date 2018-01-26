"""
Goal: store application settings
"""

# Configure this dictionary with the prefered column names
# Example:
#   'patid': 'patid_column_name_from_the_actual_file'
COLUMN_MAP = {
    'patid': 'patid',
    'first': 'first',
    'last': 'last',
    'dob': 'dob',
    'race': 'race',
    'sex': 'sex',
}

IN_DELIMITER = ','
OUT_DELIMITER = ','

IN_FILE = 'phi.csv'
OUT_FILE = 'phi_hashes.csv'

# How many lines to parse at once
LINES_PER_CHUNK = 2000

# TODO: check if we need a secret salt that only partners know
# This would mean that we need to let partners
# exchange this string without ever leaking it to us
SALT = ''

# List rules for computing hashes
ENABLED_RULES = ['F_L_D_R', 'F_L_D_S']
