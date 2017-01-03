
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class TestUnset(unittest.TestCase):

  def test_unset(self):
    """ set will set key, value data in __dict__
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    self.assertEqual(c.__dict__, {})

    c.set("key", "value")

    self.assertEqual(c.__dict__, { "key": "value" })

    c.unset("key")

    self.assertEqual(c.__dict__, {})

  def test_unset_key_not_set(self):
    """ set will set key, value data in __dict__
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    self.assertEqual(c.__dict__, {})

    c.set("key", "value")

    self.assertEqual(c.__dict__, { "key": "value" })

    with self.assertRaises(KeyError):
      c.unset("key1")

    with self.assertRaises(KeyError):
      c.unset("key.key2")

  def test_unset_dot_notation(self):
    """ set will set key, value data in __dict__
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    self.assertEqual(c.__dict__, {})

    c.set("key1.key2", "value")

    self.assertEqual(c.__dict__, { "key1": { "key2": "value" }})

    c.unset("key1.key2")

    self.assertEqual(c.__dict__, { "key1": {} })

  def test_unset_cleanup(self):
    """ unset will remove keys cascading upwards if unset results in empty dict 
    and "cleanup" is True
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    c.set("key1.key2.key3", "value")
    c.set("key1.key4", "value")

    self.assertEqual(c.__dict__, {
      "key1": {
        "key2": {
          "key3": "value"
        },
        "key4": "value"
      }
    })

    c.unset("key1.key2.key3", cleanup = True)

    self.assertEqual(c.__dict__, {
      "key1": {
        "key4": "value"
      }
    })


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestUnset)
  unittest.TextTestRunner().run(suite)
  