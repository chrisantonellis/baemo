
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class TestInit(unittest.TestCase):

  def test_init(self):
    """ __init__ returns a reference to an instantiated DotNotationString 
    """

    c = pymongo_basemodel.core.DotNotationString()
    self.assertIsInstance(c, pymongo_basemodel.core.DotNotationString)

  def test_init_with_data(self):
    """ __init__ returns a reference to an instantiated DotNotationString 
    with data argument set to __dict__ if set
    """

    c = pymongo_basemodel.core.DotNotationString("key")
    self.assertEqual(c.raw, "key")


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestInit)
  unittest.TextTestRunner().run(suite)