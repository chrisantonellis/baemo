
import sys; sys.path.append("../")

import unittest
import pymongo

from pymongo_basemodel.connection import add_connection
from pymongo_basemodel.connection import get_connection
from pymongo_basemodel.connection import set_default_connection
from pymongo_basemodel.connection import _connections

class TestConnection(unittest.TestCase):

    def setUp(self):
        global connection1, connection2

        connection1 = pymongo.MongoClient(connect=False)["pymongo_basemodel1"]
        connection2 = pymongo.MongoClient(connect=False)["pymongo_basemodel1"]

    def tearDown(self):
        _connections = {}

    def test_add_connection(self):
        global connection1, connection2

        add_connection("connection1", connection1)
        self.assertEqual(_connections, {"connection1": connection1})

    def test_get_connection(self):
        global connection1, connection2

        add_connection("connection1", connection1)
        add_connection("connection2", connection2)

        # get by name
        self.assertEqual(get_connection("connection1"), connection1)
        self.assertEqual(get_connection("connection2"), connection2)

        # get default connection
        self.assertEqual(get_connection(), connection1)

    def test_set_default_connection(self):
        global connection1, connection2

        add_connection("connection1", connection1)
        self.assertEqual(get_connection(), connection1)

        set_default_connection("connection2")
        self.assertEqual(get_connection(), connection2)


if __name__ == "__main__":
    unittest.main()
