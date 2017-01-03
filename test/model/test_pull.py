
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_pull_string(self):
    """ pull will remove a value from a model list attribute
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # set data on model
    a.set("key", [ "value1", "value2", "value3" ])

    # pull value from model
    a.pull("key", "value2")

    # assert that value was pulled
    self.assertEqual(a.get(), {
      "key": [ "value1", "value3" ]
    })

  def test_pull_dot_notation_syntaxz(self):
    """ pull will remove a value from a model list attribute and a dot notation 
    key
    """

    a = pymongo_basemodel.core.Model()
    a.attributes({
      "key1": {
        "key2": {
          "key3": [ "value1", "value2" ]
        }
      }
    })

    a.pull("key1.key2.key3", "value2")

    self.assertEqual(a.attributes, {
      "key1": {
        "key2": {
          "key3": [ "value1" ]
        }
      }
    })

  def test_pull_raise_exception(self):
    """ pull will raise exception if attribute key or value not set or value is 
    incorrect type
    """

    a = pymongo_basemodel.core.Model()
    a.set("key", [ "value" ])
    a.original({ "key": [ "value" ] })

    with self.assertRaises(KeyError):
      a.pull("something", "value")

    with self.assertRaises(ValueError):
      a.pull("key", "something")

    with self.assertRaises(TypeError):
      a.pull("key.key2", "value")

    a.set("key2", "value")
    with self.assertRaises(TypeError):
      a.pull("key2", "value")

  def test_pull_force(self):
    """ pull will toss exception if argument "force" is True, allowing for 
    setting pull updates in model.updates for attributes not set in 
    model.attributes
    """

    a = pymongo_basemodel.core.Model()
    a.original({ "key": "value" })

    a.pull("something", "value", force = True)
    a.pull("key", "value", force = True)
    a.pull("key.key2", "value", force = True)

    a.set("key2", "value")
    a.pull("key2", "value", force = True)

  def test_pull_nested_model(self):
    """ pull() will pass pull operation forward to nested model if nested model 
    found while trying to resolve keys
    """

    a = pymongo_basemodel.core.Model()
    b = pymongo_basemodel.core.Model()
    b.set("key", [ "value" ])
    a.set("child", b)

    a.pull("child.key", "value")    

    self.assertEqual(b.get("key"), [])


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
