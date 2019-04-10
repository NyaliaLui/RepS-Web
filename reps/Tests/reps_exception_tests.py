import unittest
import os
from .. import RepsError

class RepsErrorTestCase(unittest.TestCase):
    def test_raise(self):
        try:
            raise RepsError(['foo.zip', 'bar.rar'])
        except RepsError as ex:
           self.assertTrue(ex.names == ['foo.zip', 'bar.rar'])

    def test_print_as_string(self):
        try:
            raise RepsError(['foo.zip', 'bar.rar'])
        except RepsError as ex:
            s = str(ex)
            self.assertTrue(s == '[\'foo.zip\', \'bar.rar\']')
