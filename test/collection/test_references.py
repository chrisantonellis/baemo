
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
        super().__init__(*args, **kwargs)

    class TestCollection(pymongo_basemodel.core.Collection):
      model = TestModel
      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

  def tearDown(self):
    client["pymongo_basemodel"].drop_collection(collection_name)


  def test_dereference_one_to_many_local(self):
    """deference_nested_models will resolve a one to many relationship defined 
    in self.relationships on local model
    """

    # define class with one to many local relationship
    class User(TestModel):
      def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

        # define one to one local relationship
        self.relationships = {
          "partners": {
            "type": "one_to_many",
            "model": Users,
            "local_key": "partners",
            "foreign_key": User.id_attribute
          }
        }

    class Users(TestCollection):
      model = User

    # create model
    user1 = User()
    user1.save()

    # create another model
    user2 = User()
    user2.save()

    # create model, set relationship, and save
    user3 = User()
    user3.set("partners", [ user1.get("_id"), user2.get("_id") ])
    user3.save()

    # create another model and find by id of model with relationship
    user4 = User(user3.get("_id"))

    # assert no attributes before find
    self.assertEqual(user4.attributes, {})

    user4.find(projection = {
      "partners": 2
    })

    # assert relationship resolved
    self.assertEqual(type(user4.attributes["partners"]), Users)
    for user in user4.attributes["partners"]:
      self.assertEqual(type(user), User)

  def test_dereference_one_to_many_local_with_projection(self):
    """deference_nested_models will resolve a one to many relationship defined 
    in self.relationships on local model and pass forward projection
    """

    # define class with one to many local relationship
    class User(TestModel):
      def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

        # define one to one local relationship
        self.relationships = {
          "partners": {
            "type": "one_to_many",
            "model": Users,
            "local_key": "partners",
            "foreign_key": User.id_attribute
          }
        }

    class Users(TestCollection):
      model = User

    # create model
    user1 = User()
    user1.set("key1", "value")
    user1.set("key2", "value")
    user1.set("key3", "value")
    user1.save()

    # create another model
    user2 = User()
    user2.set("key1", "value")
    user2.set("key2", "value")
    user2.set("key3", "value")
    user2.save()

    # create model, set relationship, and save
    user3 = User()
    user3.set("partners", [ user1.get("_id"), user2.get("_id") ])
    user3.save()

    # create another model and find by id of model with relationship
    user4 = User(user3.get("_id"))

    # assert no attributes before find
    self.assertEqual(user4.attributes, {})

    user4.find(projection = {
      "partners": {
        "key2": 0
      }
    })

    # assert relationship resolved
    self.assertEqual(type(user4.attributes["partners"]), Users)
    for user in user4.attributes["partners"]:
      self.assertEqual(user.get(), {
          "_id": user.get("_id"),
          "key1": "value",
          "key3": "value"
        })

  def test_dereference_one_to_many_local_relationship_resolution_error(self):
    """deference_nested_models will reeturn a relationship resolution error for 
    any models not found when trying to resolve one to many local relationship
    """

    # define class with one to many local relationship
    class User(TestModel):
      def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

        # define one to one local relationship
        self.relationships = {
          "partners": {
            "type": "one_to_many",
            "model": Users,
            "local_key": "partners",
            "foreign_key": User.id_attribute
          }
        }

    class Users(TestCollection):
      model = User

    # create model
    user1 = User()
    user1.save()

    # create model, set relationship, and save
    user3 = User()
    user3.set("partners", [ user1.get("_id") ])
    user3.save()

    # delete referenced model
    user1.delete()
    user1.save()

    # create another model and find by id of model with relationship
    user4 = User(user3.get("_id"))

    # assert no attributes before find
    self.assertEqual(user4.attributes, {})

    user4.find(projection = {
      "partners": 2
    })

    # assert relationship resolved
    self.assertEqual(type(user4.attributes["partners"]), Users)
    for user in user4.attributes["partners"]:
      self.assertEqual(type(user), pymongo_basemodel.exceptions.RelationshipResolutionError)

  def test_dereference_many_to_many_local(self):
    """deference_nested_models will resolve a many to many relationship defined 
    in self.relationships on local model
    """

    # define class with one to many local relationship
    class User(TestModel):
      def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

        # define one to one local relationship
        self.relationships = {
          "partners": {
            "type": "many_to_many",
            "model": Users,
            "local_key": "partners",
            "foreign_key": User.id_attribute
          }
        }

    class Users(TestCollection):
      model = User

    # create model
    user1 = User()
    user1.save()

    # create another model
    user2 = User()
    user2.save()

    # create model, set relationship, and save
    user3 = User()
    user3.set("partners", [ user1.get("_id"), user2.get("_id") ])
    user3.save()

    # create another user to actually make it a many to many
    temp_user = User()
    temp_user.set("partners", [ user1.get("_id") ])
    temp_user.save()

    # create another model and find by id of model with relationship
    user4 = User(user3.get("_id"))

    # assert no attributes before find
    self.assertEqual(user4.attributes, {})

    user4.find(projection = {
      "partners": 2
    })

    # assert relationship resolved
    self.assertEqual(type(user4.attributes["partners"]), Users)
    for user in user4.attributes["partners"]:
      self.assertEqual(type(user), User)

  def test_dereference_one_to_many_foreign(self):
    """deference_nested_models  will resolve a one to many relationship defined 
    in self.relationships with data on foreign models
    """

    # define class with one to many local relationship
    class User(TestModel):
      def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

        # define one to one local relationship
        self.relationships = {
          "employees": {
            "type": "one_to_many",
            "model": Users,
            "local_key": User.id_attribute,
            "foreign_key": "manager"
          }
        }

    class Users(TestCollection):
      model = User

    # create model
    manager = User()
    manager.save()

    # create model with relationship
    employee1 = User()
    employee1.set("manager", manager.get(manager.id_attribute))
    employee1.save()

    # create another model with relationship
    employee2 = User()
    employee2.set("manager", manager.get(manager.id_attribute))
    employee2.save()

    # create another model and resolve relationship
    manager2 = User(manager.get(manager.id_attribute))
    manager2.find(projection = {
      "employees": 2
    })

    # assert relationship resolved with models
    self.assertEqual(type(manager2.attributes["employees"]), Users)
    for user in manager2.attributes["employees"]:
      self.assertEqual(type(user), User)

  def test_dereference_one_to_many_foreign_with_projection(self):
    """deference_nested_models() will resolve a one to many relationship defined 
    in self.relationships with data on foreign models and pass forward 
    projection
    """

    # define class with one to many local relationship
    class User(TestModel):
      def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

        # define one to one local relationship
        self.relationships = {
          "employees": {
            "type": "one_to_many",
            "model": Users,
            "local_key": User.id_attribute,
            "foreign_key": "manager"
          }
        }

    class Users(TestCollection):
      model = User

    # create model
    manager = User()
    manager.set("key1", "value")
    manager.set("key2", "value")
    manager.set("key3", "value")
    manager.save()

    # create model with relationship
    employee1 = User()
    employee1.set("manager", manager.get(manager.id_attribute))
    employee1.set("key1", "value")
    employee1.set("key2", "value")
    employee1.set("key3", "value")
    employee1.save()

    # create another model with relationship
    employee2 = User()
    employee2.set("manager", manager.get(manager.id_attribute))
    employee2.set("key1", "value")
    employee2.set("key2", "value")
    employee2.set("key3", "value")
    employee2.save()

    # create another model and resolve relationship
    manager2 = User(manager.get(manager.id_attribute))
    manager2.find(projection = {
      "employees": {
        "key1": 1,
        "key2": 1
      }
    })

    # assert relationship resolved with models
    self.assertEqual(type(manager2.attributes["employees"]), Users)
    for user in manager2.attributes["employees"]:
      self.assertEqual(user.get(), {
          "_id": user.get("_id"),
          "key1": "value",
          "key2": "value"
        })

  def test_dereference_many_to_many_foreign(self):
    """deference_nested_models  will resolve a many to many relationship defined 
    in self.relationships with data on foreign models
    """

    # define class with one to many local relationship
    class User(TestModel):
      def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

        # define one to one local relationship
        self.relationships = {
          "employees": {
            "type": "many_to_many",
            "model": Users,
            "local_key": User.id_attribute,
            "foreign_key": "manager"
          }
        }

    class Users(TestCollection):
      model = User

    # create model
    manager = User()
    manager.save()

    # create another model
    temp_manager = User()
    temp_manager.save()

    # create model with relationship
    employee1 = User()
    employee1.set("manager", manager.get(manager.id_attribute))
    employee1.save()

    # create another model with relationship
    employee2 = User()
    employee2.set("manager", [
      manager.get(manager.id_attribute),
      temp_manager.get(temp_manager.id_attribute)
    ])
    employee2.save()

    # create another model and resolve relationship
    manager2 = User(manager.get(manager.id_attribute))
    manager2.find(projection = {
      "employees": 2
    })

    self.assertEqual(type(manager2.attributes["employees"]), Users)
    for user in manager2.attributes["employees"]:
      self.assertEqual(type(user), User)

  def test_dereference_many_to_many_foreign_with_projection(self):
    """deference_nested_models will resolve a many to many relationship defined 
    in self.relationships with data on foreign models and pass forward 
    projection
    """

    # define class with one to many local relationship
    class User(TestModel):
      def __init__(self, *args, **kwargs):
        super(User, self).__init__(*args, **kwargs)

        # define one to one local relationship
        self.relationships = {
          "employees": {
            "type": "many_to_many",
            "model": Users,
            "local_key": User.id_attribute,
            "foreign_key": "manager"
          }
        }

    class Users(TestCollection):
      model = User

    # create model
    manager = User()
    manager.save()

    # create another model
    temp_manager = User()
    temp_manager.save()

    # create model with relationship
    employee1 = User()
    employee1.set("manager", [
      manager.get(manager.id_attribute)
    ])
    employee1.set("key1", "value")
    employee1.set("key2", "value")
    employee1.set("key3", "value")
    employee1.save()

    # create another model with relationship
    employee2 = User()
    employee2.set("manager", [
      manager.get(manager.id_attribute),
      temp_manager.get(temp_manager.id_attribute)
    ])
    employee2.set("key1", "value")
    employee2.set("key2", "value")
    employee2.set("key3", "value")
    employee2.save()

    # create another model and resolve relationship
    manager2 = User(manager.get(manager.id_attribute))

    manager2.find()

    manager2.find(projection = {
      "employees": {
        "key1": 1
      }
    })

    self.assertEqual(type(manager2.attributes["employees"]), Users)
    for user in manager2.attributes["employees"]:
      self.assertEqual(user.get(), {
          "_id": user.get("_id"),
          "key1": "value"
        })

  def test_reference_basic(self):
    """reference_nested_models will call get_target() on nested models to format 
    model data for saving to the db
    """

    # create model
    user1 = TestModel()
    user1.save()

    # create another model
    user2 = TestModel()
    user2.save()

    # create collection
    users = TestCollection()
    users.add(user1)
    users.add(user2)

    # create another model
    user3 = TestModel()
    user3.set("group", users)

    # convert nested models to references
    data = user3.reference_nested_models()

    # assert that models were converted to references
    self.assertIn("group", data)
    for value in data["group"]:
      self.assertEqual(type(value), bson.objectid.ObjectId)


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)