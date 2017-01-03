
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_set(self):
    """set() calls model.set() and passes args and kwargs forward for all 
    models in collection.collection
    """

    # create model
    model1 = pymongo_basemodel.core.Model()

    # create another model
    model2 = pymongo_basemodel.core.Model()

    # create collection
    collection = pymongo_basemodel.core.Collection()

    # set models on collection
    collection.add(model1)
    collection.add(model2)

    # set on collection
    collection.set("key", "value")

    # assert values 
    self.assertEqual(collection.get(), [
      {
        "key": "value"
      },{
        "key": "value"
      }
    ])

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)