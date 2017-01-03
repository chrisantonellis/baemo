
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo
import pymongo_basemodel

import bson
import datetime


class Test(unittest.TestCase):

  def setUp(self):
    global client, collection_name, TestModel, TestCollection
    client = pymongo.MongoClient(host = ["localhost:27017"], connect = False)
    collection_name = "%s_%s" % (self.__class__.__name__, self._testMethodName)

    class TestModel(pymongo_basemodel.core.Model):
      pymongo_collection = client["pymongo_basemodel"][collection_name]
      def __init__(self, *args, **kwargs):
        super(TestModel, self).__init__(*args, **kwargs)

  def tearDown(self):
    client["pymongo_basemodel"].drop_collection(collection_name)

  def test_insert_new(self):
    """save() inserts a document in the db consisting of the attributes of the 
    model on which it was called, if the model does not have a target and does 
    have data in its model.updates attribute
    """

    # create model
    model = TestModel()

    # set data on model
    model.set("key", "value")

    # save model
    model.save()

    # assert model is in db by manual lookup
    self.assertEqual(TestModel.pymongo_collection.find_one(), model.attributes)

  def test_protected_pre_insert_post_insert_hooks(self):
    """save() calls _pre_insert_hook() if inserting a new document which 
    generates an ObjectId and sets it on model as model.id_attribute
    """

    # create model
    model = TestModel()

    # set data on model
    model.set("key", "value")

    # save model
    model.save()

    # assert id created and set by _pre_insert_hook
    self.assertIn(model.id_attribute, model.attributes)
    self.assertEqual(type(model.attributes[model.id_attribute]), bson.objectid.ObjectId)

    # assert model.original set to model.attributes, model.updates is empty, 
    # and model.target set to generated ObjectId
    self.assertEqual(model.attributes, model.original)
    self.assertEqual(model.updates, {})
    self.assertEqual({ model.id_attribute: model.attributes[model.id_attribute] }, model.target)

  def test_target_set_changed_empty(self):
    """save() does nothing on a model with model.target set and model.updates empty
    """

    # create model
    model = TestModel()

    # set data on model
    model.set("key", "value")

    # save model
    model.save()

    # assert model.target is set
    self.assertEqual(model.target, { model.id_attribute: model.attributes[model.id_attribute] })

    # asset model.updates is empty
    self.assertEqual(model.updates, {})

    # save model again and show no exception raised
    model.save()

  def test_update(self):
    """save() updates a document in the db that matches model.target using 
    model.updates attributes in mongo operator syntax
    """

    # create and save model to load from db
    temp_model = TestModel()
    temp_model.set("key1", "value")
    model_id = temp_model.save().get(TestModel.id_attribute)

    # create model
    model1 = TestModel()
    model1.set_target(model_id)
    model1.find()

    # set data on model
    model1.set("key2", "value")

    # save model
    model1.save()

    # create another model for comparison
    model2 = TestModel()
    model2.set_target(model_id)
    model2.find()

    # assert model is in db by manual lookup
    self.assertEqual(model1.attributes, model2.attributes)

  def test_update_push_pull_iterators(self):
    """ save() will update a document correctly using the mongodb $each and $in 
    operators 
    """
    a = TestModel()
    a.save()
    a.set("key1.key2.key3", "something")
    a.push_many("key", ["value", "value", "value"])
    a.save()

    b = TestModel(a.get_target()).find()
    self.assertIn("key", b.attributes)
    self.assertEqual(b.get("key"), [
      "value", "value", "value"
    ])

  def test_update_without_find(self):
    """save() updates a document in the db that matches model.target using 
    model.updates attributes in mongo operator syntax
    """

    # create and save model to load from db
    temp_model = TestModel()
    temp_model.set("key1", "value")
    model_id = temp_model.save().get(TestModel.id_attribute)

    # create model
    model1 = TestModel()
    model1.set_target(model_id)

    # set data on model
    model1.set("key2", "value")

    # save model
    model1.save()

    model3 = TestModel(model_id)
    model3.find()

    # assert model was updated in db
    self.assertEqual(model3.get(), {
      "_id": model_id,
      "key1": "value",
      "key2": "value"
    })

  def test_protected_pre_update_post_update_hooks(self):
    """save() sets model.loaded, sets attribute to retrieved 
    """

    # create model
    model = TestModel()

    # set new data on unloaded model with target
    model.set("key", "value")

    # assert state before save
    self.assertEqual(model.target, {})
    self.assertEqual(model.original, {})
    self.assertEqual(model.updates, {
      "$set": {
        "key": "value"
      }
    })

    # save model
    model.save()

    # assert state after save
    self.assertEqual(type(model.target[model.id_attribute]), bson.objectid.ObjectId)
    self.assertEqual(model.original, {
      model.id_attribute: model.attributes[model.id_attribute],
      "key": "value"
    })
    self.assertEqual(model.updates, {})

  def test_raise_exception(self):
    """save() will raise exception ModelNotUpdated if model.target does not 
    match a document in the db and model.updates contains data
    """

    # create model
    model = TestModel()

    # manually set target to something not in the db
    model.set_target(bson.objectid.ObjectId())

    # set data on model
    model.set("key", "value")

    # manually set original
    model.original({ "key": "value" })

    # assert raises exception on save
    with self.assertRaises(pymongo_basemodel.exceptions.ModelNotUpdated):
      model.save()

  def test_delete(self):
    """save() will raise exception ModelNotDeleted if trying to delete document 
    from db by model.target that is not present in db
    """

    # create model
    model1 = TestModel()

    # save model()
    model1.save()

    # set delete flag
    model1.delete()

    # delete model
    model1.save()

    # create another model
    model2 = TestModel()

    # set model2 target to model1 target
    model2.set_target(model1.get_target())

    # assert model is deleted
    with self.assertRaises(pymongo_basemodel.exceptions.ModelNotFound):
      model2.find()

  def test_raise_exception_model_not_deleted(self):
    """save() will raise exception when trying to delete document not present 
    in db
    """

    # create model
    model1 = TestModel()

    # set data on model
    model1.set("key", "value")

    # save model
    model1.save()

    # set delete flag
    model1.delete()

    # assert delete flag is true
    self.assertEqual(model1._delete, True)

    # delete document from db
    model1.save()

    # create another model
    model2 = TestModel()

    # set model2 target to model1 target
    model2.set_target(model1.get_target())

    # set delete flag
    model2.delete()

    # assert model cannot be deleted again
    with self.assertRaises(pymongo_basemodel.exceptions.ModelNotDeleted):
      model2.save()

  def test_raise_exception_model_target_not_set(self):
    """save() will raise exception when trying to delete a document from a 
    model without a target
    """

    model = TestModel()
    model.save()
    model.target = {}
    model.delete()

    with self.assertRaises(pymongo_basemodel.exceptions.ModelTargetNotSet):
      model.save()

  def test_extendable_pre_insert_hook(self):
    """save() will run an extendable function pre_insert_hook before inserting 
    a document in the db
    """

    # define model with post insert hook
    class User(TestModel):
      def pre_insert_hook(self):
        self.set("created", datetime.datetime.today())

    # create model
    user = User()

    # save model
    user.save()

    # assert attribute saved to db
    self.assertIn("created", user.attributes)
    self.assertEqual(datetime.datetime, type(user.attributes["created"]))

  def test_extandable_post_insert_hook(self):
    """save() will run an extendable function post_insert_hook after inserting 
    a document in the db
    """

    # define model with post insert hook
    class User(TestModel):
      def post_insert_hook(self):
        self.set("full_name", "%s %s" % (self.get("first_name"), self.get("last_name")))

    # create model
    user = User()

    # set necessary data for hook to work
    user.set("first_name", "John")
    user.set("last_name", "Doe")

    # save model
    user.save()

    # assert attribute saved to db
    self.assertEqual(user.get("full_name"), "John Doe")

  def test_extendable_pre_update_hook(self):
    """save() will run an extendable function pre_update_hook before updating 
    a document in the db
    """

    # define model with pre update hook
    class User(TestModel):
      def pre_update_hook(self):
        self.set("updated", datetime.datetime.today())

    # create model
    user = User()

    # save model
    user.save()

    # assert hook not run yet
    self.assertNotIn("updated", user.attributes)

    # set data model
    user.set("key", "value")

    # update model
    user.save()

    # assert attribute saved to db
    self.assertIn("updated", user.attributes)
    self.assertEqual(datetime.datetime, type(user.attributes["updated"]))

  def test_extandable_post_update_hook(self):
    """save() will run an extendable function post_update_hook after updating 
    a document in the db
    """

    # define model with post insert hook
    class User(TestModel):
      def post_update_hook(self):
        self.set("full_name", "%s %s" % (self.get("first_name"), self.get("last_name")))

    # create model
    user = User()

    # save model
    user.save()

    # assert that hook not run yet
    self.assertNotIn("full_name", user.attributes)

    # set necessary data for hook to work
    user.set("first_name", "John")
    user.set("last_name", "Doe")

    # update model
    user.save()

    # assert attribute saved to db
    self.assertEqual(user.get("full_name"), "John Doe")

  def test_extendable_pre_delete_hook(self):
    """save() will run an extendable function pre_delete_hook before deleting a 
    document from the db
    """

    # define model with pre update hook
    class User(TestModel):
      def pre_delete_hook(self):

        # create *another* model
        inner_model = TestModel()

        # read this model's data onto inner model
        inner_model.set_target(self.get_target())
        inner_model.find()

        # if read worked, copy of outer model's data will exist
        self.set("data_copy", inner_model.get())

    # create model
    user = User()

    # set data model
    user.set("key", "value")

    # save model
    user.save()

    # assert hook not run yet
    self.assertNotIn("data_copy", user.attributes)

    # set delete flag
    user.delete()

    # delete model
    user.save()

    # assert attribute read from db before model deleted
    self.assertIn("data_copy", user.attributes)
    self.assertEqual(user.get("data_copy"), {
      user.id_attribute: user.get(user.id_attribute),
      "key": "value"
    })

    # assert model deleted so can't read data again
    temp_user = User(user.attributes[user.id_attribute])

    # assert raises exception on save
    with self.assertRaises(pymongo_basemodel.exceptions.ModelNotFound):
      temp_user.find()

  def test_extandable_post_delete_hook(self):
    """save() will run an extendable function post_delete_hook after deleting a 
    document from the db
    """

    # define model with pre update hook
    class User(TestModel):
      def post_delete_hook(self):

        # create *another* model
        inner_model = TestModel()

        # read this model's target onto another model
        inner_model.set(inner_model.id_attribute, self.get_id())

        # save inner model with target but no data
        inner_model.save()

    # create model
    user = User()

    # set data model
    user.set("key1", "value")
    user.set("key2", "value")
    user.set("key3", "value")

    # save model
    user.save()

    # set delete flag
    user.delete()

    # delete model
    user.save()

    # create another model
    temp_user = User(user.get(user.id_attribute))
    temp_user.find()

    # assert no values on model with same target as original model because
    # hook saved copy of model without data in post_delete_hook
    self.assertEqual(temp_user.attributes, {
      temp_user.id_attribute: user.get(user.id_attribute)
      })


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
  