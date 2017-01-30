"""
Goal: implement tests for `HashGenerator` class

@authors:
    Andrei Sura <sura.andrei@gmail.com>
"""
import os
import unittest
import pandas.util.testing as tm
# from mock import patch
# from io import StringIO
from onefl.config import Config
from onefl import logutils
from onefl import utils
from onefl.utils.ui import check_file_exists
from onefl.hash_generator import HashGenerator
from onefl.normalized_patient import NormalizedPatient

# patch it
# sys.exit = lambda *x: None

DELIMITER = '\t'
logger = logutils.get_a_logger(__file__)

SETTINGS_FILE = 'config/test_settings_hasher.py'


class TestHashGenerator(unittest.TestCase):

    def setUp(self):
        super(TestHashGenerator, self).setUp()
        HashGenerator.configure_logger(logger)
        NormalizedPatient.configure_logger(logger)

    def tearDown(self):
        pass

    # @unittest.skip
    def test_hasher(self):
        """ Verify that we produce hashes properly """
        inputdir = 'tests/data_in'
        outputdir = 'tests/data_out'
        config = Config(root_path='.', defaults={})
        config.from_pyfile(SETTINGS_FILE)
        result = HashGenerator.generate(config, inputdir, outputdir)
        self.assertTrue(result)

        # Check if the reference file exists
        file_name = os.path.join('tests/data_in', 'phi_hashes.csv')
        exists = check_file_exists(ask=False, file_name=file_name)
        self.assertTrue(exists)

        # read the reference frame
        df_expected = utils.frame_from_file(file_name, delimiter=DELIMITER)

#         file = StringIO(u"""
# patid| sha_rule_1| sha_rule_2
# 01 | 1 | 1
# 02 | 1 | 1
# 03 | 2 | 1
# 04 | 2 | 1
# """)
#         df_expected = pd.read_csv(file, sep='|',
#                                   dtype=object,
#                                   skipinitialspace=True,
#                                   skip_blank_lines=True)

        # read the frame produced by calling `generate()`
        df_actual = utils.frame_from_file(
            os.path.join('tests/data_out', 'phi_hashes.csv'),
            delimiter=DELIMITER)

        tm.assert_frame_equal(df_expected, df_actual)


if __name__ == '__main__':
    unittest.main()
