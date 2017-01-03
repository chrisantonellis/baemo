
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class TestRepr(unittest.TestCase):

  def test_repr(self):
    """ __repr__ returns a string representation of __dict__
    """

    c = pymongo_basemodel.core.DotNotationContainer({ "key": "value"})
    self.assertEqual(str(c), "{'key': 'value'}")


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestRepr)
  unittest.TextTestRunner().run(suite)