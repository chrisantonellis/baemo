
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class TestInit(unittest.TestCase):

  def test_init(self):
    """ __init__ returns a reference to an instantiated Projection
    """

    c = pymongo_basemodel.core.Projection()
    self.assertIsInstance(c, pymongo_basemodel.core.Projection)

  def test_init_with_data(self):
    """ __init__ returns a reference to an instantiated Projection 
    with data argument validated and set to __dict__ if set
    """

    c = pymongo_basemodel.core.Projection({ "key": 0 })
    self.assertEqual(c.__dict__, { "key": 0 })

  def test_init_raise_exception(self):
    """ __init__ will raise an exception if passed an invalid projection on 
    Projection instantiation
    """

    with self.assertRaises(pymongo_basemodel.exceptions.ProjectionMalformed):
      pymongo_basemodel.core.Projection({ "key": "something" })

    with self.assertRaises(pymongo_basemodel.exceptions.ProjectionTypeMismatch):
      pymongo_basemodel.core.Projection({
        "key1": 0,
        "key2": 1
      })


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestInit)
  unittest.TextTestRunner().run(suite)