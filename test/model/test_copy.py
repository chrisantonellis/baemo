
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel

import copy


class Test(unittest.TestCase):

  def test_copy(self):
    """__copy__ returns a shallow copy of a model
    """

    # create model
    model_1 = pymongo_basemodel.core.Model()

    # manually set attributes
    model_1.attributes = {
      "key1": "value",
      "key2": {
        "key3": "value"
      }
    }

    # make shallow copy
    model_2 = copy.copy(model_1)

    # assert two instances are different
    self.assertIsNot(model_1, model_2)

    # assert two instances have the same attributes
    self.assertEqual(model_1.attributes, model_2.attributes)

    # assert two instances attributes are a shallow copy
    model_1.attributes["key2"]["key3"] = "new_value"
    self.assertEqual(model_1.attributes, model_2.attributes)

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
