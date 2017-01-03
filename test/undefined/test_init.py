
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_init(self):
    """ __init__ returns a reference to an instantiated Undefined
    """

    c = pymongo_basemodel.core.Undefined()
    self.assertIsInstance(c, pymongo_basemodel.core.Undefined)


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)