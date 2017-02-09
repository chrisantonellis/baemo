
import unittest

from pymongo_basemodel.model import Undefined


class TestUndefined(unittest.TestCase):

    def test_str(self):
        first_name = Undefined()
        last_name = "Somebody"
        full_name = "{} {}".format(first_name, last_name)
        self.assertEqual(full_name, "undefined Somebody")

    def test_bool(self):
        u = Undefined()
        self.assertEqual(bool(u), False)
