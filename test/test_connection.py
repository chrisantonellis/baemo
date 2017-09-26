
import sys; sys.path.append("../")

import unittest
import pymongo

from baemo.connection import Connections
from baemo.exceptions import ConnectionNotSet


class TestConnection(unittest.TestCase):

    def setUp(self):
        global database_name, collection_name, c
        database_name = "baemo"
        collection_name = "{}_{}".format(
            self.__class__.__name__,
            self._testMethodName
        )
        c = pymongo.MongoClient(connect=False)[database_name]

    def tearDown(self):
        Connections.cache = {}
        Connections.default = None

    # set

    def test_set__connection_param(self):
        global c
        Connections.set("c", c)
        self.assertEqual(Connections.cache, {"c": c})

    def test_set__connection_param__set_default_connection(self):
        global c
        Connections.set("c", c)
        self.assertEqual(Connections.default, c)

    def test_set__connection_and_default_param__overwrite_default_connection(self):
        global c, database_name
        Connections.set("c", c)
        d = pymongo.MongoClient(connect=False)[database_name]
        Connections.set("d", d, default=True)
        self.assertEqual(Connections.default, d)

    # get

    def test_get__string_param__returns_connection(self):
        global c
        Connections.set("c", c)
        self.assertEqual(Connections.get("c"), c)
        self.assertEqual(type(Connections.get("c")), pymongo.database.Database)

    def test_get__string_params__returns_collection(self):
        global c, collection_name
        Connections.set("c", c)
        self.assertEqual(type(Connections.get("c", collection_name)), pymongo.collection.Collection)

    def test_get__string_param__raises_ConnectionNotSet(self):
        with self.assertRaises(ConnectionNotSet):
            Connections.get("foo")

    def test_get__no_param__returns_default_connection(self):
        global c
        Connections.set("c", c)
        self.assertEqual(Connections.get(), c)

    def test_get__no_param__raises_ConnectionNotSet(self):
        with self.assertRaises(ConnectionNotSet):
            Connections.get()


if __name__ == "__main__":
    unittest.main()
