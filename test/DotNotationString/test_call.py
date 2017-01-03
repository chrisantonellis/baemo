
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class TestCall(unittest.TestCase):

  def test_call(self):
    """ when called DotNotationString will overwrite __dict__ with data 
    argument
    """

    c = pymongo_basemodel.core.DotNotationString()
    self.assertEqual(c.raw, "")
    self.assertEqual(c.keys, [""])

    c("key")
    self.assertEqual(c.raw, "key")
    self.assertEqual(c.keys, ["key"])


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestCall)
  unittest.TextTestRunner().run(suite)
