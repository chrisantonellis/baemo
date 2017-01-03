
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class TestKeys(unittest.TestCase):

  def test_keys(self):
    """ __keys__ yields an iterable for keys of __dict__
    """

    c = pymongo_basemodel.core.DotNotationContainer({ "key": "value"})

    for key in c.keys():
      self.assertEqual(key, "key")
      self.assertEqual(type(key), str)


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestKeys)
  unittest.TextTestRunner().run(suite)