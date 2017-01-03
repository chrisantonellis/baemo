
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_unset(self):
    """unset() calls model.unset() and passes args and kwargs forward for all 
    models in collection.collection
    """

    # create model
    model1 = pymongo_basemodel.core.Model()
    model1.set("key", "value")

    # create another model
    model2 = pymongo_basemodel.core.Model()
    model2.set("key", "value")

    # create collection
    collection = pymongo_basemodel.core.Collection()

    # set models on collection
    collection.add(model1)
    collection.add(model2)

    # set on collection
    collection.unset("key")

    # assert values 
    self.assertEqual(collection.get(), [{},{}])

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)