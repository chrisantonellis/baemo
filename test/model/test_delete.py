
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

  def test_set_delete(self):
    """ delete sets model._delete to True
    """

    # create model
    model = TestModel()

    # assert delete flag is not set on instantiation
    self.assertEqual(model._delete, False)

    # set delete flag
    model.delete()

    # assert delete flag set on model
    self.assertEqual(model._delete, True)

  def test_cascade_nested_model_simple(self):
    """ delete will cascade setting model._delete to True for nested models 
    if keyword argument 'cascade' is set to True
    """

    # create parent model
    parent_model = TestModel()

    # create child model
    child_model = TestModel()

    # set child model as attribute of parent model
    parent_model.set("child", child_model)

    # cascade delete flag on nested models
    parent_model.delete(cascade = True)

    # assert delete flag set on parent model
    self.assertEqual(parent_model._delete, True)

    # assert delete flag set on child model
    self.assertEqual(child_model._delete, True)

  def test_cascade_nested_model_advanced(self):
    """ delete will cascade setting model._delete to True for nested models if 
    keyword argument 'cascade' is set to True
    """

    # create parent model
    parent_model = TestModel()

    # create child model
    child_model = TestModel()

    # set child model as attribute of parent model
    parent_model.set("children.first_born", child_model)

    # cascade delete flag on nested models
    parent_model.delete(cascade = True)

    # assert delete flag set on parent model
    self.assertEqual(parent_model._delete, True)

    # assert delete flag set on child model
    self.assertEqual(child_model._delete, True)
    

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)