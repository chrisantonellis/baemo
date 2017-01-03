
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class TestCall(unittest.TestCase):

  def test_call_with_data(self):
    """ __call__ overwrites data in __dict__ with validated dict argument
    """

    c = pymongo_basemodel.core.Projection()

    c({ "key": 0 })

    self.assertEqual(c.__dict__, { "key": 0 })

  def test_call_raise_exception(self):
    """ __call__ will raise an exception if passed an invalid projection
    """

    c = pymongo_basemodel.core.Projection()

    with self.assertRaises(pymongo_basemodel.exceptions.ProjectionMalformed):
      c({ "key": "something" })

    with self.assertRaises(pymongo_basemodel.exceptions.ProjectionTypeMismatch):
      c({
        "key1": 0,
        "key2": 1
      })


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestCall)
  unittest.TextTestRunner().run(suite)