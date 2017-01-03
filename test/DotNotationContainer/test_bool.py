
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class TestBool(unittest.TestCase):

  def test_bool(self):
    """ when DotNotationContainer is cast to a bool, it will return true if 
    there is any data in __dict__ and False if not
    """

    c1 = pymongo_basemodel.core.DotNotationContainer()
    self.assertEqual(bool(c1), False)

    c2 = pymongo_basemodel.core.DotNotationContainer({ "key": "value" })
    self.assertEqual(bool(c2), True)


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestBool)
  unittest.TextTestRunner().run(suite)
