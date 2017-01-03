
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_set_by_string(self):
    """ set sets an attribute of a model to a value
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # set data on model
    a.set("key", "value")

    # assert value set on model at key
    self.assertEqual(a.get(), {
      "key": "value"
    })
    self.assertEqual(a.get("key"), "value")

    # create model
    b = pymongo_basemodel.core.Model()

    # set data on model
    b.set({ "key": "value" })

    # assert value set on model at key
    self.assertEqual(b.get(), {
      "key": "value"
    })
    self.assertEqual(b.get("key"), "value")

  def test_set_by_dict_with_nested_data(self):
    """ set sets the attributes of a model to the keys and values of the first 
    positional argument if it is a dict, taking into consideration nested data
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # set data on model
    a.set({
      "key1": "value",
      "key2": {
        "key3": "value"
      }
    })

    # assert value set on model at key
    self.assertEqual(a.get(), {
      "key1": "value",
      "key2": {
        "key3": "value"
      }
    })
    self.assertEqual(a.get("key2"), { "key3": "value" })

  def test_set_by_string_with_dot_notation_syntax(self):
    """set() sets an attribute of a model by the first positional argument 
    'key' if it is a string to the second position argument 'value' taking into 
    consideration dot notation syntax keys
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # set data on model
    a.set({
      "key1": "value",
      "key2": {
        "key3": "value"
      }
    })

    # set data on model via dot notation syntax
    a.set("key2.key4", "value")

    # assert value set on model at key without overwriting other values
    self.assertEqual(a.get(), {
      "key1": "value",
      "key2": {
        "key3": "value",
        "key4": "value"
      }
    })

  def test_set_data_on_nested_model(self):
    """ set will call model.set on nested model with data if nested model is 
    targeted
    """

    # create model
    model1 = pymongo_basemodel.core.Model()

    # create another model with nested model
    model2 = pymongo_basemodel.core.Model()
    model2.set("partner", model1)

    # set data on nested model
    model2.set("partner.key", "value")

    # assert data set on nested model
    self.assertEqual(model2.get(), {
      "partner": {
        "key": "value"
      }
    })

  def test_set_nested_exception(self):
    """ set will overwrite nested exception if found while trying to set value 
    and "create" is True
    """

    a = pymongo_basemodel.core.Model()
    a.attributes({
      "key": pymongo_basemodel.exceptions.RelationshipResolutionError(),
      "key1.key2": pymongo_basemodel.exceptions.RelationshipResolutionError()
    })

    a.set("key", "value")
    self.assertEqual(a.attributes["key"], "value")

    a.set("key1.key2.key3", "value")
    self.assertEqual(a.attributes["key1.key2.key3"], "value")

  def test_set_overwrite_value_with_nested_value(self):
    """ set will overwrite an existing value with nested value when using dot 
    notation syntax
    """

    # create model
    model = pymongo_basemodel.core.Model()

    # set data on model
    model.set("key", "value")

    # assert value set on model at key
    self.assertEqual(model.get(), {
      "key": "value"
    })

    # set nested data over string value
    model.set("key.key2", "value")

    self.assertEqual(model.get(), {
      "key": {
        "key2": "value"
      }
    })

  def test_set_create_false(self):
    """ set will raise an exception if key does not exist or value is wrong 
    type if "create" is False
    """

    # key error, key does not exist
    a = pymongo_basemodel.core.Model()
    with self.assertRaises(KeyError):
      a.set("key", "value", create = False)

    # type error, value is wrong type
    a.attributes({ "key": "value" })
    with self.assertRaises(TypeError):
      a.set("key.key2", "value", create = False)

    # type error, value is exception
    a.attributes({ "key": pymongo_basemodel.exceptions.RelationshipResolutionError() })
    with self.assertRaises(TypeError):
      a.set("key.key2", "value", create = False)


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
