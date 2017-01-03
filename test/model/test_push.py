
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_push_create_list(self):
    """push() creates a for a model attribute if the attribute is not already a 
    list
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # assert value not set
    self.assertEqual(type(a.get("key")), pymongo_basemodel.core.Undefined)

    # set string value
    a.set("key", "value")

    # push value
    a.push("key", "value")

    # assert string value created into list and value pushed to list
    self.assertEqual(a.get("key"), [ "value", "value" ])

    a.push("key.key2.key3", "value")

    # overwrite other values destructively
    self.assertEqual(a.get("key.key2.key3"), [ "value" ])

  def test_push_create_list_append_existing_value(self):
    """push() creates a for a model attribute if the attribute is not already a 
    list and appends an existing value if present
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # set non-list value on model
    a.set("key", "value1")

    # assert value not a list
    self.assertNotEqual(type(a.get("key")), list)

    # push value
    a.push("key", "value2")

    # assert value pushed to list attribute
    self.assertEqual(type(a.get("key")), list)

    # assert existing value appended to list
    self.assertIn("value1", a.get("key"))

  def test_push_string(self):
    """push() appends a value to a model list attribute. the first positional 
    argument is the model attribute if it is a string and the second positional 
    argument is the value to append
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # manually set list as attribute value
    a.attributes({ "key": [ "value1" ] })

    # push value
    a.push("key", "value2")

    # assert value pushed to list attribute
    self.assertEqual(a.get("key"), [ "value1", "value2" ])

  def test_push_dot_notation_syntax_string(self):
    """push() appends a value to a model list attribute taking into 
    consideration dot notation syntax strings
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # manually set list as attribute value
    a.attributes({
      "key1": {
        "key2": [ "value1" ]
      }
    })

    # push value
    a.push("key1.key2", "value2")

    # assert value pushed to list attribute
    self.assertEqual(a.get("key1.key2"), [ "value1", "value2" ])

    # test dot notation syntax on non existant keys
    model2 = pymongo_basemodel.core.Model()
    model2.push("key1.key2.key3", "value")
    self.assertEqual(model2.get(), {
      "key1": {
        "key2": {
          "key3": [ "value" ]
        }
      }
    })

  def test_push_create_false(self):
    """ push() will raise keyerror if key not set and typeerror if value not 
    dict while trying to evaluate keys and "create" is False
    """

    a = pymongo_basemodel.core.Model()

    with self.assertRaises(KeyError):
      a.push("key1.key2.key3", "value", create = False)

    a.set("key1", "value")

    with self.assertRaises(TypeError):
      a.push("key1.key2.key3", "value", create = False)

  def test_push_nested_model(self):
    """ push() will pass forward push operation to nested model if nested model 
    found while trying to resolve keys
    """

    a = pymongo_basemodel.core.Model()
    b = pymongo_basemodel.core.Model()
    a.set("child", b)

    a.push("child.key", "value")

    self.assertEqual(b.get("key"), [ "value" ])

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)