
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_get(self):
    """get() returns a list of values from calling model.get() on all models in 
    collection.collection
    """

    # create model
    model1 = pymongo_basemodel.core.Model()
    model1.set("key", "value")

    # create another model
    model2 = pymongo_basemodel.core.Model()
    model2.set("key", "value")

    # create collection
    collection = pymongo_basemodel.core.Collection()

    # set models on collection
    collection.add(model1)
    collection.add(model2)

    # assert values 
    self.assertEqual(collection.get(), [
      {
        "key": "value"
      },{
        "key": "value"
      }
    ])

  def test_get_pass_args_and_kwargs(self):
    """get() passes any args and kwargs to model.get
    """

    # create model
    model1 = pymongo_basemodel.core.Model()
    model1.set("key1", "value")
    model1.set("key2", "value")

    # create another model
    model2 = pymongo_basemodel.core.Model()
    model2.set("key1", "value")
    model2.set("key2", "value")

    # create collection
    collection = pymongo_basemodel.core.Collection()

    # set models on collection
    collection.add(model1)
    collection.add(model2)

    # assert projection kwarg passed forwarad
    self.assertEqual(collection.get(projection = {
      "key1": 0
    }), [
      {
        "key2": "value"
      },{
        "key2": "value"
      }
    ])

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)