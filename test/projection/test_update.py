
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class TestUpdate(unittest.TestCase):

  def test_update(self):
    """ update will validate and recursively merge argument projection with 
    __dict__ and return result
    """

    c = pymongo_basemodel.core.Projection({
      "key1": 1
    })

    projection = {
      "key2": 1
    }

    value = c.update(projection)

    self.assertEqual(value, {
      "key1": 1,
      "key2": 1
    })

    self.assertEqual(c.__dict__, {
      "key1": 1,
      "key2": 1
    })

  def test_update_raise_exception(self):
    """ update will validate argument projection and raise exception if invalid
    """

    c = pymongo_basemodel.core.Projection({ "key1": 1 })

    with self.assertRaises(pymongo_basemodel.exceptions.ProjectionMalformed):
      c.merge({ "key2": "something" })

    with self.assertRaises(pymongo_basemodel.exceptions.ProjectionTypeMismatch):
      c.merge({ "key2": 0 })


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestUpdate)
  unittest.TextTestRunner().run(suite)
  