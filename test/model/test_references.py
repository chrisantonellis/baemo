
import sys
sys.path.extend([ "../", "../../" ])

import bson
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

  def tearDown(self):
    client["pymongo_basemodel"].drop_collection(collection_name)
  

  def test_dereference_one_to_one_local(self):
    """deference_nested_models will resolve a one to one relationship defined 
    in self.relationships with local_key and foreign_key defined
    """

    # define class with one to one local relationship
    class User(TestModel):
      def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

        # define one to one local relationship
        self.relationships = {
          "partner": {
            "type": "one_to_one",
            "model": User,
            "local_key": "partner",
            "foreign_key": User.id_attribute
          }
        }

    # create model
    user1 = User()
    user1.set("key", "value")

    # create another model
    user2 = User()
    user2.set("key", "value")
    user2.save()

    # set relationship on model
    user1.set("partner", user2.get_id())

    # save model
    user1.save()

    # load from db and resolve relationship
    user3 = User(user1.get_id()).find(projection = {
      "partner": 2
    })

    # assert resolved relationship
    self.assertEqual(type(user3.attributes["partner"]), User)
    self.assertEqual(user3.get("partner._id"), user2.get("_id"))

  def test_dereference_one_to_one_local_with_projection(self):
    """deference_nested_models will resolve a one to one relationship defined 
    in self.relationships with local_key and foreign_key defined and apply 
    projection passed
    """

    # define class with one to one local relationship
    class User(TestModel):
      def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

        # define one to one local relationship
        self.relationships = {
          "partner": {
            "type": "one_to_one",
            "model": User,
            "local_key": "partner",
            "foreign_key": User.id_attribute
          }
        }

    # create model
    user1 = User()
    user1.set("key", "value")

    # create another model
    user2 = User()
    user2.set("key", "value")
    user2.save()

    # set relationship on model
    user1.set("partner", user2.get_id())

    # save model
    user1.save()

    # load from db and resolve relationship
    user3 = User(user1.get_id()).find(projection = {
      "partner": {
        "key": 0
      }
    })

    # assert resolved relationship
    self.assertEqual(type(user3.attributes["partner"]), User)
    self.assertEqual(user3.get("partner._id"), user2.get("_id"))
    self.assertEqual(user3.get("partner"), {
      "_id": user2.get("_id")
    })

  def test_dereference_one_to_one_without_local_key(self):
    """deference_nested_models will resolve a one to one relationship defined 
    in self.relationships with local_key undefined and foreign_key defined
    """

    # define class with one to one local relationship
    class User(TestModel):
      def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

        # define one to one local relationship
        self.relationships = {
          "partner": {
            "type": "one_to_one",
            "model": User,
            "foreign_key": User.id_attribute
          }
        }

    # create model
    user1 = User()
    user1.set("key", "value")

    # create another model
    user2 = User()
    user2.set("key", "value")
    user2.save()

    # set relationship on model
    user1.set("partner", user2.get_id())

    # save model
    user1.save()

    # load from db and resolve relationship
    user3 = User(user1.get_id()).find(projection = {
      "partner": 2
    })

    # assert resolved relationship
    self.assertEqual(type(user3.attributes["partner"]), User)
    self.assertEqual(user3.get("partner._id"), user2.get("_id"))

  def test_dereference_one_to_one_local_without_foreign_key(self):
    """deference_nested_models will resolve a one to one relationship defined 
    in self.relationships with local_key defined and foreign_key undefined
    """

    # define class with one to one local relationship
    class User(TestModel):
      def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

        # define one to one local relationship
        self.relationships = {
          "partner": {
            "type": "one_to_one",
            "model": User,
            "local_key": "partner"
          }
        }

    # create model
    user1 = User()
    user1.set("key", "value")

    # create another model
    user2 = User()
    user2.set("key", "value")
    user2.save()

    # set relationship on model
    user1.set("partner", user2.get_id())

    # save model
    user1.save()

    # load from db and resolve relationship
    user3 = User(user1.get_id()).find(projection = {
      "partner": 2
    })

    # assert resolved relationship
    self.assertEqual(type(user3.attributes["partner"]), User)
    self.assertEqual(user3.get("partner._id"), user2.get("_id"))

  def test_dereference_many_to_one_local(self):
    """deference_nested_models will resolve a many to one relationship defined 
    in self.relationships with relationship identifier defined on local model
    """

    # define class with one to one local relationship
    class User(TestModel):
      def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

        # define one to one local relationship
        self.relationships = {
          "partner": {
            "type": "many_to_one",
            "model": User,
            "local_key": "partner",
            "foreign_key": User.id_attribute
          }
        }

    # create model
    user1 = User()
    user1.set("key", "value")

    # create another model
    user2 = User()
    user2.set("key", "value")
    user2.save()

    # set relationship on model
    user1.set("partner", user2.get_id())

    # save model
    user1.save()

    # load from db and resolve relationship
    user3 = User(user1.get_id()).find(projection = {
      "partner": 2
    })

    # assert resolved relationship
    self.assertEqual(type(user3.attributes["partner"]), User)
    self.assertEqual(user3.get("partner._id"), user2.get("_id"))

  def test_dereference_one_to_one_foreign(self):
    """deference_nested_models will resolve a one to one relationship defined 
    in self.relationships with relationship identifier defined on foreign model
    """

    # define class with one to one local relationship
    class User(TestModel):
      def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

        # define one to one foreign relationship
        self.relationships = {
          "partner": {
            "type": "one_to_one",
            "model": User,
            "local_key": User.id_attribute,
            "foreign_key": "partner"
          }
        }

    # create model
    user1 = User()
    user1.set("key", "value")

    # create another model
    user2 = User()
    user2.set("key", "value")
    user2.save()

    # set relationship on model
    user1.set("partner", user2.get_id())

    # save model
    user1.save()

    # load from db and resolve relationship
    user3 = User(user2.get_id()).find(projection = {
      "partner": 2
    })

    # assert resolved relationship
    self.assertEqual(type(user3.attributes["partner"]), User)
    self.assertEqual(user3.get("partner._id"), user1.get("_id"))

  def test_dereference_one_to_one_foreign_with_projection(self):
    """deference_nested_models will resolve a one to one relationship defined 
    in self.relationships with relationship identifier defined on foreign model 
    and apply projection passed
    """

    # define class with one to one local relationship
    class User(TestModel):
      def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

        # define one to one foreign relationship
        self.relationships = {
          "partner": {
            "type": "one_to_one",
            "model": User,
            "local_key": User.id_attribute,
            "foreign_key": "partner"
          }
        }

    # create model
    user1 = User()
    user1.set("key1", "value")
    user1.set("key2", "value")
    user1.set("key3", "value")

    # create another model
    user2 = User()
    user2.set("key", "value")
    user2.save()

    # set relationship on model
    user1.set("partner", user2.get_id())

    # save model
    user1.save()

    # load from db and resolve relationship
    user3 = User(user2.get_id()).find(projection = {
      "partner": {
        "key2": 1
      }
    })

    # assert resolved relationship
    self.assertEqual(type(user3.attributes["partner"]), User)
    self.assertEqual(user3.get("partner._id"), user1.get("_id"))
    self.assertEqual(user3.get("partner"), {
      "_id": user1.get("_id"),
      "key2": "value"
    })

  def test_dereference_many_to_one_foreign(self):
    """deference_nested_models will resolve a many to one relationship defined 
    in self.relationships with relationship identifier defined on foreign model
    """

    # define class with one to one local relationship
    class User(TestModel):
      def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

        # define one to one foreign relationship
        self.relationships = {
          "partner": {
            "type": "many_to_one",
            "model": User,
            "local_key": User.id_attribute,
            "foreign_key": "partner"
          }
        }

    # create model
    user1 = User()
    user1.set("key", "value")

    # create another model
    user2 = User()
    user2.set("key", "value")
    user2.save()

    # set relationship on model
    user1.set("partner", user2.get_id())

    # save model
    user1.save()

    # load from db and resolve relationship
    user3 = User(user2.get_id()).find(projection = {
      "partner": 2
    })

    # assert resolved relationship
    self.assertEqual(type(user3.attributes["partner"]), User)
    self.assertEqual(user3.get("partner._id"), user1.get("_id"))

  def test_dereference_one_to_one_local_relationship_resolution_error(self):
    """deference_nested_models will resolve a one to one relationship defined 
    in self.relationships with a relationship resolution error if defined 
    document is not found
    """

    # define class with one to one local relationship
    class User(TestModel):
      def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

        # define one to one foreign relationship
        self.relationships = {
          "partner": {
            "type": "one_to_one",
            "model": User,
            "local_key": "partner",
            "foreign_key": User.id_attribute
          }
        }

    # create model
    user1 = User()

    # create another model
    user2 = User()
    user2.save()

    # set relationship on model
    user1.set("partner", user2.get_id())

    # save model
    user1.save()

    # delete relationship model to create error
    user2.delete()
    user2.save()

    # load from db and resolve relationship
    user3 = User(user1.get_id()).find(projection = {
      "partner": 2
    })

    # assert relationship_resolution_error
    self.assertEqual(type(user3.attributes["partner"]), pymongo_basemodel.exceptions.RelationshipResolutionError)

  def test_dereference_one_to_one_foreign_relationship_resolution_error(self):
    """deference_nested_models will resolve a one to one relationship defined 
    in self.relationships with None if no documents matching relationship 
    are found
    """

    # define class with one to one local relationship
    class User(TestModel):
      def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

        # define one to one foreign relationship
        self.relationships = {
          "partner": {
            "type": "one_to_one",
            "model": User,
            "local_key": User.id_attribute,
            "foreign_key": "partner"
          }
        }

    # create model
    user1 = User()
    user1.save()

    # attempt to resolve relationship
    user2 = User(user1.get("_id"))
    user2.find(projection = {
      "partner": 2
    })

    # assert that relationship value is None
    self.assertEqual(user2.get("partner"), None)

  def test_reference_basic(self):
    """reference_nested_models will call get_id() on nestd models to format 
    model data for saving to the db
    """

    # create model
    user1 = TestModel()

    # create another model
    user2 = TestModel()
    user2.save()

    # set relationship on model as a model
    user1.set("partner", user2)

    # save model
    user1.save()

    # load from db and resolve relationship
    user3 = TestModel(user1.get_id()).find()

    # assert model was converted to reference during save
    self.assertEqual(type(user3.attributes["partner"]), bson.objectid.ObjectId)
    self.assertEqual(user3.get("partner"), user2.get("_id"))



if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)