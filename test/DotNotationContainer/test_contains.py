
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class TestContains(unittest.TestCase):

  def test_contains(self):
    """ __contains__ allows for use of in to check for keys in __dict__
    """

    c = pymongo_basemodel.core.DotNotationContainer({ "key": "value" })

    self.assertEqual("key" in c, True)
    self.assertEqual("hrr" in c, False)



if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestContains)
  unittest.TextTestRunner().run(suite)
