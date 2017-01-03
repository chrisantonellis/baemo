
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_str(self):
    """ __str__ will return message attribute when called
    """

    first_name = pymongo_basemodel.core.Undefined()
    last_name = "Somebody"
    full_name = "%s %s" % (first_name, last_name)
    self.assertEqual(full_name, "undefined Somebody")

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)