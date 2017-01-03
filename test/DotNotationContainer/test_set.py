
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class TestSet(unittest.TestCase):

  def test_set(self):
    """ set will set key, value data in __dict__
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    self.assertEqual(c.__dict__, {})

    c.set("key", "value")

    self.assertEqual(c.__dict__, { "key": "value" })

  def test_set_dot_notation_key(self):
    """ set will set key, value data in __dict__ and expand dot notation key
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    self.assertEqual(c.__dict__, {})

    c.set("key1.key2", "value")

    self.assertEqual(c.__dict__, {
      "key1": {
        "key2": "value" 
      }
    })

  def test_set_create_false_keyerror(self):
    """ set will raise keyerror if key not set and "create" is False
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    with self.assertRaises(KeyError):
      c.set("key", "value", create = False)


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestSet)
  unittest.TextTestRunner().run(suite)
  