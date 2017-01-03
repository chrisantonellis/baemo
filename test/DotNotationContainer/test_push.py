
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class TestPush(unittest.TestCase):

  def test_push(self):
    """ push will append a value to a list in __dict__ and create the list if
    necessary
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    self.assertEqual(c.__dict__, {})

    c.push("key", "value1")

    self.assertEqual(c.__dict__, { "key": [ "value1" ] })

    c.push("key", "value2")

    self.assertEqual(c.__dict__, { "key": [ "value1", "value2" ] })

  def test_push_convert_value(self):
    """ push will create a list and add any existing value to the list
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    self.assertEqual(c.__dict__, {})

    c.set("key", "value1")
    self.assertEqual(c.__dict__, { "key": "value1" })

    c.push("key", "value2")
    self.assertEqual(c.__dict__, { "key": [ "value1", "value2" ] })

    d = pymongo_basemodel.core.DotNotationContainer()

    self.assertEqual(d.__dict__, {})

    d.set("key", { "inner_key1": "value" })
    self.assertEqual(d.__dict__, { "key": { "inner_key1": "value" }})

    d.push("key", { "inner_key2": "value" })
    self.assertEqual(d.__dict__, {
      "key": [
        { "inner_key1": "value" },
        { "inner_key2": "value" }
      ]
    })

  def test_push_dot_notation_key(self):
    """ push will append a value to a list in __dict__ and expand dot notation 
    key
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    self.assertEqual(c.__dict__, {})

    c.push("key1.key2", "value1")

    self.assertEqual(c.__dict__, {
      "key1": {
        "key2": [ "value1" ]
      }
    })

    c.push("key1.key2", "value2")

    self.assertEqual(c.__dict__, {
      "key1": {
        "key2": [ "value1", "value2" ]
      }
    })

  def test_push_raise_keyerror(self):
    """ push will raise keyerror if key not set and "create" is False
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    with self.assertRaises(KeyError):
      c.push("key", "value1", create = False)

  def test_push_raise_typeerror(self):
    """ push will raise typeerror if trying to push value to non list and 
    "create" is False
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    c.set("key", "value")
    self.assertEqual(c.__dict__, {
      "key": "value"
    })

    with self.assertRaises(TypeError):
      c.push("key", "value1", create = False)

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestPush)
  unittest.TextTestRunner().run(suite)
  