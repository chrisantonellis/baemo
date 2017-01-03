
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_reset(self):
    """ reset sets all model state variables to default values
    """

    # create model
    a = pymongo_basemodel.core.Model()

    # set data on model
    a.attributes({ "key": "value" })
    a.target = { "color": "red" }

    a.delete()

    self.assertEqual(bool(a.target), True)
    self.assertEqual(bool(a.attributes), True)
    self.assertEqual(a._delete, True)

    # reset model
    a.reset()

    # assert that model state variables set to default values
    self.assertEqual(bool(a.target), False)
    self.assertEqual(bool(a.updates), False)
    self.assertEqual(bool(a.attributes), False)
    self.assertEqual(a._delete, False)

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)