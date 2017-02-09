
import unittest

from pymongo_basemodel.exceptions import BaseException
from pymongo_basemodel.exceptions import ProjectionMalformed


class TestExceptions(unittest.TestCase):

    def test_base_exception(self):
        be1 = BaseException()
        self.assertIsInstance(be1, BaseException)
        self.assertEqual(be1.message, "pymongo_basemodel error")
        self.assertEqual(be1.data, None)

        # message
        be2 = BaseException(message="custom message")
        self.assertEqual(be2.message, "custom message")

        # data
        be3 = BaseException(data={"key": "value"})
        self.assertEqual(be3.data, {"key": "value"})

        # get()
        be4 = BaseException(message="custom message", data={"k": "v"})
        self.assertEqual(be4.get(), {
            "message": "custom message",
            "data": {"k": "v"}
        })

    def test_projection_malformed(self):
        be1 = ProjectionMalformed("k", "v")
        self.assertIsInstance(be1, ProjectionMalformed)
        self.assertEqual(be1.key, "k")
        self.assertEqual(be1.value, "v")
        self.assertEqual(
            be1.message,
            "Projection malformed, invalid value 'v' for key 'k'"
        )
