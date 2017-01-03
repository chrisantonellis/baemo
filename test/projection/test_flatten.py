
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class TestFlatten(unittest.TestCase):

  def test_flatten_projection(self):
    """ flatten_projection will validate and reduce projection to values 
    usable by pymongo and mongodb
    """

    c = pymongo_basemodel.core.Projection()

    projection_1 = {
      "key1": 1,
      "key2": 2,
      "key3": {
        "key4": 1,
        "key5": 2
      }
    }

    self.assertEqual(c.flatten_projection(projection_1), {
      "key1": 1,
      "key2": 1,
      "key3": 1
    })

    projection_2 = {
      "key1": 0,
      "key2": {
        "key3": 0
      },
      "key4": 2
    }

    self.assertEqual(c.flatten_projection(projection_2), {
      "key1": 0
    })

  def test_flatten_projection_raise_exception(self):
    """ flatten_projection will validate argument projection and raise 
    exception if invalid
    """

    c = pymongo_basemodel.core.Projection()

    with self.assertRaises(pymongo_basemodel.exceptions.ProjectionMalformed):
      c.flatten_projection({ "key": "something" })

    with self.assertRaises(pymongo_basemodel.exceptions.ProjectionTypeMismatch):
      c.flatten_projection({
        "key1": 1,
        "key2": 0
      })

  def test_flatten(self):
    """ flatten will reduce __dict__ projection to values usable by pymongo and 
    mongodb
    """

    c = pymongo_basemodel.core.Projection({
      "key1": 1,
      "key2": 2,
      "key3": {
        "key4": 1,
        "key5": 2
      }
    })

    self.assertEqual(c.flatten(), {
      "key1": 1,
      "key2": 1,
      "key3": 1
    })


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestFlatten)
  unittest.TextTestRunner().run(suite)
  