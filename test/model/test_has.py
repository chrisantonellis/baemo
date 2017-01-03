  
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_has(self):
    """ has will return True if a value is set in __dict__ for key
    """

    a = pymongo_basemodel.core.Model()

    a.attributes({ "key": "value" })

    self.assertEqual(a.has("key"), True)

  def test_has_dot_notation(self):
    """ has will return True if a value is set in __dict__ for dot notation key
    """

    a = pymongo_basemodel.core.Model()
    a.attributes({ "key1.key2.key3": "value" })
    self.assertEqual(a.has("key1.key2.key3"), True)

  def test_has_false(self):
    """ has will return False if a value is not set in __dict__ for key or if 
    value is wrong type
    """

    a = pymongo_basemodel.core.Model()
    a.attributes({ "key": "value" })

    self.assertEqual(a.has("something"), False)
    self.assertEqual(a.has("key.key2.key3"), False)

  def test_has_nested_model(self):
    """ ref will return a reference to a value for key in __dict__ if the value 
    is a nested Model or Collection
    """
    b = pymongo_basemodel.core.Model()
    b.attributes({ "key": "nested_value" })

    a = pymongo_basemodel.core.Model()
    a.attributes({ "child": b })
    self.assertEqual(a.has("child"), True)
    self.assertEqual(a.has("child.key"), True)

    self.assertEqual(a.has("child.somethin"), False)

  def test_has_exception(self):
    """ ref will return a reference to a value for key in __dict__ if the value 
    is an exception even if the exception is encounted with leftover keys in a 
    dot notation string
    """

    a = pymongo_basemodel.core.Model()
    a.attributes({ "key": pymongo_basemodel.exceptions.RelationshipResolutionError() })

    self.assertEqual(a.has("key"), True)
    self.assertEqual(a.has("key.key2.key3"), False)


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
  