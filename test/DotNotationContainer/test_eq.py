
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_eq(self):
    """ eq returns true if dicts of two instances being compared are equal 
    and false if not
    """

    # create model
    a = pymongo_basemodel.core.DotNotationContainer()

    # manually set attributes
    a({ "key": "value" })

    # make shallow copy
    b = pymongo_basemodel.core.DotNotationContainer()

    # manually set attributes
    b({ "key": "value" })

    self.assertEqual(a, b)
    self.assertEqual(bool(a == b), True)

    # manually set attributes
    b({ "key": "something" })

    self.assertNotEqual(a, b)
    self.assertEqual(bool(a == b), False)

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
