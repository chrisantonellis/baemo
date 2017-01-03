
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_expand_dot_notation(self):
    """ expand_dot_notation will recursively expand dot notation keys in a dict 
    to nested data and return the restult
    """

    c = pymongo_basemodel.core.DotNotationContainer()    

    data1 = {
      "key1.key2.key3": "value"
    }

    self.assertEqual(c.expand_dot_notation(data1), {
      "key1": {
        "key2": {
          "key3": "value"
        }
      }
    })

    data2 = {
      "key1.key2.key3": "value",
      "key1.key2.key4": "value",
      "key1.key2.key5": "value",
      "key1.key8.key9": "value"
    }

    self.assertEqual(c.expand_dot_notation(data2), {
      "key1": {
        "key2": {
          "key3": "value",
          "key4": "value",
          "key5": "value"
        },
        "key8": {
          "key9": "value"
        }
      }
    })


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
  