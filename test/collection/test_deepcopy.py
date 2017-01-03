
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel

import copy


class Test(unittest.TestCase):

  def test_deepcopy(self):
    """__deepcopy__ returns a deep copy of a model
    """

    # create model
    a = pymongo_basemodel.core.Collection()
    a.collection.append(pymongo_basemodel.core.Model())

    b = copy.deepcopy(a)

    self.assertIsNot(a, b)
    self.assertNotEqual(a.collection, b.collection)

    b.collection.append(pymongo_basemodel.core.Model())
    
    self.assertNotEqual(a.collection, b.collection)

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
