
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
        super().__init__(*args, **kwargs)

    class TestCollection(pymongo_basemodel.core.Collection):
      model = TestModel
      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

  def tearDown(self):
    client["pymongo_basemodel"].drop_collection(collection_name)

  def test_save(self):
    """save() checks the state of each model in collection.collection and 
    creates a pymongo bulk write operation instance then sends all bulk write 
    operations to collection.model.pymongo_collection at the same time
    """

    # create model and change after saving to create update operation
    model1 = TestModel()
    model1.save()
    model1.set("key", "value1")

    # capture model id
    model1_id = model1.get(model1.id_attribute)

    # create another model and change before saving to create insert operation
    model2 = TestModel()
    model2.set("key", "value2")

    # create model, save, and set delete flag to create remove operation
    model3 = TestModel()
    model3.save()
    model3.delete()

    # capture model id
    model3_id = model3.get(model3.id_attribute)

    # create collection
    collection = TestCollection()

    # set models on collection
    collection.add(model1)
    collection.add(model2)
    collection.add(model3)

    # save collection
    collection.save()

    # assert first model was updated
    model1_copy = TestModel(model1_id)
    model1_copy.find()
    self.assertEqual(model1_copy.get(), {
      model1_copy.id_attribute: model1_id,
      "key": "value1"
    })

    # assert second model was inserted
    self.assertIn(model2.id_attribute, model2.attributes)

    model2_copy = TestModel(model2.attributes[model2.id_attribute])
    model2_copy.find()

    self.assertEqual(model2_copy.get(), {
      model2_copy.id_attribute: model2.get(model2_copy.id_attribute),
      "key": "value2"
    })

    # assert third model was deleted
    model3_copy = TestModel(model3_id)
    with self.assertRaises(pymongo_basemodel.exceptions.ModelNotFound):
      model3_copy.find()

  def test_save_delete_raise_exception(self):
    """save() will raise exception if trying to delete a document from a model 
    without a target set
    """

    model = TestModel()
    model.save()
    model.target = {}
    model.delete()

    collection = TestCollection()
    collection.add(model)

    with self.assertRaises(pymongo_basemodel.exceptions.ModelTargetNotSet):
      collection.save()

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)