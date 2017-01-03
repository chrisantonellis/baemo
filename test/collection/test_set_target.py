
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_set_target(self):
    """set_target() sets collection lookup target on collection
    """ 

    # value is dict
    a = pymongo_basemodel.core.Collection()
    a.set_target({ "color": "red" })
    self.assertEqual(a.target, { "color": "red" })

    # value is list, use iterator
    b = pymongo_basemodel.core.Collection()
    b.set_target([ "value1", "value2", "value3" ], "key")
    self.assertEqual(b.target, { "key": { "$in": [ "value1", "value2", "value3" ] }})

    # value is string, conver to list, use iterator
    b = pymongo_basemodel.core.Collection()
    b.set_target("value", "key")
    self.assertEqual(b.target, { "key": { "$in": [ "value" ] }})


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
