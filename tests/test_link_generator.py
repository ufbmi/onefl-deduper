"""
Goal: implement tests for `LinkGenerator` class

@authors:
    Andrei Sura <sura.andrei@gmail.com>
"""
# flake8: noqa
import os
import unittest
import pandas.util.testing as tm
from onefl.config import Config
from onefl import logutils
from onefl import utils
from onefl.utils.ui import check_file_exists
from onefl.link_generator import LinkGenerator

DELIMITER = '\t'
logger = logutils.get_a_logger(__file__)

SETTINGS_FILE = 'config/test_settings_linker.py'


class TestHashGenerator(unittest.TestCase):

    def setUp(self):
        super(TestHashGenerator, self).setUp()
        LinkGenerator.configure_logger(logger)

    def tearDown(self):
        pass

    def test_generate(self):
        """ Verify that we produce hashes properly """
        inputdir = 'tests/data_in'
        outputdir = 'tests/data_out'
        config = Config(root_path='.', defaults={})
        config.from_pyfile(SETTINGS_FILE)
        result = LinkGenerator.generate(config, inputdir, outputdir)
        self.assertTrue(result)

        # Check if the reference file exists
        file_name = os.path.join('tests/data_in', 'links.csv')
        exists = check_file_exists(ask=False, file_name=file_name)
        self.assertTrue(exists)

        # read the reference frame
        df_expected = utils.frame_from_file(file_name, delimiter=DELIMITER)

        # read the frame produced by calling `generate()`
        df_actual = utils.frame_from_file(
            os.path.join('tests/data_out', 'links.csv'),
            delimiter=DELIMITER)

        tm.assert_frame_equal(df_expected, df_actual)


if __name__ == '__main__':
    unittest.main()
