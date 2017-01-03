
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel

import copy


class Test(unittest.TestCase):

  def test_copy(self):
    """ copy returns a shallow copy of a model
    """

    # create model
    a = pymongo_basemodel.core.DotNotationContainer()

    # manually set attributes
    a({
      "key1": "value",
      "key2": {
        "key3": "value"
      }
    })

    # make shallow copy
    a2 = copy.copy(a)

    # assert two instances are different
    self.assertIsNot(a, a2)

    # assert two instances have the same attributes
    self.assertEqual(a, a2)

    # assert two instances attributes are a shallow copy
    a.set("key2.key3", "value")
    self.assertEqual(a, a2)

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
