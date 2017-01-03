
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_has(self):

    c = pymongo_basemodel.core.DotNotationString()

    c("key")

    self.assertEqual(len(c), 1)

    c("key1.key2.key3")
    self.assertEqual(len(c), 3)


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
  