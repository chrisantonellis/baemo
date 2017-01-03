
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class TestSet(unittest.TestCase):

  def test_set(self):
    """ set will set key, validate data, and if data is valid set data in
     __dict__ 
    """

    c = pymongo_basemodel.core.Projection()

    c.set("key1", 1)

    self.assertEqual(c.__dict__, { "key1": 1 })

    c.set("key2", 1)

    self.assertEqual(c.__dict__, {
      "key1": 1,
      "key2": 1
    })

    c.set("key3.key4.key5", 1)

    self.assertEqual(c.__dict__, {
      "key1": 1,
      "key2": 1,
      "key3": {
        "key4": {
          "key5": 1
        }
      }
    })

  def test_set_raise_exception(self):
    """ set will raise exception if setting a value would make the projection 
    invalid, and __data__ will not be changed
    """

    c = pymongo_basemodel.core.Projection()

    c.set("key1", 1)

    self.assertEqual(c.__dict__, { "key1": 1 })

    with self.assertRaises(pymongo_basemodel.exceptions.ProjectionMalformed):
      c.set("key2", "something")

    self.assertEqual(c.__dict__, { "key1": 1 })

    with self.assertRaises(pymongo_basemodel.exceptions.ProjectionTypeMismatch):
      c.set("key2", 0)

    self.assertEqual(c.__dict__, { "key1": 1 })


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestSet)
  unittest.TextTestRunner().run(suite)
  