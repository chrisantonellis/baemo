
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_reset(self):
    """delete() calls model.delete() and passes args and kwargs forward for all 
    models in collection.collection
    """

    # create model
    a = pymongo_basemodel.core.Model()
    a.set("key", "value")

    # create collection
    b = pymongo_basemodel.core.Collection()

    # set model on collection
    b.add(a)
    b.reset()

    self.assertEqual(b.target, {})
    self.assertEqual(b.collection, [])

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)