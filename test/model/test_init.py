
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class TestInit(unittest.TestCase):

  def test_init(self):
    """__init__ returns an instantiated model with correct default attributes 
    set
    """

    model = pymongo_basemodel.core.Model()

    self.assertEqual(model.id_attribute, "_id")
    self.assertEqual(model.pymongo_collection, None)

    self.assertEqual(type(model.target), pymongo_basemodel.core.DotNotationContainer)
    self.assertEqual(type(model.attributes), pymongo_basemodel.core.DotNotationContainer)
    self.assertEqual(type(model.relationships), pymongo_basemodel.core.DotNotationContainer)
    self.assertEqual(type(model.default_attributes), pymongo_basemodel.core.DotNotationContainer)
    self.assertEqual(type(model.computed_attributes), pymongo_basemodel.core.DotNotationContainer)

    self.assertEqual(type(model.default_find_projection), pymongo_basemodel.core.Projection)
    self.assertEqual(type(model.default_get_projection), pymongo_basemodel.core.Projection)

    self.assertEqual(model._delete, False)
    self.assertEqual(type(model.original), pymongo_basemodel.core.DotNotationContainer)
    self.assertEqual(type(model.updates), pymongo_basemodel.core.DotNotationContainer)


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestInit)
  unittest.TextTestRunner().run(suite)
