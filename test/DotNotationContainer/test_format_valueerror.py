
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_format_valueerror(self):
    """ format_valueerror returns a message formatted for use in a 
    ValueError
    """

    a = pymongo_basemodel.core.DotNotationContainer()

    value = "value"
    needle = "key"
    key = pymongo_basemodel.core.DotNotationString("key")
    message = "value not in list for key"
    self.assertEqual(a.format_valueerror(needle, key, value), message)

    value = "value"
    needle = "key2"
    key = pymongo_basemodel.core.DotNotationString("key1.key2.key3")
    message = "value not in list for key2 in key1.key2.key3"
    self.assertEqual(a.format_valueerror(needle, key, value), message)

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
