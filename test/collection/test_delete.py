
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_delete(self):
    """delete() calls model.delete() and passes args and kwargs forward for all 
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

    # assert delete not set on models yet
    for model in collection.collection:
      self.assertEqual(model._delete, False)

    # call delete on collection
    collection.delete()

    # assert delete set on models
    for model in collection.collection:
      self.assertEqual(model._delete, True)

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)