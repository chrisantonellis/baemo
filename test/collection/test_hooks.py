
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

  def test_pre_find_hook(self):
    """pre_find_hook() will be called before find() returns data when calling 
    find() on a collection
    """

    # define collection with pre_find_hook
    class MyCollection(TestCollection):
      def pre_find_hook(self):
        # create a new model
        model = TestModel()
        model.set("unique_key", "unique_value")
        self.add(model)

    # create collection
    collection = MyCollection()

    # call find, finding nothing because pymongo_collection is empty
    collection.find()

    # assert that model injected into collection.collection by hook
    self.assertEqual(len(collection.collection), 1)
    self.assertEqual(type(collection.collection[0]), TestModel)

  def test_post_find_hook(self):
    """post_find_hook() will be called after find() returns data when calling 
    find() on a collection
    """

    # create and save some models
    model1 = TestModel()
    model1.save()

    model2 = TestModel()
    model2.save()

    model3 = TestModel()
    model3.save()

    # define collection with post_find_hook
    class MyCollection(TestCollection):
      def post_find_hook(self):
        self.collection = []

    # create normal collection
    collection1 = TestCollection()
    collection1.find()

    # assert collection is populated with models
    self.assertEqual(len(collection1.collection), 3)

    # create collection with post_find_hook
    collection2 = MyCollection()
    collection2.find()

    # assert models removed by post find hook
    self.assertEqual(len(collection2.collection), 0)

  def test_pre_modify_hook(self):
    """pre_modify_hook() will be called before save() writes data to the db 
    when calling save() on a collection
    """

    # define collection with pre_find_hook
    class MyCollection(TestCollection):
      def pre_modify_hook(self):
        # create a new model
        model = TestModel()
        model.set("key", "hook_value")
        self.add(model)

    # create model
    model = TestModel()
    model.set("key", "value")

    # create collection
    collection = MyCollection()

    # set model on collection
    collection.add(model)

    # save collection
    collection.save()

    # asssert two models in collection, one from pre_modify_hook
    self.assertEqual(len(collection.collection), 2)

    # assert that model added by pre_modify_hook was saved too
    for model in collection:
      self.assertIn(model.id_attribute, model.attributes)

  def test_post_modify_hook(self):
    """post_modify_hook() will be called after save() writes data to the db 
    when calling save() on a collection
    """

    # define collection with pre_find_hook
    class MyCollection(TestCollection):
      def __init__(self, *args, **kwargs):
        super(MyCollection, self).__init__(*args, **kwargs)

      def post_modify_hook(self):
        self.collection = []

    # create models
    model1 = TestModel()
    model2 = TestModel()
    model3 = TestModel()

    # create collection
    collection = MyCollection()

    # add models to collection
    collection.add(model1)
    collection.add(model2)
    collection.add(model3)

    # assert that collection is not empty before save()
    self.assertEqual(len(collection.collection), 3)

    # save collection
    collection.save()

    # assert that collection is empty after save() due to post_modify_hook
    self.assertEqual(len(collection.collection), 0)

  def test_model_find_hooks(self):

    class MyModel(TestModel):
      def pre_find_hook(self):
        pass
      def post_find_hook(self):
        pass

    class MyCollection(TestCollection):
      model = MyModel

    mymodel = MyModel()
    mymodel.save()

    mycollection = MyCollection()
    mycollection.set_target(mymodel.get_id())
    mycollection.find()

  def test_model_insert_hooks(self):

    class MyModel(TestModel):
      def pre_insert_hook(self):
        pass
      def post_insert_hook(self):
        pass

    class MyCollection(TestCollection):
      model = MyModel

    mycollection = MyCollection()
    mycollection.add(MyModel())
    mycollection.save()

  def test_model_update_hooks(self):

    class MyModel(TestModel):
      def pre_update_hook(self):
        pass
      def post_update_hook(self):
        pass

    class MyCollection(TestCollection):
      model = MyModel

    mymodel = MyModel()
    mymodel.save()

    mycollection = MyCollection()
    mycollection.add(mymodel)
    mycollection.set("key", "value")
    mycollection.save()

  def test_model_delete_hooks(self):

    class MyModel(TestModel):
      def pre_delete_hook(self):
        pass
      def post_delete_hook(self):
        pass

    class MyCollection(TestCollection):
      model = MyModel

    mymodel = MyModel()
    mymodel.save()

    mycollection = MyCollection()
    mycollection.add(mymodel)
    mycollection.delete()
    mycollection.save()


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)