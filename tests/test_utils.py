
import unittest
# from mock import patch
from onefl import utils


class TestUtils(unittest.TestCase):

    def test_prepare_for_hashing(self):
        """ Verify that punctuation characters are removed """
        subjects = {
            '1': {'in': 'AbC xyZă', 'out': 'abcxyză'},
            '2': {'in': 'A&B,C.D:E;F-G}H{I@#J!', 'out': 'abcdefghij'},
            '3': {'in': 'ABC!"#$%&\'()*+,-./:;=>?@[\\]^_`{|}~ \t\n\r\x0b\x0c', 'out': 'abc'},  # NOQA
        }

        for case, data in subjects.items():
            self.assertEqual(data.get('out'),
                             utils.prepare_for_hashing(data.get('in')))
