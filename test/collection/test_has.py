
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_had(self):

    model1 = pymongo_basemodel.core.Model()
    model1.set("key", "value")

    collection = pymongo_basemodel.core.Collection()
    collection.add(model1)
    collection.add(pymongo_basemodel.core.Model())

    self.assertEqual(collection.has("key"), [ True, False ])

if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)