
import sys
sys.path.extend([ "../", "../../" ])

import unittest
import pymongo_basemodel


class Test(unittest.TestCase):

  def test_init(self):
    """ baseexception is the base exception that all other pymongo_basemodel 
    exceptions extend from
    """

    e = pymongo_basemodel.exceptions.BaseException()

    self.assertIsInstance(e, pymongo_basemodel.exceptions.BaseException)
    self.assertEqual(e.message, "pymongo_basemodel error")
    self.assertEqual(e.data, None)

  def test_message(self):
    """ baseexception allows for overriding the default message by passing the 
    argument "message" on instantiation
    """

    e = pymongo_basemodel.exceptions.BaseException(message = "custom message")
    self.assertEqual(e.message, "custom message")

  def test_data(self):
    """ baseexception allows for attaching data to the exception by passing 
    the argument "data" on instantiation
    """

    e = pymongo_basemodel.exceptions.BaseException(data = { "key": "value" })
    self.assertEqual(e.data, { "key": "value" })

  def test_get(self):
    """ get returns a dict representation of attributes set on baseexception
    """

    e = pymongo_basemodel.exceptions.BaseException(
      message = "Custom Message",
      data = { "key": "value" }
    )
    self.assertEqual(e.get(), {
      "message": "Custom Message",
      "data": {
        "key": "value"
      }
    })


if __name__ == "__main__":
  suite = unittest.defaultTestLoader.loadTestsFromTestCase(Test)
  unittest.TextTestRunner().run(suite)
