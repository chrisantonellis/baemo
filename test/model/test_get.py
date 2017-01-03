
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_get_value_not_set(self):
    """ get returns Undefined if value being retrieved is not set in 
    model.attributes
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # assert None returned for key not set on model
    self.assertEqual(
      type(a.get("key")),
      pymongo_basemodel.core.Undefined
    )

  def test_get_all_attributes(self):
    """ get returns a dict of all model attributes if called with no args
    """

    # define data
    data = {
      "color": "red",
      "info": {
        "previous_owners": [{
          "name": "John Doe"
        },{
          "name": "Paul Bunyan"
        }],
        "current_owners": [{
          "name": "Jane Doe"
        },{
          "name": "Paula Bunyan"
        }]
      },
      "engine": {
        "cylinders": 8
      }
    }

    # create model
    a = pymongo_basemodel.core.Model()

    # set model attributes to data
    a.attributes(data)

    self.assertEqual(a.get(), data)

  def test_get_default_projection_dot_notation_syntax(self):
    """ get returns a dit of model attribtues with default_get_projection 
    applied
    """

    # define model with default get projection
    class TestModel(pymongo_basemodel.core.Model):
      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_get_projection({
          "password": 1,
          "key1.key2": 1
        })

    # create model
    a = TestModel()

    # set model attributes
    a.attributes({
      "password": "1234",
      "key1": {
        "key2": "value",
        "key3": "value"
      }
    })


    # assert default_get_projection applied to attributes
    self.assertEqual(a.get(), {
      "password": "1234",
      "key1": {
        "key2": "value"
      }
    })

  def test_get_inclusive_default_get_projection(self):
    """ get returns a dict of model attributes with inclusive 
    default_get_projection applied
    """

    # define model with default get projection
    class TestModel(pymongo_basemodel.core.Model):
      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_get_projection ({
          "password": 1
        })

    # create model
    a = TestModel()

    # set model attributes
    a.attributes({
      "key": "value",
      "password": "1234"
    })

    # assert default_get_projection applied to attributes
    self.assertEqual(a.get(), {
      "password": "1234"
    })

  def test_get_inclusive_default_get_projection_and_keyword_argument_projection(self):
    """ get returns a dict of model attribtues with inclusive 
    default_get_projection and keyword arguemtn "projection" applied
    """

    # define model with default get projection
    class TestModel(pymongo_basemodel.core.Model):
      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_get_projection({
          "password": 1
        })

    # create model
    a = TestModel()

    # set model attributes
    a.attributes({
      "key1": "value",
      "key2": "value",
      "password": "1234"
    })

    # assert default_get_projection applied to attributes
    self.assertEqual(a.get(projection = {
      "key1": 1
    }, default = True), {
      "password": "1234",
      "key1": "value"
    })

  def test_get_exclusive_default_get_projection(self):
    """ get returns a dict of model attributes with exclusive
    default_get_projection applied
    """

    # define model with default get projection
    class TestModel(pymongo_basemodel.core.Model):
      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_get_projection({
          "password": 0
        })

    # create model
    a = TestModel()

    # set model attributes
    a.attributes({
      "key": "value",
      "password": "1234"
    })

    # assert default_get_projection applied to attributes
    self.assertEqual(a.get(), {
      "key": "value"
    })

  def test_get_exclusive_default_get_projection_and_keyword_argument_projection(self):
    """ get returns a dict of model attribtues with exclusive
    default_get_projection and keyword argument "projection" applied
    """

    # define model with default get projection
    class TestModel(pymongo_basemodel.core.Model):
      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_get_projection({
          "password": 0
        })

    # create model
    a = TestModel()

    # set model attributes
    a.attributes({
      "key1": "value",
      "key2": "value",
      "password": "1234"
    })

    # assert default_get_projection applied to attributes
    self.assertEqual(a.get(projection = {
      "key1": 0
    }, default = True), {
      "key2": "value"
    })

  def test_get_attribute_by_string(self):
    """get() returns the value of a model attribute when passed the key name
    of that attribute as a string
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # set model attributes
    a.attributes({
      "key1": "value1",
      "key2": "value2",
      "key3": "value3"
    })

    # assert default_get_projection applied to attributes
    self.assertEqual(a.get("key2"), "value2")

  def test_get_attribyute_by_dot_notation_syntax_string(self):
    """get() returns the value of a nested model attribute when passed the key 
    name of that attribute as a dot notation syntax string
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # set model attributes
    a.attributes({
      "key1": {
        "key2": "value"
      }
    })

    # assert default_get_projection applied to attributes
    self.assertEqual(a.get("key1.key2"), "value")

  def test_get_all_attributes_with_nested_model(self):
    """ get returns the value of a model attribute when passed the key name
    of that attribute as a string
    """

    # create child model
    child_model = pymongo_basemodel.core.Model()

    # set child model attributes
    child_model.attributes({
      "key": "child_model_value"
    })

    # create parent model
    parent_model = pymongo_basemodel.core.Model()

    # set parent model attributes
    parent_model.attributes({
      "key": "parent_model_value",
      "child_model": child_model
    })

    # assert default_get_projection applied to attributes
    self.assertEqual(parent_model.get(), {
      "key": "parent_model_value",
      "child_model": {
        "key": "child_model_value"
      }
    })

  def test_get_attribute_of_nested_model_by_dot_notation_syntax_string(self):
    """ get returns the value of an attribute of a nested model when passed 
    the key name of that attribute as a dot notation syntax string
    """

    # create child model
    child_model = pymongo_basemodel.core.Model()

    # set child model attributes
    child_model.attributes({
      "key": "child_model_value"
    })

    # create parent model
    parent_model = pymongo_basemodel.core.Model()

    # set parent model attributes
    parent_model.attributes({
      "key": "parent_model_value",
      "child_model": child_model
    })

    # assert default_get_projection applied to attributes
    self.assertEqual(parent_model.get("child_model.key"), "child_model_value")

  def test_get_all_attributes_with_nested_model_with_projection(self):
    """get() returns the attributes of a model and the attributes of nested 
    models with a projection applied
    """

    # create child model
    child_model = pymongo_basemodel.core.Model()

    # set child model attributes
    child_model.attributes({
      "key1": "child_model_value1",
      "key2": "child_model_value2"
    })

    # create parent model
    parent_model = pymongo_basemodel.core.Model()

    # set parent model attributes
    parent_model.attributes({
      "key1": "parent_model_value1",
      "key2": "child_model_value2",
      "child_model": child_model
    })

    # assert default_get_projection applied to attributes
    self.assertEqual(parent_model.get(projection = {
      "key2": 0,
      "child_model": {
        "key1": 0
      }
    }), {
      "key1": "parent_model_value1",
      "child_model": {
        "key2": "child_model_value2"
      }
    })

  def test_get_handle_relationship_resolution_error(self):
    """ get returns a flattened version of RelationshipResolutionError if 
    found when resolving attributes
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # set model attributes with relationship resolution error
    a.attributes({
      "key1": {
        "key2": "value",
        "friend": pymongo_basemodel.exceptions.RelationshipResolutionError(data = {
          "key": "value"
        })
      }
    })

    self.assertEqual(a.get("key1.friend"), {
      "message": "Relationship resolution error",
      "data": {
        "key": "value"
      }
    })


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
  