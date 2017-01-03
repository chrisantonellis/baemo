
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class TestIter(unittest.TestCase):

  def test_iter(self):
    """ __iter__ yields an interable tuple of key value pairs from __dict__
    """

    c = pymongo_basemodel.core.DotNotationString("key.key.key")

    self.assertEqual(len(c.keys), 3)
    for item in c:
      self.assertEqual(item, "key")


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestIter)
  unittest.TextTestRunner().run(suite)