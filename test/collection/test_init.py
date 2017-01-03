
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_init(self):
    """__init__() returns an instantiated collection with correct default 
    attributes set
    """

    a = pymongo_basemodel.core.Collection()

    self.assertIsInstance(a.target, pymongo_basemodel.core.DotNotationContainer)
    self.assertEqual(a.collection, [])

    b = pymongo_basemodel.core.Collection({ "key": "value" })

    self.assertEqual(b.target, { "key": "value" })


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
