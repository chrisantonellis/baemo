
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel

import copy


class TestDeepCopy(unittest.TestCase):

  def test_deepcopy(self):
    """__deepcopy__ returns a deep copy of a model
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

    # make deep copy
    model_2 = copy.deepcopy(model_1)

    # assert two instances are different
    self.assertIsNot(model_1, model_2)

    # assert two instances have the same attributes
    self.assertEqual(model_1.attributes, model_2.attributes)

    # assert two instances attributes are a deep copy
    model_1.attributes["key2"]["key3"] = "new_value"
    self.assertNotEqual(model_1.attributes, model_2.attributes)

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestDeepCopy)
  unittest.TextTestRunner().run(suite)
