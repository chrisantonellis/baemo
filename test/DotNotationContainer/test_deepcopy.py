
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel

import copy


class Test(unittest.TestCase):

  def test_deepcopy(self):
    """ deepcopy returns a deep copy of a model
    """

    # create model
    a1 = pymongo_basemodel.core.DotNotationContainer()

    # manually set attributes
    a1({
      "key1": "value",
      "key2": {
        "key3": "value"
      }
    })

    # make deep copy
    a2 = copy.deepcopy(a1)

    # assert two instances are different
    self.assertIsNot(a1, a2)

    # assert two instances have the same attributes
    self.assertEqual(a1, a2)

    # assert two instances attributes are a deep copy
    a1.set("key2.key3", "new_value")
    self.assertNotEqual(a1, a2)

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
