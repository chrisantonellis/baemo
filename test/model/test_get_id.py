
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel

import bson


class Test(unittest.TestCase):

  def test_get_id(self):
    """get_id returns the value of the models id_attribute or None
    """

    a = pymongo_basemodel.core.Model()

    self.assertEqual(a.get_id(), None)

    a.target({ "_id": bson.objectid.ObjectId() })

    self.assertIsInstance(a.get_id(), bson.objectid.ObjectId)


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
