# coding: utf-8
import sys; sys.path.append("../")

import unittest

from pymongo_basemodel.undefined import Undefined


class TestUndefined(unittest.TestCase):

    def test_str(self):
        first_name = Undefined()
        last_name = "Somebody"
        full_name = "{} {}".format(first_name, last_name)
        self.assertEqual(full_name, "undefined Somebody")

    def test_bool(self):
        u = Undefined()
        self.assertEqual(bool(u), False)

if __name__ == "__main__":
    unittest.main()
