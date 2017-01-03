
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class TestBool(unittest.TestCase):

  def test_bool(self):
    """ __bool__ called on Undefined will return False
    """

    c = pymongo_basemodel.core.Undefined()
    self.assertEqual(bool(c), False)


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestBool)
  unittest.TextTestRunner().run(suite)
