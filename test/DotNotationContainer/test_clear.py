
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class TestClear(unittest.TestCase):

  def test_clear(self):
    """ clear removes all values from __dict__
    """
    c = pymongo_basemodel.core.DotNotationContainer({
      "key1": "value",
      "key2": "value",
      "key3": "value"
    })

    self.assertEqual(c.__dict__, {
      "key1": "value",
      "key2": "value",
      "key3": "value"
    })

    c.clear()

    self.assertEqual(c.__dict__, {})    


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestClear)
  unittest.TextTestRunner().run(suite)
