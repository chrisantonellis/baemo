
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_unset_many(self):
    """unset() calls model.unset() and passes args and kwargs forward for all 
    models in collection.collection
    """

    # create model
    model1 = pymongo_basemodel.core.Model()
    model1.set("key1", "value")
    model1.set("key2", "value")
    model1.set("key3", "value")

    # create another model
    model2 = pymongo_basemodel.core.Model()
    model2.set("key1", "value")
    model2.set("key2", "value")
    model2.set("key3", "value")

    # create collection
    collection = pymongo_basemodel.core.Collection()

    # set models on collection
    collection.add(model1)
    collection.add(model2)

    # set on collection
    collection.unset_many([ "key1", "key2" ])

    # assert values 
    self.assertEqual(collection.get(), [{
      "key3": "value"
    },{
      "key3": "value"
    }]  )

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)