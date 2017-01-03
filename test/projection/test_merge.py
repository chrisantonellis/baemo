
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class TestMerge(unittest.TestCase):

  def test_merge_projections(self):
    """ merge_projections will recursively merge projection dicts where first 
    projection overwrites second projection and return result
    """

    c = pymongo_basemodel.core.Projection()

    projection_1 = {
      "key1": 1,
      "key2": {
        "key3": 1
      }
    }

    projection_2 = {
      "key2": {
        "key4": 1
      }
    }

    self.assertEqual(c.merge_projections(projection_1, projection_2), {
      "key1": 1,
      "key2": {
        "key3": 1,
        "key4": 1
      }
    })

  def test_merge_projection_remove_key(self):
    """ merge_projections will unset a key from a projection while merging if
    the value '-1' is found
    """

    c = pymongo_basemodel.core.Projection()

    projection_1 = {
      "key1": 1,
      "key2": {
        "key3": 1
      },
      "key5": -1
    }

    projection_2 = {
      "key2": {
        "key4": 1
      },
      "key5": 1
    }

    self.assertEqual(c.merge_projections(projection_1, projection_2), {
      "key1": 1,
      "key2": {
        "key3": 1,
        "key4": 1
      }
    })

  def test_merge(self):
    """ merge will validate projection, merge with __dict__ projection and 
    return result without changing __dict__
    """

    c = pymongo_basemodel.core.Projection({ "key1": 1 })

    value = c.merge({ "key2": 1 })

    self.assertEqual(value, {
      "key1": 1,
      "key2": 1
    })


  def test_merge_raise_exception(self):
    """ merge will validate argument projection and raise exception if invalid
    """

    c = pymongo_basemodel.core.Projection({ "key1": 1 })

    projection_1 = {
      "key2": "something"
    }

    with self.assertRaises(pymongo_basemodel.exceptions.ProjectionMalformed):
      c.merge(projection_1)

    projection_2 = {
      "key2": 0
    }

    with self.assertRaises(pymongo_basemodel.exceptions.ProjectionTypeMismatch):
      c.merge(projection_2)


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestMerge)
  unittest.TextTestRunner().run(suite)
  