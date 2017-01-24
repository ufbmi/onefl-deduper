"""
Goal: implement tests for `LinkGenerator` class

@authors:
    Andrei Sura <sura.andrei@gmail.com>
"""
# flake8: noqa
import os
import unittest
import pandas.util.testing as tm  # noqa
from base_test import BaseTestCase
from onefl.config import Config
from onefl import logutils
from onefl import utils
from onefl.utils.ui import check_file_exists
from onefl.link_generator import LinkGenerator

DELIMITER = '\t'
logger = logutils.get_a_logger(__file__)

SETTINGS_FILE = 'config/test_settings_linker.py'


# class TestLinkGenerator(unittest.TestCase):
class TestLinkGenerator(BaseTestCase):

    def setUp(self):
        super(TestLinkGenerator, self).setUp()
        LinkGenerator.configure_logger(logger)

    def tearDown(self):
        pass

    def test_linker(self):
        """ Verify that we produce hashes properly """
        inputdir = 'tests/data_in'
        outputdir = 'tests/data_out'
        config = Config(root_path='.', defaults={})
        config.from_pyfile(SETTINGS_FILE)
        result = LinkGenerator.generate(config, inputdir, outputdir,
                                        partner='UFH')
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

        # tm.assert_frame_equal(df_expected, df_actual)
        uuids_actual = set()
        uuids_expected = set()
        uuids_actual.update(df_actual['UUID'].tolist())
        uuids_expected.update(df_expected['UUID'].tolist())

        # compare the numbers of distinct UUIDs
        self.assertEqual(len(uuids_actual), len(uuids_expected))


if __name__ == '__main__':
    unittest.main()
