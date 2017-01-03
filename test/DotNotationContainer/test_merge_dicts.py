
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_merge_dicts(self):
    """ merge_dicts will recursively merge argument dicts where first dict 
    overwrites second dict and return result
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    data1 = {
      "key1": "value",
      "key2": {
        "key3": "value",
        "key4": "value"
      }
    }

    data2 = {
      "key2": {
        "key3": "something",
        "key5": "value"
      },
      "key3": "value"
    }

    self.assertEqual(c.merge_dicts(data1, data2), {
      "key1": "value",
      "key2": {
        "key3": "value",
        "key4": "value",
        "key5": "value"
      },
      "key3": "value"
    })

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)