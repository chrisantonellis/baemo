
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_set_target_by_string(self):
    """when the argument is a string, set_target() sets model.target to a dict
    with model.id_attribute as the key and the argument string as the value
    """

    # create model
    model = pymongo_basemodel.core.Model()

    # assert target set with id attribute when received as string
    model.set_target("target")
    self.assertEqual(model.target, { model.id_attribute: "target" })

  def test_set_target_by_dict(self):
    """when the argument is a dict, set_target() sets model.target to the
    argument dict
    """

    # create model
    model = pymongo_basemodel.core.Model()

    # assert target set when received as dict
    model.set_target({ "_id": "target" })
    self.assertEqual(model.target, { "_id": "target" })

  def test_set_target_on_instantiation_by_string_positional_argument(self):
    """when a model is instantianted with a string as the first positional 
    argument, set_target() set model.target to a dict with model.id_Attribute 
    as the key and the argument string as the value
    """

    # create model
    model = pymongo_basemodel.core.Model("target")

    # assert target set
    self.assertEqual(model.target, { model.id_attribute: "target" })

  def test_set_target_on_instantiation_by_dict_positional_argument(self):
    """when a model is instantiated with a dict as the first positional 
    argument, set_target() sets model.target to the argument dict
    """
  
    # create model
    model = pymongo_basemodel.core.Model({ "id_key": "target" })

    # assert target set
    self.assertEqual(model.target, { "id_key": "target" })

  def test_get_target(self):
    """get_target() returns a value that represents the model for use in 
    referencing nested model relationships
    """

    # create model
    model = pymongo_basemodel.core.Model()
    model.set_target("target")

    # assert target returned
    self.assertEqual(model.get_target(), { "_id": "target" })

  def test_get_target_not_set(self):
    """get_target() raises exception ModelTargetNotSet if called on model with
    model.target not set
    """

    # create another model
    model = pymongo_basemodel.core.Model()

    # assert exception raised when target not set
    self.assertEqual(model.get_target(), None)

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)