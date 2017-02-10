
from collections import OrderedDict

IN_DELIMITER = '\t'
OUT_DELIMITER = '\t'

IN_FILE = 'phi_hashes.csv'
OUT_FILE = 'links.csv'
SAVE_OUT_FILE = True

# How many lines to parse at once
LINES_PER_CHUNK = 2000

# List rules for computing hashes
ENABLED_RULES = OrderedDict(
    [('1', 'F_L_D_R'),
     ('2', 'F_L_D_S')])

# List column names for the input file
EXPECTED_COLS = ['PATID']
EXPECTED_COLS.extend(ENABLED_RULES.values())

# =============== Database Settings
DB_TYPE = 'TEST'
