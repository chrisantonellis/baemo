
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class TestHas(unittest.TestCase):

  def test_has(self):
    """ has will return True if a key is set in __dict__ and False if not
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    c.set("key", "value")

    self.assertEqual(c.has("key"), True)

    self.assertEqual(c.has("something"), False)

  def test_has_dot_notation(self):
    """ has will return True if a key is set in __dict__ and False if not and 
    expand dot notation keys
    """

    c = pymongo_basemodel.core.DotNotationContainer()

    c.set("key1.key2", "value")

    self.assertEqual(c.has("key1.key2"), True)
    self.assertEqual(c.has("key1.something"), False)


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(TestHas)
  unittest.TextTestRunner().run(suite)
  