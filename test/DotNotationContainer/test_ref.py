
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_ref(self):
    """ ref will return a reference to a value for key in __dict__
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    c.set("key", "value")

    value = c.ref("key")

    self.assertIs(c.ref("key"), value)

  def test_ref_dot_notation(self):
    """ ref will return a reference to a value for key in __dict__ using 
    dot notation
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    c.set("key1.key2.key3", "value")

    value = c.ref("key1.key2.key3")

    self.assertIs(c.ref("key1.key2.key3"), value)

  def test_ref_create(self):
    """ ref will return a reference to a value for key in __dict__ and create 
    nested dicts as needed if "create" is True
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    c.ref("key1", create = True)

    self.assertEqual(c.__dict__, {
      "key1": {}
    })

    c({ "key1": "value" })
    self.assertEqual(c.__dict__, {
      "key1": "value"
    })

    c.ref("key1.key2", create = True)

    self.assertEqual(c.__dict__, {
      "key1": {
        "key2": {}
      }
    })

  def test_ref_raise_keyerror(self):
    """ ref will raise a keyerror if key not found and "create" is false
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    with self.assertRaises(KeyError):
      c.ref("key")

  def test_ref_raise_valueerror(self):
    """ ref will raise a valueerror if key suggests to search for nested key in 
    non dict type
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    c({ "key1": "value" })

    with self.assertRaises(TypeError):
      c.ref("key1.key2")

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
  