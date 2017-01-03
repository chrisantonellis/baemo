
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class TestGetType(unittest.TestCase):

  def test_get_projection_type(self):
    """ get_type will validate the argument projection and return the type
    """

    c = pymongo_basemodel.core.Projection()

    projection_1 = {
      "key": 1
    }

    self.assertEqual(c.get_projection_type(projection_1), "inclusive")

    projection_2 = {
      "key1": 1,
      "key2": {
        "key3": 1,
        "key4": 2
      },
      "key6": -1
    }

    self.assertEqual(c.get_projection_type(projection_2), "inclusive")

    projection_3 = { "key": 0 }

    self.assertEqual(c.get_projection_type(projection_3), "exclusive")

    projection_4 = {
      "key1": 0,
      "key2": {
        "key3": 0,
        "key4": 2
      },
      "key6": -1
    }

    self.assertEqual(c.get_projection_type(projection_4), "exclusive")

    projection_5 = { "key": 2 }

    self.assertEqual(c.get_projection_type(projection_5), None)

    projection_6 = {
      "key1": 2,
      "key2": {
        "key3": 2
      },
      "key6": -1
    }

    self.assertEqual(c.get_projection_type(projection_6), None)

  def test_get_type_raise_exception(self):
    """ get_type will validate the argument projection and raise exception if 
    invalid
    """

    c = pymongo_basemodel.core.Projection()

    projection_1 = { "key": "something" }

    with self.assertRaises(pymongo_basemodel.exceptions.ProjectionMalformed):
      c.get_projection_type(projection_1)

    projection_2 = {
      "key1": 1,
      "key2": 0
    }

    with self.assertRaises(pymongo_basemodel.exceptions.ProjectionTypeMismatch):
      c.get_projection_type(projection_2)

    projection_3 = {
      "key1": 1,
      "key2": {
        "key3": 2,
        "key4": {
          "key5": 0
        }
      }
    }

    with self.assertRaises(pymongo_basemodel.exceptions.ProjectionTypeMismatch):
      c.get_projection_type(projection_3)

  def test_get_type(self):
    """ get_type will run get_projection_type on __dict__ and return the result
    """

    c = pymongo_basemodel.core.Projection({ "key": 1 })

    self.assertEqual(c.get_type(), "inclusive")

    c({ "key": 0 })

    self.assertEqual(c.get_type(), "exclusive")

    c({ "key": 2 })

    self.assertEqual(c.get_type(), None)


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestGetType)
  unittest.TextTestRunner().run(suite)
  