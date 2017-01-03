
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_add(self):
    """add() will add a model to collection.collection
    """

    model = pymongo_basemodel.core.Model()
    collection = pymongo_basemodel.core.Collection()
    collection.add(model)
    self.assertIn(model, collection.collection)

  def test_add_raise_exception(self):
    """add() will raise exception CollectionModelClassMismatch if add() called 
    with model that is of different type than colleciton.model
    """

    class MismatchModel(pymongo_basemodel.core.Model):
      pass

    mismatch_model = MismatchModel()
    collection = pymongo_basemodel.core.Collection()

    with self.assertRaises(pymongo_basemodel.exceptions.CollectionModelClassMismatch):
      collection.add(mismatch_model)

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)