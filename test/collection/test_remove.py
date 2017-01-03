
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_remove(self):
    """remove() will remove a model from collection.collection by reference
    """

    model = pymongo_basemodel.core.Model()
    collection = pymongo_basemodel.core.Collection()
    collection.add(model)
    collection.remove(model)

    self.assertNotIn(model, collection.collection)

  def test_remove_raise_exception(self):
    """remove() will raise an exception with trying to remove a model from 
    collection.collection if the model is not present
    """

    model = pymongo_basemodel.core.Model()
    collection = pymongo_basemodel.core.Collection()

    with self.assertRaises(pymongo_basemodel.exceptions.CollectionModelNotPresent):
      collection.remove(model)

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)