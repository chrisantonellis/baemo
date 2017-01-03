
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

  def tearDown(self):
    client["pymongo_basemodel"].drop_collection(collection_name)

  def test_find(self):
    """find() uses model.target to lookup the model from the pymongo collection 
    model.pymongo_collection and populates model.attributes with the data
    returned
    """

    # create and save model to get model id
    temp_model = TestModel()
    temp_model.attributes({ "key": "value" })
    model_id = temp_model.save().get(temp_model.id_attribute)

    # create model
    model = TestModel()

    # set target
    model.target({ TestModel.id_attribute: model_id })

    # call find
    model.find()

    # assert that model.loaded is true and attributes were loaded from db
    self.assertIn("key", model.attributes)
    self.assertEqual(model.attributes["key"], "value")

  def test_find_raise_exception(self):
    """find() will raise exception if called on a model without a target set
    """

    # create model
    model = TestModel()

    # assert that exception raised
    with self.assertRaises(pymongo_basemodel.exceptions.ModelTargetNotSet):
      model.find()

  def test_find_with_default_find_projection(self):
    """find() will apply default_find_projection to the pymongo find operation
    if set on the model
    """

    # define data
    data = {
      "key1": "value",
      "key2": "value",
      "key3": "value"
    }

    # create and save model to get model id
    temp_model = TestModel()
    temp_model.attributes(data)
    model_id = temp_model.save().attributes[TestModel.id_attribute]

    # define model with default find projection
    class TestModelWithDefaultFindProjection(TestModel):
      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_find_projection({
          "key1": 0
        })

    # create model
    model = TestModelWithDefaultFindProjection()

    # set target
    model.target({ TestModel.id_attribute: model_id })

    # call find
    model.find()

    # assert that default_find_projection applied to pymongo find operation
    self.assertEqual(model.attributes, {
      TestModel.id_attribute: model_id,
      "key2": "value",
      "key3": "value"
    })

  def test_find_with_argument_projection(self):
    """find() will apply keyword argument "projection" to the pymongo find 
    operation
    """

    # define data
    data = {
      "key1": "value",
      "key2": "value",
      "key3": "value"
    }

    # create and save model to get model id
    temp_model = TestModel()
    temp_model.attributes(data)
    model_id = temp_model.save().attributes[TestModel.id_attribute]

    # create model
    model = TestModel()

    # set target
    model.target({ TestModel.id_attribute: model_id })

    # call find
    model.find(projection = {
      "key1": 0
    })

    # assert that default_find_projection applied to pymongo find operation
    self.assertEqual(model.attributes, {
      TestModel.id_attribute: model_id,
      "key2": "value",
      "key3": "value"
    })

  def test_find_with_default_get_projection_and_argument_projection(self):
    """find() will merge keyword argument "projection" with 
    default_find_projection
    """

    # define data
    data = {
      "key1": "value",
      "key2": "value",
      "key3": "value"
    }

    # create and save model to get model id
    temp_model = TestModel()
    temp_model.attributes(data)
    model_id = temp_model.save().attributes[TestModel.id_attribute]

    # define model with default find projection
    class TestModelWithDefaultFindProjection(TestModel):
      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_find_projection({
          "key1": 0
        })

    # create model
    model = TestModelWithDefaultFindProjection()

    # set target
    model.target({ TestModel.id_attribute: model_id })

    # call find
    model.find(projection = {
      "key3": 0
    }, default = True)

    # assert that default_find_projection applied to pymongo find operation
    self.assertEqual(model.attributes, {
      TestModel.id_attribute: model_id,
      "key2": "value"
    })

  def test_find_with_default_get_projection_and_argument_projection_raise_exception(self):
    """find() will raise exception ProjectionTypeMismatch if 
    default_find_projection type and keyword argument "projection" type do not 
    match
    """

    # define data
    data = {
      "key1": "value",
      "key2": "value",
      "key3": "value"
    }

    # create and save model to get model id
    temp_model = TestModel()
    temp_model.attributes(data)
    model_id = temp_model.save().attributes[TestModel.id_attribute]

    # define model with default find projection
    class TestModelWithDefaultFindProjection(TestModel):
      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_find_projection({
          "key1": 0
        })

    # create model
    model = TestModelWithDefaultFindProjection()

    # set target
    model.target({ TestModel.id_attribute: model_id })

    # assert that exception is raied
    with self.assertRaises(pymongo_basemodel.exceptions.ProjectionTypeMismatch):
      model.find(projection = {
        "key3": 1
      }, default = True)

  def test_extendable_pre_find_hook(self):
    """ find() will call extendable pre_find_hook() if defined on model
    """

    class MyModel(TestModel):
      def pre_find_hook(self):
        self.target({ "key": "value" })

    mymodel = MyModel()
    mymodel.target({ "something": "something" })
    try:
      mymodel.find()
    except:
      pass

    self.assertEqual(mymodel.target, {
      "key": "value"
    })

  def test_extendable_post_find_hook(self):
    """ find() will call extendable post_find_hook() if defined on a model
    """

    class MyModel(TestModel):
      def post_find_hook(self):
        self.target({ "key": "value" })

    mymodel = MyModel()
    mymodel.set("something", "something")
    mymodel.save()

    mymodel2 = MyModel(mymodel.get("_id"))
    mymodel2.find()

    self.assertEqual(mymodel2.target, { "key": "value" })


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
