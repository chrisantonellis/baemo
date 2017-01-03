
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_setitem(self):
    """ when called DotNotationContainer will return a child instance of 
    DotNotationContainer with __dict__ as a reference to nested data in 
    parent instance, to allow for chaining an changing nested values by 
    reference
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    c["key"] = "value"
    self.assertEqual(c.__dict__, { "key": "value" })

    c.clear()
    c["key1.key2.key3"] = "value"
    self.assertEqual(c.__dict__, { "key1": { "key2": { "key3": "value" }}})



if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
