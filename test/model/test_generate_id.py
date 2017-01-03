
import sys
sys.path.extend([ "../", "../../" ])

import bson
import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_generate_id(self):
    """ generate_id returns a new ObjectId
    """

    a = pymongo_basemodel.core.Model()

    self.assertEqual(
      type(a.generate_id()),
      bson.objectid.ObjectId
    )


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
  