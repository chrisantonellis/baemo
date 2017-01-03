
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class TestUpdate(unittest.TestCase):

  def test_update(self):
    """ update will recursively merge dict argument with __dict__ and and return 
    result 
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    c.set("key1", "value")

    self.assertEqual(c.__dict__, { "key1": "value" })

    value1 = c.update({ "key2": "value" })

    self.assertEqual(value1, {
      "key1": "value", 
      "key2": "value"
    })

    self.assertEqual(c.__dict__, {
      "key1": "value", 
      "key2": "value"
    })

    c.update({ "key1": "something" })

    self.assertEqual(c.__dict__, {
      "key1": "something",
      "key2": "value"
    })



if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestUpdate)
  unittest.TextTestRunner().run(suite)
  