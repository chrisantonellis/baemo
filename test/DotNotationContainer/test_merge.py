
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_merge(self):
    """ merge will recursively merge dict argument with __dict__ and return 
    result without altering __dict__
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    c.set("key1", "value")

    self.assertEqual(c.__dict__, { "key1": "value" })

    value1 = c.merge({ "key2": "value" })

    self.assertEqual(value1, {
      "key1": "value",
      "key2": "value"
    })

    value2 = c.merge({ "key1": "something" })

    self.assertEqual(value2, {
      "key1": "something",
      "key2": "value"
    })



if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
  