
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo
import pymongo_basemodel

class Test(unittest.TestCase):

  def setUp(self):
    global client, collection_name, TestModel, TestCollection

    client = pymongo.MongoClient(connect = False)
    collection_name = "%s_%s" % (self.__class__.__name__, self._testMethodName)

    class TestModel(pymongo_basemodel.core.Model):
      pymongo_collection = client["pymongo_basemodel"][collection_name]
      def __init__(self, *args, **kwargs):
        super(TestModel, self).__init__(*args, **kwargs)

    class TestCollection(pymongo_basemodel.core.Collection):
      model = TestModel
      def __init__(self, *args, **kwargs):
        super(TestCollection, self).__init__(*args, **kwargs)

  def tearDown(self):
    client["pymongo_basemodel"].drop_collection(collection_name)


  def test_find(self):
    """find() will return all docs from collection.model.pymongo_collection if 
    collection.target is None, set the data on collection.model instances and 
    set the models in collection.collection
    """

    # create model
    model1 = TestModel()
    model1.save()

    # create another model
    model2 = TestModel()
    model2.save()

    # create collection
    collection = TestCollection()

    # assert collection target is None
    self.assertEqual(collection.target, {})

    # call find on collection
    collection.find()

    # assert models found
    self.assertEqual(len(collection.collection), 2)
    for model in collection:
      self.assertEqual(type(model), TestModel)

  def test_find_with_target(self):
    """find() will return all docs from collection.model.pymongo_collection 
    that match collection.target and se the docs as collection.model 
    instances in collection.collection
    """

    # create model
    model1 = TestModel()
    model1.set("key", "value1")
    model1.save()

    # create another model
    model2 = TestModel()
    model2.set("key", "value2")
    model2.save()

    model2_id = model2.get(model2.id_attribute)

    # create collection
    collection = TestCollection()

    # set target on collection
    collection.set_target({ "key": "value2" })

    # call find on collection
    collection.find()

    # assert only one model returned that matches collection.target
    self.assertEqual(len(collection.collection), 1)

    # assert that model returned is correct model
    self.assertEqual(collection.collection[0].get(TestModel.id_attribute), model2_id)

  def test_find_with_projection(self):
    """find() will return all docs from collection.model.pymongo_collection if 
    collection.target is None, set the data on collection.model instances and 
    set the models in collection.collection, and pass forward projection
    """

    # create model
    model1 = TestModel()
    model1.set("key1", "value")
    model1.set("key2", "value")
    model1.set("key3", "value")
    model1.save()

    # create another model
    model2 = TestModel()
    model2.set("key1", "value")
    model2.set("key2", "value")
    model2.set("key3", "value")
    model2.save()

    # create collection
    collection = TestCollection()

    # assert collection target is None
    self.assertEqual(collection.target, {})

    # call find on collection_name
    collection.find(projection = {
      "key2": 1
    })

    # assert models found
    self.assertEqual(len(collection.collection), 2)
    for model in collection:
      self.assertEqual(type(model), TestModel)
      self.assertEqual(model.get(), {
        "_id": model.get("_id"),
        "key2": "value"
      })

  def test_find_with_target_and_projection(self):
        # create model
    model1 = TestModel()
    model1.set("key1", "value1")
    model1.set("key2", "value1")
    model1.set("key3", "value1")
    model1.save()

    # create another model
    model2 = TestModel()
    model2.set("key1", "value2")
    model2.set("key2", "value2")
    model2.set("key3", "value2")
    model2.save()

    # create collection with target
    collection = TestCollection({
      "key1": "value1"
    })

    # call find on collection
    collection.find(projection = {
      "key3": 0
    })

    # assert models found
    self.assertEqual(len(collection.collection), 1)
    for model in collection:
      self.assertEqual(model.get("_id"), model1.get("_id"))
      self.assertEqual(model.get(), {
        "_id": model.get("_id"),
        "key1": "value1",
        "key2": "value1"
      })

  def test_find_mongo_syntax_target(self):
    """find() willl return all docs from collection.model.pymongo_collection
    that match collection.target in mongo operator syntax and set the docs 
    as collection.model instances in collection.collection
    """

    # create model
    model1 = TestModel()
    model1.set("key", [ "value1", "value2" ])
    model1.save()

    model1_id = model1.get(model1.id_attribute)

    # create another model
    model2 = TestModel()
    model2.set("key", [ "value1" ])
    model2.save()

    # create collection
    collection = TestCollection()

    # set target on collection
    collection.set_target({ "key": { "$in": [ "value2" ] }})

    # call find on collection
    collection.find()

    # assert only one model returned that matches collection.target
    self.assertEqual(len(collection.collection), 1)

    # assert that model returned is correct model
    self.assertEqual(collection.collection[0].get(TestModel.id_attribute), model1_id)

  def test_find_default_find_projection(self):

    class MyCollection(TestCollection):
      def __init__(self):
        super().__init__()
        self.default_find_projection({ "key1": 0 })

    mymodel = TestModel()
    mymodel.set({
      "key1": "value",
      "key2": "value",
      "key3": "value"
    })
    mymodel.save()

    collection = MyCollection()
    collection.set_target(mymodel.get_id())
    collection.find()

  def test_find_model_default_find_projection(self):

    class MyModel(TestModel):
      def __init__(self):
        super().__init__()
        self.default_find_projection({ "key1": 0 })

    class MyCollection(TestCollection):
      model = MyModel

    mymodel = MyModel()
    mymodel.set({
      "key1": "value",
      "key2": "value",
      "key3": "value"
    })
    mymodel.save()

    collection = MyCollection()
    collection.set_target(mymodel.get_id())
    collection.find(default_model_projection = True)


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
