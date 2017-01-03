
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_push_many(self):
    """ push_many appends multiple values successively to a model list 
    attribute
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # assert value not set
    self.assertEqual(type(a.get("key")), pymongo_basemodel.core.Undefined)

    # push value
    a.push_many("key", ["value1", "value2", "value3"])

    # assert value pushed to list attribute
    self.assertEqual(type(a.get("key")), list)
    self.assertEqual(a.get("key"), ["value1", "value2", "value3"])

    # the reason push and push_many are separated
    a.push("key2", ["value1", "value2"])
    a.push("key2", ["value3", "value4"])

    self.assertEqual(a.get("key2"), [
      ["value1", "value2"],
      ["value3", "value4"]
    ])

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)