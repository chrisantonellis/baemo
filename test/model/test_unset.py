
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_unset_string(self):
    """unset() removes an attribute from a model. the first positional argument 
    is the model attribute if it is a string
    """

    # create model
    model = pymongo_basemodel.core.Model()

    # set data on model
    model.set({
      "key1": "value",
      "key2": "value"
    })

    # unset attribute on model
    model.unset("key1")

    # assert that attribute was unset
    self.assertEqual(model.get(), {
      "key2": "value"
    })

  def test_unset_dot_notation_syntax_string(self):
    """unset() removes an attribute from a model taking into consideration dot 
    notation syntax strings
    """

    # create model
    model = pymongo_basemodel.core.Model()

    # set data on model
    model.set({
      "key1": {
        "key2": {
          "key3": "value",
          "key4": "value"
        }
      }
    })

    # unset attribute on model
    model.unset("key1.key2.key3")

    # assert that attribute was unset
    self.assertEqual(model.get(), {
      "key1": {
        "key2": {
          "key4": "value"
        }
      }
    })

    # set original on model to trigger exception
    model.original({
      "key": "value"
    })

    # values that arent set
    with self.assertRaises(KeyError):
      model.unset("some.thing")

  def test_unset_nested_model(self):
    """ unset() removes an attribute from a nesetd model if nested model found 
    while trying to resolve keys
    """

    a = pymongo_basemodel.core.Model()
    a.attributes({ "key": "value" })

    b = pymongo_basemodel.core.Model()
    b.attributes({ "child": a })

    self.assertEqual(b.attributes, {
      "child": a
    })

    b.unset("child.key")

    self.assertEqual(b.attributes, {
      "child": a
    })

    self.assertEqual(a.attributes, {})

  def test_unset_no_exception(self):
    """ unset() will not raise a typeerror if an exception is found while 
    trying to resolve keys if model.original is empty or "force" is True
    """

    a = pymongo_basemodel.core.Model()
    a.unset("key", "value")
    a.original({ "key": "value" })
    a.unset("key", "value", force = True)

  def test_unset_exception(self):
    """ unset() will raise a typeerror if an exception is found while trying 
    to resolve keys
    """

    a = pymongo_basemodel.core.Model()
    a.attributes({ "key1": pymongo_basemodel.exceptions.RelationshipResolutionError() })
    a.original(a.ref())

    with self.assertRaises(TypeError):
      a.unset("key1.key2.key3")

    a.attributes({ "key1": "value" })
    with self.assertRaises(TypeError):
      a.unset("key1.key2.key3")


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
