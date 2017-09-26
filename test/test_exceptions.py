
import sys; sys.path.append("../")

import unittest

from baemo.exceptions import BasemodelException


class TestBasemodelException(unittest.TestCase):

    # __init__

    def test___init__(self):
        e = BasemodelException()
        self.assertIsInstance(e, BasemodelException)

    def test___init__message_param(self):
        e = BasemodelException(message="foo")
        self.assertEqual(e.message, "foo")

    def test___init__data_param(self):
        e = BasemodelException(data={"foo": "bar"})
        self.assertEqual(e.data, {"foo": "bar"})

    def test___init___message_with_args(self):
        e = BasemodelException("foo", "bar", message="{}, {}")
        self.assertEqual(e.message, "foo, bar")

    # get

    def test_get__returns_dict(self):
        e = BasemodelException(message="foo", data={"k": "v"})
        self.assertEqual(e.get(), {
            "message": "foo",
            "data": {"k": "v"}
        })


if __name__ == "__main__":
    unittest.main()