
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_repr(self):
    c = pymongo_basemodel.core.DotNotationString("key1.key2.key3")
    self.assertEqual(str(c), "key1.key2.key3")


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)