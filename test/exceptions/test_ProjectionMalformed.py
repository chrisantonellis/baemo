
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_init(self):
    """ ProjectionMalformed accepts arguments "key" and "value" to populate its 
    message string
    """

    e = pymongo_basemodel.exceptions.ProjectionMalformed("test_key", "test_value")

    self.assertIsInstance(e, pymongo_basemodel.exceptions.ProjectionMalformed)
    self.assertEqual(e.key, "test_key")
    self.assertEqual(e.value, "test_value")
    self.assertEqual(e.message, "Projection malformed, invalid value 'test_value' for key 'test_key'")

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
