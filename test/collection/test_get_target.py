
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_get_target(self):
    """ get_target() returns a target of a collection or None
    """ 

    a = pymongo_basemodel.core.Collection()
    self.assertEqual(a.get_target(), None)
    a.set_target({ "color": "red" })
    self.assertEqual(a.get_target(), { "color": "red" })


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
