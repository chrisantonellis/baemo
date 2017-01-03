
import sys
sys.path.extend([ "../", "../../" ])

import pymongo
import unittest
import pymongo_basemodel
import datetime


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

  def test_default_attributes(self):
    """ default_attributes will be merged with model.attributes on 
    save if save results in insert operation and "default" is True
    """

    class TestModelWithDefaultAttributes(TestModel):
      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_attributes({
          "key": "value"
        })

    # create model without target
    model = TestModelWithDefaultAttributes()

    # save model
    model.save()

    # assert default attributes applied
    self.assertIn("key", model.attributes)
    self.assertEqual(model.attributes["key"], "value")

  def test_default_attributes_callable(self):
    """ default_attributes values will be called if callable and merged with 
    model.attributes on save
    """

    class TestModelWithDefaultAttributes(TestModel):
      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_attributes({
          "key": lambda: datetime.datetime.today()
        })

    # create model without target
    model = TestModelWithDefaultAttributes()

    # save model
    model.save()

    # assert default attributes applied
    self.assertIn("key", model.attributes)
    self.assertIsInstance(model.attributes["key"], datetime.datetime)

  def test_default_attributes_callable_raise_exception(self):
    """ default_attributes values will be called if callable and exceptions 
    will not be caught if raised
    """

    class TestModelWithDefaultAttributes(TestModel):
      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_attributes({
          "key": lambda: 0/0
        })

    # create model without target
    model = TestModelWithDefaultAttributes()

    with self.assertRaises(ZeroDivisionError):
      model.save()

  def test_default_false(self):
    """ default_attributes will not be merged with model.attributes on 
    save if save results in insert operation and "default" is False
    """

    class TestModelWithDefaultAttributes(TestModel):
      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_attributes({
          "key": "value"
        })

    # create model without target
    model = TestModelWithDefaultAttributes()

    # save model
    model.save(default = False)

    # assert default attributes applied
    self.assertNotIn("key", model.attributes)

  def test_inherit_overwrite(self):
    """ default_attributes will be merged parent model default_attributes 
    on insantiation if merge method is used
    save if save results in insert operation and "default" is True
    """

    class TestModelWithDefaultAttributesParent(TestModel):
      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_attributes({
          "key1": "value"
        })

    class TestModelWithDefaultAttributesChild(TestModelWithDefaultAttributesParent):
      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_attributes({
          "key2": "value"
        })

    # create model without target
    model = TestModelWithDefaultAttributesChild()

    # save model
    model.save()

    # assert default attributes applied
    self.assertNotIn("key1", model.attributes)
    self.assertIn("key2", model.attributes)
    self.assertEqual(model.attributes["key2"], "value")

  def test_inherit_merge(self):
    """ default_attributes will be merged parent model default_attributes 
    on insantiation if merge method is used
    save if save results in insert operation and "default" is True
    """

    class TestModelWithDefaultAttributesParent(TestModel):
      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_attributes({
          "key1": "value"
        })

    class TestModelWithDefaultAttributesChild(TestModelWithDefaultAttributesParent):
      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_attributes.merge({
          "key2": "value"
        })

    # create model without target
    model = TestModelWithDefaultAttributesChild()

    # save model
    model.save()

    # assert default attributes applied
    self.assertIn("key1", model.attributes)
    self.assertIn("key2", model.attributes)
    self.assertEqual(model.attributes["key1"], "value")
    self.assertEqual(model.attributes["key2"], "value")


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
  