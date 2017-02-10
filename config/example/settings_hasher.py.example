"""
Goal: store application settings
"""

# TODO: check if we need to allow flexible column naming
EXPECTED_COLS = ['patid', 'first', 'last', 'dob', 'race', 'sex']

IN_DELIMITER = '\t'
OUT_DELIMITER = '\t'

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
