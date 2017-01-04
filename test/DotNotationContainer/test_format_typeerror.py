
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_format_typeerror(self):
    """ format_typeerror returns a message formatted for use in a 
    TypeError
    """

    a = pymongo_basemodel.core.DotNotationContainer()

    type_ = "string"
    needle = "key"
    key = pymongo_basemodel.core.DotNotationString("key")
    message = "Expected dict, found str for key"
    self.assertEqual(a.format_typeerror(type_, needle, key), message)

    type_ = [ "list" ]
    needle = "key2"
    key = pymongo_basemodel.core.DotNotationString("key1.key2.key3")
    message = "Expected dict, found list for key2 in key1.key2.key3"
    self.assertEqual(a.format_typeerror(type_, needle, key), message)

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
