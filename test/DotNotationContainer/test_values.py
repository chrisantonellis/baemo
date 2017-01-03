
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class TestValues(unittest.TestCase):

  def test_values(self):
    """ __values__ yields an iterable for values of __dict__
    """

    c = pymongo_basemodel.core.DotNotationContainer({ "key": "value"})

    for val in c.values():
      self.assertEqual(val, "value")
      self.assertEqual(type(val), str)


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestValues)
  unittest.TextTestRunner().run(suite)