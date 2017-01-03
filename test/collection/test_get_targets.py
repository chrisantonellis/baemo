
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel
import bson


class Test(unittest.TestCase):

  def test_get_targets(self):
    """ get_targets() calls model.get_target() on all models in self.collection 
    and returns values as a list
    """ 

    # create model
    a = pymongo_basemodel.core.Model()
    a.set_target(bson.objectid.ObjectId())

    # create another model
    b = pymongo_basemodel.core.Model()
    b.set_target(bson.objectid.ObjectId())

    # create collection
    collection = pymongo_basemodel.core.Collection()

    # add models to collection
    collection.add(a)
    collection.add(b)

    # assert collection.get() returns a list
    self.assertEqual(type(collection.get_targets()), list)

    # assert that values returned are ObjectIds
    for value in collection.get_targets():
      self.assertEqual(type(value), dict)

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)