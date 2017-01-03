
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

  def test_computed_attributes(self):
    """ computed_attributes will be merged with model.attributes on 
    get non destructively
    """

    class TestModelWithComputedAttributes(TestModel):
      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.computed_attributes({
          "key": "value"
        })

    # create model without target
    model = TestModelWithComputedAttributes()

    self.assertEqual({}, model.attributes)
    self.assertEqual({ "key": "value" }, model.get())
    self.assertEqual({}, model.attributes)

  def test_computed_attributes_callable(self):
    """ computed_attributes values will be called if callable and merged with 
    model.attributes on get 
    """

    class TestModelWithComputedAttributes(TestModel):
      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.computed_attributes({
          "key": lambda: datetime.datetime.today()
        })

    # create model without target
    model = TestModelWithComputedAttributes()

    self.assertEqual({}, model.attributes)
    self.assertIn("key", model.get())
    self.assertIsInstance(model.get("key"), datetime.datetime)
    self.assertEqual({}, model.attributes)

  def test_computed_attributes_callable_raise_exception(self):
    """ computed_attributes values will be called if callable and not merged 
    with model.attributes on get if exception raised
    """

    class TestModelWithComputedAttributes(TestModel):
      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.computed_attributes({
          "key": lambda: 0/0
        })

    # create model without target
    model = TestModelWithComputedAttributes()
    self.assertEqual({}, model.attributes)
    self.assertEqual({}, model.get())


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
  