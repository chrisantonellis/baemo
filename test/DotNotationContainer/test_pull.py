
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class TestPull(unittest.TestCase):

  def test_pull(self):
    """ pull will remove a value from a list in __dict__
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    self.assertEqual(c.__dict__, {})

    c.set("key", [ "value1", "value2" ])

    self.assertEqual(c.__dict__, { "key": [ "value1", "value2" ] })

    c.pull("key", "value2")

    self.assertEqual(c.__dict__, { "key": [ "value1" ] })

  def test_pull_value_not_found(self):
    """ pull will return false if called for a value that does not exist
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    self.assertEqual(c.__dict__, {})

    c.set("key", [ "value1" ])

    self.assertEqual(c.__dict__, { "key": [ "value1" ] })

    with self.assertRaises(ValueError):
      c.pull("key", "value2")

  def test_pull_value_wrong_type(self):
    """ pull will return false if called for a value that is wrong tyoe
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    self.assertEqual(c.__dict__, {})

    c.set("key", "value")

    self.assertEqual(c.__dict__, { "key": "value" })

    with self.assertRaises(TypeError):
      c.pull("key", "value1")

  def test_pull_dot_notation(self):
    """ pull will remove a value from a list in __dict__ and expand dot 
    notation key
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    self.assertEqual(c.__dict__, {})

    c.set("key1", { "key2": [ "value1", "value2" ]})

    self.assertEqual(c.__dict__, { "key1": { "key2": [ "value1", "value2" ]} })

    c.pull("key1.key2", "value2")

    self.assertEqual(c.__dict__, { "key1": { "key2": [ "value1" ] }})

  def test_pull_dot_notation_value_not_found(self):
    """ pull will remove a value from a list in __dict__ and expand dot 
    notation key
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    self.assertEqual(c.__dict__, {})

    c.set("key1", { "key2": [ "value1", "value2" ]})

    self.assertEqual(c.__dict__, { "key1": { "key2": [ "value1", "value2" ]} })

    with self.assertRaises(KeyError):
      c.pull("key1.key3", "value1")

    with self.assertRaises(KeyError):
      c.pull("key1.key3.key7", "value1")

  def test_pull_cleanup(self):
    """ pull will unset key if pull results in empty dict and "cleanup" is True
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    self.assertEqual(c.__dict__, {})

    c.set("key", [ "value" ])

    self.assertEqual(c.__dict__, {
      "key": [ "value" ],
    })

    c.pull("key", "value", cleanup = True)

    self.assertEqual(c.__dict__, {})



if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestPull)
  unittest.TextTestRunner().run(suite)
  