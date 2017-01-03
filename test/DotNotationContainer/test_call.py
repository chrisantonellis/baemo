
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class TestCall(unittest.TestCase):

  def test_call(self):
    """ when called DotNotationContainer will overwrite __dict__ with data 
    argument
    """

    c = pymongo_basemodel.core.DotNotationContainer()
    self.assertEqual(c.__dict__, {})

    c({ "key": "value" })
    self.assertEqual(c.__dict__, { "key": "value" })


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestCall)
  unittest.TextTestRunner().run(suite)
