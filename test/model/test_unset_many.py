
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_unset_many(self):
    """ unset removes an attribute from a model. the first positional argument 
    is the model attribute if it is a string
    """

    # create model
    model = pymongo_basemodel.core.Model()

    # set data on model
    model.set({
      "key1": "value",
      "key2": "value",
      "key3": "value"
    })

    # unset attribute on model
    model.unset_many([ "key1", "key2" ])

    # assert that attribute was unset
    self.assertEqual(model.get(), {
      "key3": "value"
    })

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)