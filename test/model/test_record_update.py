
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_set(self):
    """ record_update records attribute update in model.attributes in mongodb 
    update operator syntax
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # assert model.original is empty
    self.assertEqual(a.original, {})

    # set data with model.loaded set to False
    a.set("key", "value")

    # assert that change was recorded
    self.assertEqual(a.updates, {
      "$set": {
        "key": "value"
      }
    })

  def test_set_dot_notation(self):
    """ record_update records dot notation attribute update in model.attributes 
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # assert model.original is empty
    self.assertEqual(a.original, {})

    # set data
    a.set("key1.key2.key3", "value")

    # assert that change was recorded
    self.assertEqual(a.updates, {
      "$set": {
        "key1": {
          "key2": {
            "key3": "value"
          }
        }
      }
    })

  def test_set_record_false(self):
    """ record_update does not record attribute update if argument "record" is 
    False
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # set data with record set to False
    a.set("key", "value", record = False)

    # assert that change was not recorded
    self.assertEqual(a.updates, {})

  def test_set_original_not_set(self):
    """ record_update records attribute update without considering existing 
    value if model.original is empty
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # asert model.loaded is False
    self.assertEqual(a.original, {})

    # set data with model.loaded set to False
    a.set("key", "value1")
    a.set("key", "value2")
    a.set("key", "value1")

    # assert that change was recorded
    self.assertEqual(a.updates, {
      "$set": {
        "key": "value1"
      }
    })

  def test_set_original_set(self):
    """ record_update records attribute update while considering existing 
    value if model.original is set
    """

    a = pymongo_basemodel.core.Model()

    # manually set model.original
    a.original({
      "key": "value"
    })
    self.assertEqual(a.original, {
      "key": "value"
    })
    self.assertEqual(a.updates, {})

    # set value already set in model.original
    a.set("key", "value")
    # assert update was not recored
    self.assertEqual(a.updates, {})

    # set attribute to value different than value set in model.original
    a.set("key", "something")
    # assert update was recorded
    self.assertEqual(a.updates, {
      "$set": {
        "key": "something"
      }
    })

    # set attribute back to value set in model.original
    a.set("key", "value")
    # assert recorded update was removed
    self.assertEqual(a.updates, {})

  def test_unset(self):
    """ record_update records attribute update without considering previous 
    value if model.original is empty
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # manually set attributes
    a.attributes({
      "key": "value"
    })

    # unset data
    a.unset("key")

    # assert that change was recorded in model.updates
    self.assertEqual(a.updates, {
      "$unset": {
        "key": ""
      }
    })

  def test_unset_dot_notation(self):
    """ record_update records dot notation attribute update in model.attributes 
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # manually set attributes
    a.attributes({
      "key1.key2.key3": "value"
    })
    self.assertEqual(a.attributes, {
      "key1": {
        "key2": {
          "key3": "value"
        }
      }
    })

    # unset data
    a.unset("key1.key2.key3", "value")

    # assert that change was recorded in model.updates
    self.assertEqual(a.updates, {
      "$unset": {
        "key1": {
          "key2": {
            "key3": ""
          }
        }
      }
    })

  def test_unset_record_false(self):
    """ record_update does not record attribute update if argument "record" is 
    False
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # manually set attributes
    a.attributes({ "key": "value" })
    # assert that attribute set in model.attributes
    self.assertEqual(a.attributes, { "key": "value" })

    # unset data
    a.unset("key", record = False)

    # assert that change was recorded in model.attributes and not model.updates
    self.assertEqual(a.attributes, {})
    self.assertEqual(a.updates, {})

  def test_unset_original_not_set(self):
    """ record_update records attribute update without considering existing 
    value if model.original is empty
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # unset data
    a.unset("key")

    # assert that change was recorded in model.attributes and not model.updates
    self.assertEqual(a.updates, {
      "$unset": {
        "key": ""
      }
    })

  def test_unset_original_set(self):
    """ record_update records attribute update while considering existing 
    value if model.original is set
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # manually set attributes
    a.attributes({ "key": "value" })
    # manually set model.original
    a.original({ "key": "value" })

    with self.assertRaises(KeyError):
      a.unset("something")

  def test_unset_force(self):
    """ record_update records attribute update without considering existing 
    value in model.attronites if argument "force" is True
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # manually set attributes
    a.attributes({ "key": "value" })

    a.unset("something", force = True)

    self.assertEqual(a.updates, {
      "$unset": {
        "something": ""
      }
    })

  def test_push(self):
    """ record_update records attribute update in model.attributes in mongodb 
    update operator syntax
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # push data
    a.push("key", "value")

    # assert that change was recorded
    self.assertEqual(a.updates, {
      "$push": {
        "key": "value"
      }
    })

  def test_push_dot_notation(self):
    """ record_update records dot notation attribute update in model.attributes 
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # assert model.original is empty
    self.assertEqual(a.original, {})

    # push data
    a.push("key1.key2.key3", "value")

    # assert that change was recorded
    self.assertEqual(a.updates, {
      "$push": {
        "key1": {
          "key2": {
            "key3": "value"
          }
        }
      }
    })

  def test_push_record_false(self):
    """ record_update does not record attribute update if argument "record" is 
    False
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # set data with record set to False
    a.push("key", "value", record = False)

    self.assertEqual(a.attributes, {
      "key": [ "value" ]
    })

    # assert that change was not recorded
    self.assertEqual(a.updates, {})

  def test_push_iterator(self):
    """ record_update records attribute update and manages use of mongodb 
    iterator where necessary
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # push data
    a.push("key", "value1")

    # assert state of model.changed
    self.assertEqual(a.updates, {
      "$push": {
        "key": "value1"
      }
    })

    # push more data
    a.push("key", "value2")

    # assert state of model.changed
    self.assertEqual(a.updates, {
      "$push": {
        "key": {
          "$each": [ "value1", "value2" ]
        }
      }
    })

  def test_push_pull_intersect(self):
    """ record_updates keeps $pull and $push values unique to keep the mongo 
    query valid
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # manually set attributes
    a.attributes({
      "key": [ "value1", "value2", "value3" ]
    })

    # pull data
    a.pull("key", "value1")
    a.pull("key", "value2")
    a.pull("key", "value3")

    # assert state of model.changed
    self.assertEqual(a.updates, {
      "$pull": {
        "key": {
          "$in": [ "value1", "value2", "value3" ]
        }
      }
    })

    # push a value present in $pull
    a.push("key", "value2")

    # assert state of model.changed
    self.assertEqual(a.updates, {
      "$push": {
        "key": "value2"
      },
      "$pull": {
        "key": {
          "$in": [ "value1", "value3" ]
        }
      }
    })

  def test_push_pull_remove_iterator(self):
    """ record_updates will remove the $in iterator from $pull if enough values 
    are removed from $pull by push operations
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # manually set attributes
    a.attributes({
      "key": [ "value1", "value2" ]
    })

    # pull data
    a.pull("key", "value1")
    a.pull("key", "value2")

    # assert state of model.updates
    self.assertEqual(a.updates, {
      "$pull": {
        "key": {
          "$in": [ "value1", "value2" ]
        }
      }
    })

    # push a value present in $pull
    a.push("key", "value2")

    # assert state of model.updates
    self.assertEqual(a.updates, {
      "$push": {
        "key": "value2"
      },
      "$pull": {
        "key": "value1"
      }
    })

  def test_push_pull_remove(self):
    """ record_updates will remove the $pull operator from model.changed if 
    enough values are removed from $pull by push operations
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # manually set attributes
    a.attributes({
      "key": [ "value1" ]
    })

    # pull data
    a.pull("key", "value1")

    # assert state of model.updates
    self.assertEqual(a.updates, {
      "$pull": {
        "key": "value1"
      }
    })

    # push a value present in $pull
    a.push("key", "value1")

    # assert state of model.updates
    self.assertEqual(a.updates, {
      "$push": {
        "key": "value1"
      }
    })

  def test_pull(self):
    """ record_update records attribute update in model.attributes in mongodb 
    update operator syntax
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # manually set attributes
    a.attributes({
      "key": [ "value" ]
    })

    # push data
    a.pull("key", "value")

    # assert that change was recorded
    self.assertEqual(a.updates, {
      "$pull": {
        "key": "value"
      }
    })

  def test_pull_dot_notation(self):
    """ record_update records dot notation attribute update in model.attributes 
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # assert model.original is empty
    self.assertEqual(a.original, {})

    # manually set attributes
    a.attributes({
      "key1": {
        "key2": {
          "key3": [ "value" ]
        }
      }
    })

    # pull data
    a.pull("key1.key2.key3", "value")

    # assert that change was recorded
    self.assertEqual(a.updates, {
      "$pull": {
        "key1": {
          "key2": {
            "key3": "value"
          }
        }
      }
    })

  def test_pull_record_false(self):
    """ record_update does not record attribute update if argument "record" is 
    False
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # manually set attributes
    a.attributes({
      "key": [ "value" ]
    })

    # set data with record set to False
    a.pull("key", "value", record = False)

    self.assertEqual(a.attributes, { "key": [] })

    # assert that change was not recorded
    self.assertEqual(a.updates, {})

  def test_pull_iterator(self):
    """ record_update records attribute update and manages use of mongodb 
    iterator where necessary
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # push data
    a.push("key", "value1")

    # assert state of model.changed
    self.assertEqual(a.updates, {
      "$push": {
        "key": "value1"
      }
    })

    # push more data
    a.push("key", "value2")

    # assert state of model.changed
    self.assertEqual(a.updates, {
      "$push": {
        "key": {
          "$each": [ "value1", "value2" ]
        }
      }
    })

  def test_pull_push_intersect(self):
    """ record_updates keeps $pull and $push values unique to keep the mongo 
    query valid
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # manually set attributes
    a.attributes({
      "key": [ "value1", "value2", "value3" ]
    })

    # pull data
    a.pull("key", "value1")
    a.pull("key", "value2")
    a.pull("key", "value3")

    # assert state of model.changed
    self.assertEqual(a.updates, {
      "$pull": {
        "key": {
          "$in": [ "value1", "value2", "value3" ]
        }
      }
    })

    # push a value present in $pull
    a.push("key", "value2")

    # assert state of model.changed
    self.assertEqual(a.updates, {
      "$push": {
        "key": "value2"
      },
      "$pull": {
        "key": {
          "$in": [ "value1", "value3" ]
        }
      }
    })

  def test_pull_push_remove_iterator(self):
    """ record_updates will remove the $in iterator from $pull if enough values 
    are removed from $pull by push operations
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # manually set attributes
    a.attributes({
      "key": [ "value1", "value2" ]
    })

    # pull data
    a.pull("key", "value1")
    a.pull("key", "value2")

    # assert state of model.updates
    self.assertEqual(a.updates, {
      "$pull": {
        "key": {
          "$in": [ "value1", "value2" ]
        }
      }
    })

    # push a value present in $pull
    a.push("key", "value2")

    # assert state of model.updates
    self.assertEqual(a.updates, {
      "$push": {
        "key": "value2"
      },
      "$pull": {
        "key": "value1"
      }
    })

  def test_pull_push_remove(self):
    """ record_updates will remove the $pull operator from model.changed if 
    enough values are removed from $pull by push operations
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # manually set attributes
    a.attributes({
      "key": [ "value1" ]
    })

    # pull data
    a.pull("key", "value1")

    # assert state of model.updates
    self.assertEqual(a.updates, {
      "$pull": {
        "key": "value1"
      }
    })

    # push a value present in $pull
    a.push("key", "value1")

    # assert state of model.updates
    self.assertEqual(a.updates, {
      "$push": {
        "key": "value1"
      }
    })


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)