
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel

import copy


class Test(unittest.TestCase):

  def test_copy(self):
    """__copy__ returns a shallow copy of a model
    """

    # create model
    a = pymongo_basemodel.core.Collection()
    a.collection.append(pymongo_basemodel.core.Model())

    b = copy.copy(a)

    # assert two instances are different
    self.assertIsNot(a, b)

    # assert two instances have the same attributes
    self.assertEqual(a.collection, b.collection)

    # assert two instances attributes are a shallow copy
    b.collection.append(pymongo_basemodel.core.Model())
    self.assertEqual(a.collection, b.collection)

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
