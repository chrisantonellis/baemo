
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_ref(self):
    """ ref will return a reference to a value for key in __dict__
    """

    a = pymongo_basemodel.core.Model()
    value = "dis muh value"
    a.attributes({
      "key": value
    })

    ref = a.ref("key")

    self.assertIs(value, ref)

  def test_ref_dot_notation(self):
    """ ref will return a reference to a value for key in __dict__ using 
    dot notation
    """

    a = pymongo_basemodel.core.Model()
    value = "dis muh value"
    a.attributes({
      "key1.key2.key3": value
    })

    ref = a.ref("key1.key2.key3")

    self.assertIs(value, ref)

  def test_ref_undefined(self):
    """ ref will return undefined if a value is the wrong type or not set in 
    __dict__ for key
    """

    a = pymongo_basemodel.core.Model()
    a.attributes({ "key": "value" })

    self.assertIsInstance(a.ref("something"), pymongo_basemodel.core.Undefined)
    self.assertIsInstance(a.ref("key.key2.key3"), pymongo_basemodel.core.Undefined)

    b = pymongo_basemodel.core.Model()
    b.attributes({ "key": pymongo_basemodel.exceptions.RelationshipResolutionError() })

    self.assertIsInstance(b.ref("key"), pymongo_basemodel.exceptions.RelationshipResolutionError)
    self.assertIsInstance(b.ref("key.key2.key3"), pymongo_basemodel.core.Undefined)

  def test_ref_nested_model(self):
    """ ref will return a reference to a value for key in __dict__ if the value 
    is a nested Model or Collection
    """

    nested_value = "nested_value"
    b = pymongo_basemodel.core.Model()
    b.attributes({ "key": nested_value })

    a = pymongo_basemodel.core.Model()
    a.attributes({ "child": b })

    c = a.ref("child")
    self.assertIs(b, c)

    d = a.ref("child.key")
    self.assertIs(d, nested_value)

  def test_ref_create_true(self):
    """ ref will return a reference to a value for key in __dict__ if the key 
    is missing or wrong type and set the correct type
    """

    a = pymongo_basemodel.core.Model()

    self.assertEqual(a.ref("key", create = True), {})
    self.assertEqual(a.attributes, { "key": {} })

    b = pymongo_basemodel.core.Model()
    b.attributes({ "key1": "value" })

    self.assertEqual(b.ref("key1.key2", create = True), {})
    self.assertEqual(b.attributes, { "key1": { "key2": {} }})


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
