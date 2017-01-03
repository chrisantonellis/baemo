
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class TestGet(unittest.TestCase):

  def test_get(self):
    """ get will return a value for key in __dict__
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    c.set("key", "value")

    self.assertEqual(c.get("key"), "value")

  def test_get_all(self):
    """ get will return all keys and values for __dict__ when called with no 
    arguments
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    c.set("key", "value")

    self.assertEqual(c.get(), { "key": "value" })

  def test_get_dot_notation(self):
    """ get will return a value for key in __dict__ and expand dot notation key
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    c.set("key1", { "key2": { "key3": "value"}})

    self.assertEqual(c.get("key1.key2.key3"), "value")

  def test_get_not_found(self):
    """ get will return undefined for keys not found
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    c.set("key1", { "key2": { "key3": "value"}})

    self.assertEqual(True, True)

    with self.assertRaises(KeyError):
      c.get("key2")


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestGet)
  unittest.TextTestRunner().run(suite)
  