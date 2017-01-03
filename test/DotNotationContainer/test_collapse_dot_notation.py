
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_collapse_dot_notation(self):
    """ collapse_dot_notation will return nested data keys from argument dict
    in dot notation
    """

    c = pymongo_basemodel.core.DotNotationContainer()    

    data = {
      "key1": {
        "key2": {
          "key3": "value"
        }
      }
    }

    self.assertEqual(c.collapse_dot_notation(data), {
      "key1.key2.key3": "value"
    })

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)