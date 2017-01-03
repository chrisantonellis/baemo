
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel
import bson


class Test(unittest.TestCase):

  def test_get_ids(self):
    """ get_ids() returns a list of the value of id_attribute for models in 
    collection.collection
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
    self.assertEqual(type(collection.get_ids()), list)

    # assert that values returned are ObjectIds
    for value in collection.get_ids():
      self.assertEqual(type(value), bson.objectid.ObjectId)

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)