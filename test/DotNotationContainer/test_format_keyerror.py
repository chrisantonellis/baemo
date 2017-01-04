
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_format_keyerror(self):
    """ format_keyerror returns a message formatted for use in a 
    KeyError
    """

    # create model
    a = pymongo_basemodel.core.DotNotationContainer()

    needle = "key"
    key = pymongo_basemodel.core.DotNotationString("key")

    self.assertEqual(a.format_keyerror(needle, key), "key")

    needle = "key2"
    key = "key1.key2.key3"

    self.assertEqual(a.format_keyerror(needle, key), "key2 in key1.key2.key3")

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
