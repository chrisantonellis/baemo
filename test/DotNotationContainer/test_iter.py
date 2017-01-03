
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class TestIter(unittest.TestCase):

  def test_iter(self):
    """ __iter__ yields an interable tuple of key value pairs from __dict__
    """

    c = pymongo_basemodel.core.DotNotationContainer({
      "key1": "value",
      "key2": "value",
      "key3": "value"
    })

    for item in c:
      self.assertEqual(type(item), tuple)

    for key, val in c:
      self.assertEqual(type(key), str)
      self.assertEqual(type(val), str)
      self.assertEqual(val, "value")


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestIter)
  unittest.TextTestRunner().run(suite)