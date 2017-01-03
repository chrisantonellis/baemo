
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_pull_many(self):
    """ pull_many removes multiple values successively from a model list 
    attribute
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # set data on model
    a.set("key", [ "value1", "value2", "value3" ])

    # pull value from model
    a.pull_many("key", [ "value2", "value3" ])

    # assert that value was pulled
    self.assertEqual(a.get(), {
      "key": [ "value1" ]
    })

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)