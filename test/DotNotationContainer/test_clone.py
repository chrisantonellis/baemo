
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_clone(self):
    """ clone will return an instance of DotNotationContainer with 
    __dict__ as a deepcopy of parent DotNotationContainer __dict__
    """

    a = pymongo_basemodel.core.DotNotationContainer()

    a.set("key", "value")

    self.assertEqual(a.__dict__, {
      "key": "value"
    })

    c = a.clone()

    self.assertEqual(c.__dict__, {
      "key": "value"
    })

    self.assertIsNot(a.__dict__, c.__dict__)

  def test_clone_nested(self):
    """ clone will return an instance of DotNotationContainer with 
    __dict__ as a deepcopy of parent DotNotationContainer __dict__ nested data
    """

    a = pymongo_basemodel.core.DotNotationContainer()

    a.set("key1.key2.key3", "value")

    self.assertEqual(a.__dict__, {
      "key1": {
        "key2": {
          "key3": "value"
        }
      }
    })

    c = a.clone("key1.key2")

    self.assertEqual(c.__dict__, {
      "key3": "value"
    })

    self.assertIsNot(a.ref("key1.key2"), c.__dict__)


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
  