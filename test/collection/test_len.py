
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_add(self):
    """ len(collection) will return the len of collection.collection
    """

    a = pymongo_basemodel.core.Collection()

    self.assertEqual(len(a), 0)

    a.collection.append(pymongo_basemodel.core.Model())

    self.assertEqual(len(a), 1)

    a.collection.append(pymongo_basemodel.core.Model())

    self.assertEqual(len(a), 2)

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)