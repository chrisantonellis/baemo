
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class TestInit(unittest.TestCase):

  def test_init(self):
    """ __init__ returns a reference to an instantiated DotNotationContainer 
    """

    c = pymongo_basemodel.core.DotNotationContainer()
    self.assertIsInstance(c, pymongo_basemodel.core.DotNotationContainer)

  def test_init_with_data(self):
    """ __init__ returns a reference to an instantiated DotNotationContainer 
    with data argument set to __dict__ if set
    """

    c = pymongo_basemodel.core.DotNotationContainer({ "key": "value" })
    self.assertEqual(c.__dict__, { "key": "value" })


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestInit)
  unittest.TextTestRunner().run(suite)