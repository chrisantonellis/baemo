
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_collapse(self):
    """ collapse will return nested data keys from __dict__ in dot notation
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    c.set("key1.key2.key3", "value")
    c.set("key1.key3.key4", "value")
    c.set("key1.key2.key5", "value")

    self.assertEqual(c.__dict__, {
      "key1": {
        "key2": {
          "key3": "value",
          "key5": "value"
        },
        "key3": {
          "key4": "value"
        }
      }
    })

    self.assertEqual(c.collapse(), {
      "key1.key2.key5": "value",
      "key1.key3.key4": "value",
      "key1.key2.key3": "value"
    })


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)