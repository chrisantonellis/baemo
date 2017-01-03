
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_getitem(self):
    c = pymongo_basemodel.core.DotNotationString()
    self.assertEqual(c.raw, "")
    self.assertEqual(c.keys, [""])

    c("key1.key2.key3")
    self.assertEqual(c.raw, "key1.key2.key3")
    self.assertEqual(c.keys, ["key1", "key2", "key3"])

    self.assertEqual(c[0], "key1")
    self.assertEqual(c[-1], "key3")
    self.assertEqual(c[:-1], "key1.key2")


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
