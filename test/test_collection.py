
import sys; sys.path.append("../")

import unittest
import copy
import pymongo
import bson

from pymongo_basemodel.connection import Connections
from pymongo_basemodel.sort import Sort
from pymongo_basemodel.model import Model
from pymongo_basemodel.collection import Collection
from pymongo_basemodel.entity import Entity

from pymongo_basemodel.exceptions import ModelNotFound
from pymongo_basemodel.exceptions import ModelTargetNotSet
from pymongo_basemodel.exceptions import CollectionModelClassMismatch
from pymongo_basemodel.exceptions import CollectionModelNotPresent
from pymongo_basemodel.exceptions import DereferenceError


class TestCollection(unittest.TestCase):

    def setUp(self):
        global database_name, collection_name, TestModel, TestCollection
        database_name = "pymongo_basemodel"
        collection_name = "{}_{}".format(
            self.__class__.__name__,
            self._testMethodName
        )

        connection = pymongo.MongoClient(connect=False)[database_name]
        Connections.set(database_name, connection)

        TestModel, TestCollection = Entity("Test", {
            "mongo_database": database_name,
            "mongo_collection": collection_name
        })

    def tearDown(self):
        global database_name, collection_name
        Connections.get(database_name).drop_collection(collection_name)

    def test_init(self):
        c = Collection()
        self.assertEqual(c.collection, [])

        self.assertEqual(c.target.get(), {})
        self.assertEqual(c.default_sort, Sort())

        self.assertEqual(c.default_find_projection.get(), {})
        self.assertEqual(c.default_get_projection.get(), {})

    def test_copy(self):
        c1 = TestCollection()
        c1.add(TestModel())
        c2 = copy.copy(c1)
        self.assertIsNot(c1, c2)
        self.assertEqual(c1.collection, c2.collection)

        c2.collection.append(TestModel())
        self.assertEqual(c1.collection, c2.collection)

    def test_deepcopy(self):
        c1 = TestCollection()
        c1.add(TestModel())
        c2 = copy.deepcopy(c1)
        self.assertIsNot(c1, c2)
        self.assertEqual(c1.collection, c2.collection)

        c2.collection.append(TestModel())
        self.assertNotEqual(c1.collection, c2.collection)

    def test_eq(self):
        c1 = TestCollection()
        c2 = TestCollection()
        self.assertEqual(True, c1 == c2)

    def test_ne(self):
        c1 = TestCollection()
        m1 = TestModel()
        c1.add(m1)
        c2 = TestCollection()
        self.assertEqual(True, c1 != c2)

    def test_len(self):
        c = TestCollection()
        self.assertEqual(len(c), 0)
        c.add(TestModel())
        c.add(TestModel())
        c.add(TestModel())
        self.assertEqual(len(c), 3)

    def test_iter(self):
        c = TestCollection()
        c.add(TestModel())
        c.add(TestModel())
        c.add(TestModel())
        for m in c:
            self.assertEqual(type(m), TestModel)

    def test_setitem(self):
        c = TestCollection()
        m1 = TestModel()
        c.add(m1)
        m2 = TestModel()
        c[0] = m2
        self.assertEqual(c.collection, [m2])

        with self.assertRaises(CollectionModelClassMismatch):
            c[0] = Model()

    def test_getitem(self):
        m = TestModel()
        c = TestCollection()
        c.add(m)
        self.assertEqual(c[0], m)

    def test_delitem(self):
        m = TestModel()
        c = TestCollection()
        c.add(m)
        del c[0]
        self.assertEqual(c.collection, [])

    def test_reversed(self):
        m1 = TestModel()
        m2 = TestModel()
        m3 = TestModel()
        c = TestCollection()
        c.add(m1)
        c.add(m2)
        c.add(m3)
        self.assertEqual(c.collection, [m1, m2, m3])
        self.assertEqual(list(reversed(c)), [m3, m2, m1])

    def test_set_target(self):

        # dict
        c1 = TestCollection()
        c1.set_target({"k": "v"})
        self.assertEqual(c1.target.get(), {"k": "v"})

        # list, str
        c2 = TestCollection()
        c2.set_target(["v1", "v2", "v3"], "k")
        self.assertEqual(c2.target.get(), {"k": {"$in": ["v1", "v2", "v3"]}})

        # str, str
        c3 = TestCollection()
        c3.set_target("v", "k")
        self.assertEqual(c3.target.get(), {"k": {"$in": ["v"]}})

    def test_get_target(self):
        c = TestCollection()
        self.assertEqual(c.get_target(), None)
        c.set_target({"k": "v"})
        self.assertEqual(c.get_target(), {"k": "v"})

    def test_get_targets(self):
        m1 = Model(bson.objectid.ObjectId())
        m2 = Model(bson.objectid.ObjectId())
        c = TestCollection()
        c.collection = [m1, m2]
        targets = c.get_targets()
        self.assertEqual(type(targets), list)

        for t in targets:
            self.assertEqual(type(t), dict)

    def test_get_ids(self):
        m1 = Model(bson.objectid.ObjectId())
        m2 = Model(bson.objectid.ObjectId())
        c = TestCollection()
        c.collection = [m1, m2]
        ids = c.get_ids()
        self.assertEqual(type(ids), list)

        for id_ in ids:
            self.assertEqual(type(id_), bson.objectid.ObjectId)

    def test_find(self):

        # all ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m1 = TestModel()
        m1.save()
        m2 = TestModel()
        m2.save()
        c1 = TestCollection()
        self.assertEqual(c1.target.get(), {})
        c1.find()
        self.assertEqual(len(c1), 2)

        for m in c1:
            self.assertEqual(type(m), TestModel)

        self.tearDown()

        # target ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m3 = TestModel()
        m3.set("k", "v1")
        m3.save()
        m4 = TestModel()
        m4.set("k", "v2")
        m4.save()
        c2 = TestCollection()
        c2.set_target({"k": "v2"})
        c2.find()
        self.assertEqual(len(c2), 1)
        self.assertEqual(c2.collection[0], m4)

        self.tearDown()

        # projection ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m6 = TestModel()
        m6.set("k1", "v")
        m6.set("k2", "v")
        m6.set("k3", "v")
        m6.save()
        m7 = TestModel()
        m7.set("k1", "v")
        m7.set("k2", "v")
        m7.set("k3", "v")
        m7.save()
        c3 = TestCollection()
        c3.find(projection={"k2": 1})
        self.assertEqual(len(c3.collection), 2)
        for m in c3:
            self.assertEqual(type(m), TestModel)
            self.assertNotIn("k1", m.attributes.get())
            self.assertIn("k2", m.attributes.get())
            self.assertNotIn("k3", m.attributes.get())

        self.tearDown()

        # target, projection ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m8 = TestModel()
        m8.set("k1", "v1")
        m8.set("k2", "v1")
        m8.set("k3", "v1")
        m8.save()
        m9 = TestModel()
        m9.set("k1", "v2")
        m9.set("k2", "v2")
        m9.set("k3", "v2")
        m9.save()
        c4 = TestCollection({"k1": "v1"})
        c4.find(projection={"k3": 0})
        self.assertEqual(len(c4.collection), 1)
        for m in c4:
            self.assertEqual(type(m), TestModel)
            self.assertIn("k1", m.attributes.get())
            self.assertIn("k2", m.attributes.get())
            self.assertNotIn("k3", m.attributes.get())

        self.tearDown()

        # mongo syntax target ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m10 = TestModel()
        m10.set("k", ["v1", "v2"])
        m10.save()
        m11 = TestModel()
        m11.set("k", ["v1"])
        m11.save()
        c5 = TestCollection({"k": {"$in": ["v2"]}})
        c5.find()
        self.assertEqual(len(c5.collection), 1)
        for m in c5:
            self.assertEqual(type(m), TestModel)
            self.assertEqual(m.get("k"), ["v1", "v2"])

        self.tearDown()

        # default get projection ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        DGP1Model, DGP1Collection = Entity("DGP1", {
            "mongo_database": database_name,
            "mongo_collection": collection_name,
        }, {
            "default_get_projection": {
                "k1": 0
            }
        })

        m11 = DGP1Model()
        m11.set({"k1": "v", "k2": "v", "k3": "v"})
        m11.save()
        c6 = DGP1Collection()
        c6.set_target(m11.get_id())
        c6.find()

        for m in c6.get():
            self.assertNotIn("k1", m)
            self.assertIn("k2", m)
            self.assertIn("k3", m)

        self.tearDown()

        # default find projection ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        DFP1Model, DFP1Collection = Entity("DFP1", {
            "mongo_database": database_name,
            "mongo_collection": collection_name
        }, {
            "default_find_projection": {
                "k1": 0
            }
        })

        m12 = DFP1Model()
        m12.set({"k1": "v", "k2": "v", "k3": "v"})
        m12.save()
        c7 = DFP1Collection()
        c7.set_target(m12.get_id())
        c7.find()

        for m in c7:
            self.assertNotIn("k1", m.get())
            self.assertIn("k2", m.get())
            self.assertIn("k3", m.get())

        self.tearDown()

        # default model projection ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        DFP2Model, DFP2Collection = Entity("DFP2", {
            "mongo_database": database_name,
            "mongo_collection": collection_name,
            "default_find_projection": {
                "k1": 1
            }
        })

        m1 = DFP2Model()
        m1.set({"k1": "v", "k2": "v", "k3": "v"})
        m1.save()
        c = DFP2Collection()
        c.find(default_model_projection=True)
        self.assertEqual(c.get(), [{
            m1.id_attribute: m1.get(m1.id_attribute),
            "k1": "v"
        }])

        self.tearDown()

        # default sort ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        DSModel, DSCollection = Entity("DS", {
            "mongo_database": database_name,
            "mongo_collection": collection_name
        }, {
            "default_sort": [("k2", 1)]
        })

        m1 = DSModel()
        m1.set({"k1": "v1", "k2": 2, "k3": "v1"})
        m1.save()
        m2 = DSModel()
        m2.set({"k1": "v2", "k2": 3, "k3": "v2"})
        m2.save()
        m3 = DSModel()
        m3.set({"k1": "v3", "k2": 1, "k3": "v3"})
        m3.save()
        c = DSCollection()
        c.find()

        self.assertEqual(c.get(), [
            {
                m3.id_attribute: m3.get(m3.id_attribute),
                "k1": "v3",
                "k2": 1,
                "k3":
                "v3"
            }, {
                m1.id_attribute: m1.get(m1.id_attribute),
                "k1": "v1",
                "k2": 2,
                "k3": "v1"
            }, {
                m2.id_attribute: m2.get(m2.id_attribute),
                "k1": "v2",
                "k2": 3,
                "k3": "v2"
            }
        ])

        self.tearDown()

        # argument sort ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        ASModel, ASCollection = Entity("AS", {
            "mongo_database": database_name,
            "mongo_collection": collection_name
        })

        m1 = ASModel()
        m1.set({"k1": "v1", "k2": 2, "k3": "v1"})
        m1.save()
        m2 = ASModel()
        m2.set({"k1": "v2", "k2": 3, "k3": "v2"})
        m2.save()
        m3 = ASModel()
        m3.set({"k1": "v3", "k2": 1, "k3": "v3"})
        m3.save()
        c = ASCollection()
        c.find(sort=[("k2", 1)])

        self.assertEqual(c.get(), [
            {
                m3.id_attribute: m3.get(m3.id_attribute),
                "k1": "v3",
                "k2": 1,
                "k3":
                "v3"
            }, {
                m1.id_attribute: m1.get(m1.id_attribute),
                "k1": "v1",
                "k2": 2,
                "k3": "v1"
            }, {
                m2.id_attribute: m2.get(m2.id_attribute),
                "k1": "v2",
                "k2": 3,
                "k3": "v2"
            }
        ])

        self.tearDown()

        # default limit ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        DLModel, DLCollection = Entity("DL", {
            "mongo_database": database_name,
            "mongo_collection": collection_name
        }, {
            "default_limit": 2
        })

        m1 = DLModel()
        m1.set({"k": "v"})
        m1.save()
        m2 = DLModel()
        m2.set({"k": "v"})
        m2.save()
        m3 = DLModel()
        m3.set({"k": "v"})
        m3.save()
        c = DLCollection()
        c.find()

        self.assertEqual(len(c.get()), 2)

        self.tearDown()

        # argument limit ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        ALModel, ALCollection = Entity("AL", {
            "mongo_database": database_name,
            "mongo_collection": collection_name
        })

        m1 = ALModel()
        m1.set({"k": "v"})
        m1.save()
        m2 = ALModel()
        m2.set({"k": "v"})
        m2.save()
        m3 = ALModel()
        m3.set({"k": "v"})
        m3.save()
        c = ALCollection()
        c.find(limit=2)

        self.assertEqual(len(c.get()), 2)

        self.tearDown()

        # limit raise exception ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        c = ALCollection()

        with self.assertRaises(TypeError):
            c.find(limit="foo")

        self.tearDown()

        # default skip ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        DSModel, DSCollection = Entity("DS", {
            "mongo_database": database_name,
            "mongo_collection": collection_name
        }, {
            "default_skip": 2
        })

        m1 = DSModel()
        m1.set({"k": "v1"})
        m1.save()
        m2 = DSModel()
        m2.set({"k": "v2"})
        m2.save()
        m3 = DSModel()
        m3.set({"k": "v3"})
        m3.save()
        c = DSCollection()
        c.find()

        self.assertEqual(len(c.get()), 1)
        for m in c:
            self.assertEqual(m.get("k"), "v3")

        self.tearDown()

        # argument skip ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        ASModel, ASCollection = Entity("AS", {
            "mongo_database": database_name,
            "mongo_collection": collection_name
        })

        m1 = ASModel()
        m1.set({"k": "v1"})
        m1.save()
        m2 = ASModel()
        m2.set({"k": "v2"})
        m2.save()
        m3 = ASModel()
        m3.set({"k": "v3"})
        m3.save()
        c = ASCollection()
        c.find(skip=2)

        self.assertEqual(len(c.get()), 1)
        for m in c:
            self.assertEqual(m.get("k"), "v3")

        self.tearDown()

    def test_ref(self):
        m1 = TestModel()
        m1.set("k", "v")
        c1 = TestCollection()
        c1.add(m1)
        self.assertEqual(c1.ref()[0], m1.attributes.get())

    def test_has(self):
        m1 = Model()
        m1.set("k", "v")
        m2 = Model()
        c1 = Collection()
        c1.collection.append(m1)
        c1.collection.append(m2)
        self.assertEqual(c1.has("k"), [True, False])

    def test_get(self):
        m1 = TestModel()
        m1.set("k", "v")
        m2 = TestModel()
        m2.set("k", "v")
        c1 = TestCollection()
        c1.add(m1)
        c1.add(m2)
        self.assertEqual(c1.get(), [{"k": "v"}, {"k": "v"}])

        m3 = TestModel()
        m3.set("k1", "v")
        m3.set("k2", "v")
        m4 = TestModel()
        m4.set("k1", "v")
        m4.set("k2", "v")
        c2 = TestCollection()
        c2.add(m3)
        c2.add(m4)
        self.assertEqual(c2.get("k2"), ["v", "v"])

        m = TestModel()
        m.set({"k1": "v", "k2": "v", "k3": "v"})
        c = TestCollection()
        c.add(m)
        self.assertEqual(c.get(projection={"k1": 1}), [{"k1": "v"}])

    def test_set(self):
        m1 = TestModel()
        m2 = TestModel()
        c1 = TestCollection()
        c1.add(m1)
        c1.add(m2)
        c1.set("k", "v")
        self.assertEqual(m1.get(), {"k": "v"})
        self.assertEqual(m2.get(), {"k": "v"})
        self.assertEqual(c1.get(), [{"k": "v"}, {"k": "v"}])

    def test_unset(self):
        m1 = TestModel()
        m1.set("k", "v")
        self.assertIn("k", m1.attributes)
        m2 = TestModel()
        m2.set("k", "v")
        self.assertIn("k", m2.attributes)
        c1 = TestCollection()
        c1.add(m1)
        c1.add(m2)
        c1.unset("k")
        self.assertEqual(m1.get(), {})
        self.assertEqual(m2.get(), {})

    def test_unset_many(self):
        m1 = TestModel()
        m1.set("k1", "v")
        m1.set("k2", "v")
        m1.set("k3", "v")
        m2 = TestModel()
        m2.set("k1", "v")
        m2.set("k2", "v")
        m2.set("k3", "v")
        c1 = TestCollection()
        c1.add(m1)
        c1.add(m2)
        c1.unset_many(["k1", "k2"])
        self.assertEqual(m1.get(), {"k3": "v"})
        self.assertEqual(m2.get(), {"k3": "v"})

    def test_push(self):
        m1 = TestModel()
        m2 = TestModel()
        c1 = TestCollection()
        c1.add(m1)
        c1.add(m2)
        c1.push("k", "v")
        self.assertEqual(m1.get(), {"k": ["v"]})
        self.assertEqual(m2.get(), {"k": ["v"]})

    def test_push_many(self):
        m1 = TestModel()
        m2 = TestModel()
        c1 = TestCollection()
        c1.add(m1)
        c1.add(m2)
        c1.push_many("k", ["v1", "v2"])
        self.assertEqual(m1.get(), {"k": ["v1", "v2"]})
        self.assertEqual(m2.get(), {"k": ["v1", "v2"]})

    def test_pull(self):
        m1 = TestModel()
        m1.set("k", ["v1", "v2", "v3"])
        m2 = TestModel()
        m2.set("k", ["v1", "v2", "v3"])
        c1 = TestCollection()
        c1.add(m1)
        c1.add(m2)
        c1.pull("k", "v1")
        self.assertEqual(m1.get(), {"k": ["v2", "v3"]})
        self.assertEqual(m2.get(), {"k": ["v2", "v3"]})

    def test_pull_many(self):
        m1 = TestModel()
        m1.set("k", ["v1", "v2", "v3"])
        m2 = TestModel()
        m2.set("k", ["v1", "v2", "v3"])
        c1 = TestCollection()
        c1.add(m1)
        c1.add(m2)
        c1.pull_many("k", ["v1", "v2"])
        self.assertEqual(m1.get(), {"k": ["v3"]})
        self.assertEqual(m2.get(), {"k": ["v3"]})

    def test_delete(self):
        m1 = TestModel()
        m2 = TestModel()
        c1 = TestCollection()
        c1.add(m1)
        c1.add(m2)
        for m in c1:
            self.assertEqual(m._delete, False)

        c1.delete()
        for m in c1:
            self.assertEqual(m._delete, True)

    def test_reset(self):
        m1 = TestModel()
        m1.set("k", "v")
        c1 = TestCollection()
        c1.reset()
        self.assertEqual(c1.target.get(), {})
        self.assertEqual(c1.collection, [])

    def test_save(self):
        m1 = TestModel()
        m1.save()
        m1.set("k", "v1")

        m2 = TestModel()
        m2.set("k", "v2")

        m3 = TestModel()
        m3.save()
        m3.delete()

        c1 = TestCollection()
        c1.add(m1)
        c1.add(m2)
        c1.add(m3)
        c1.save()

        # first model was updated
        m1_copy = TestModel(m1.get(m1.id_attribute))
        m1_copy.find()
        self.assertEqual(m1_copy.get(), {
            m1_copy.id_attribute: m1.get(m1.id_attribute),
            "k": "v1"
        })

        # second model was inserted
        m2_copy = TestModel(m2.get(m2.id_attribute))
        m2_copy.find()
        self.assertEqual(m2_copy.get(), {
            m2_copy.id_attribute: m2.get(m2.id_attribute),
            "k": "v2"
        })

        # third model was deleted
        m3_copy = TestModel(m3.get(m3.id_attribute))
        with self.assertRaises(ModelNotFound):
            m3_copy.find()

        # delete, raise exception ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m4 = TestModel()
        m4.save()
        m4.target = {}
        m4.delete()
        c1 = TestCollection()
        c1.add(m4)
        with self.assertRaises(ModelTargetNotSet):
            c1.save()

    def test_add(self):
        m1 = TestModel()
        c1 = TestCollection()
        c1.add(m1)
        self.assertIn(m1, c1)

        # raise exception ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        with self.assertRaises(CollectionModelClassMismatch):
            TestCollection().add(Model())

        # add model to collection by id ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m2 = TestModel().save()
        m3 = TestModel().save()
        c2 = TestCollection()
        c2.add(m2)
        c2.add(m3)
        c3 = TestCollection()
        c3.add(m2)
        c3.add(m3.get_id())

        self.assertEqual(True, c2 == c3)

    def test_remove(self):
        m1 = TestModel()
        c1 = TestCollection()
        c1.add(m1)
        c1.remove(m1)
        self.assertNotIn(m1, c1)

        # raise exception ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        with self.assertRaises(CollectionModelNotPresent):
            TestCollection().remove(Model())

    def test_dereference_models(self):
        global database_name, collection_name

        # one to many local ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        OTOM1Model, OTOM1Collection = Entity("OTOM1", {
            "mongo_database": database_name,
            "mongo_collection": collection_name,
            "references": {
                "r": {
                    "entity": "OTOM1",
                    "type": "one_to_many"
                }
            }
        })

        m1 = OTOM1Model()
        m1.save()
        m2 = OTOM1Model()
        m2.save()
        m3 = OTOM1Model()

        m3.set("r", [m1.get(m1.id_attribute), m2.get(m2.id_attribute)])
        m3.save()

        m4 = OTOM1Model(m3.get(m3.id_attribute))
        self.assertEqual(m4.attributes.get(), {})

        m4.find(projection={"r": 2})
        self.assertEqual(type(m4.attributes["r"]), OTOM1Collection)
        for m in m4.attributes["r"]:
            self.assertEqual(type(m), OTOM1Model)

        self.tearDown()

        # one to many local, without local key ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        OTOM2Model, OTOM2Collection = Entity("OTOM2", {
            "mongo_database": database_name,
            "mongo_collection": collection_name,
            "references": {
                "r": {
                    "entity": "OTOM2",
                    "type": "one_to_many"
                }
            }
        })

        m1 = OTOM2Model()
        m1.save()
        m2 = OTOM2Model()
        m2.save()
        m3 = OTOM2Model()

        m3.set("r", [m1.get(m1.id_attribute), m2.get(m2.id_attribute)])
        m3.save()

        m4 = OTOM2Model(m3.get(m3.id_attribute))
        self.assertEqual(m4.attributes.get(), {})

        m4.find(projection={"r": 2})
        self.assertEqual(type(m4.attributes["r"]), OTOM2Collection)
        for m in m4.attributes["r"]:
            self.assertEqual(type(m), OTOM2Model)

        self.tearDown()

        # one to many local, without foreign key ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        OTOM3Model, OTOM3Collection = Entity("OTOM3", {
            "mongo_database": database_name,
            "mongo_collection": collection_name,
            "references": {
                "r": {
                    "entity": "OTOM3",
                    "type": "one_to_many"
                }
            }
        })

        m1 = OTOM3Model()
        m1.save()
        m2 = OTOM3Model()
        m2.save()
        m3 = OTOM3Model()

        m3.set("r", [m1.get(m1.id_attribute), m2.get(m2.id_attribute)])
        m3.save()

        m4 = OTOM3Model(m3.get(m3.id_attribute))
        self.assertEqual(m4.attributes.get(), {})

        m4.find(projection={"r": 2})
        self.assertEqual(type(m4.attributes["r"]), OTOM3Collection)
        for m in m4.attributes["r"]:
            self.assertEqual(type(m), OTOM3Model)

        self.tearDown()

        # one to many local, projection ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        OTOM4Model, OTOM4Collection = Entity("OTOM4", {
            "mongo_database": database_name,
            "mongo_collection": collection_name,
            "references": {
                "r": {
                    "entity": "OTOM4",
                    "type": "one_to_many"
                }
            }
        })

        m5 = OTOM4Model()
        m5.set("k1", "v")
        m5.set("k2", "v")
        m5.set("k3", "v")
        m5.save()

        m6 = OTOM4Model()
        m6.set("k1", "v")
        m6.set("k2", "v")
        m6.set("k3", "v")
        m6.save()

        m7 = OTOM4Model()
        m7.set("r", [m5.get(m5.id_attribute), m6.get(m6.id_attribute)])
        m7.save()
        m8 = OTOM4Model(m7.get(m7.id_attribute))
        self.assertEqual(m8.attributes.get(), {})

        m8.find(projection={"r": {"k2": 0}})
        for m in m8.ref("r"):
            self.assertIn("k1", m.attributes)
            self.assertNotIn("k2", m.attributes)
            self.assertIn("k3", m.attributes)

        self.tearDown()

        # one to many local, relationship resolution error ~~~~~~~~~~~~~~~~~~~~
        OTML5Model, OTML5Collection = Entity("OTML5", {
            "mongo_database": database_name,
            "mongo_collection": collection_name,
            "references": {
                "r": {
                    "entity": "OTML5",
                    "type": "one_to_many"
                }
            }

        })

        m9 = OTML5Model()
        m9.save()

        m10 = OTML5Model()
        m10.set("r", [m9.get(m9.id_attribute)])
        m10.save()

        m9.delete()
        m9.save()

        m11 = OTML5Model(m10.get(m10.id_attribute))
        self.assertEqual(m11.attributes.get(), {})

        m11.find(projection={"r": 2})
        for m in m11.ref("r"):
            self.assertEqual(type(m), DereferenceError)

        self.tearDown()

        # many to many local ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        MTML1Model, MTML1Collection = Entity("MTML1", {
            "mongo_database": database_name,
            "mongo_collection": collection_name,
            "references": {
                "r": {
                    "entity": "MTML1",
                    "type": "many_to_many"
                }
            }
        })

        m12 = MTML1Model()
        m12.save()
        m13 = MTML1Model()
        m13.save()
        m14 = MTML1Model()
        m14.set("r", [m12.get(m12.id_attribute), m13.get(m13.id_attribute)])
        m14.save()
        m15 = MTML1Model()
        m15.set("r", [m12.get(m12.id_attribute), m13.get(m13.id_attribute)])
        m15.save()
        m16 = MTML1Model(m14.get(m14.id_attribute))
        m16.find(projection={"r": 2})
        self.assertEqual(len(m16.ref("r")), 2)
        for m in m16.ref("r"):
            self.assertEqual(type(m), MTML1Model)

        self.tearDown()

        # one to many foreign ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        OTMF1Model, OTMF1Collection = Entity("OTMF1", {
            "mongo_database": database_name,
            "mongo_collection": collection_name,
            "references": {
                "foo": {
                    "entity": "OTMF1",
                    "type": "one_to_many",
                    "foreign_key": "bar"
                }
            }
        })

        m17 = OTMF1Model()
        m17.save()
        m18 = OTMF1Model()

        m18.set("bar", m17.get(m17.id_attribute))
        m18.save()
        m19 = OTMF1Model()
        m19.set("bar", m17.get(m17.id_attribute))
        m19.save()

        m20 = OTMF1Model(m19.get(m19.id_attribute))

        m20.find(projection={"foo": 2})

        for m in m20.ref("foo"):
            self.assertEqual(type(m), OTMF1Model())

        self.tearDown()

        # one to many foreign, projection ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        OTMF5Model, OTMF5Collection = Entity("OTMF5", {
            "mongo_database": database_name,
            "mongo_collection": collection_name,
            "references": {
                "foo": {
                    "entity": "OTMF5",
                    "type": "one_to_many"
                }
            }
        })

        m21 = OTMF5Model()
        m21.set({"k1": "v", "k2": "v", "k3": "v"})
        m21.save()
        m22 = OTMF5Model()
        m22.set("bar", m21.get(m21.id_attribute))
        m22.set({"k1": "v", "k2": "v", "k3": "v"})
        m22.save()
        m23 = OTMF5Model()
        m23.set("bar", m21.get(m21.id_attribute))
        m23.set({"k1": "v", "k2": "v", "k3": "v"})
        m23.save()

        m24 = OTMF5Model(m21.get(m21.id_attribute))
        m24.find(projection={"foo": {"k1": 1, "k2": 1}})

        self.assertEqual(type(m24.attributes["foo"]), OTMF5Collection)
        for m in m24.ref("foo"):
            self.assertIn("k1", m.get())
            self.assertIn("k2", m.get())
            self.assertNotIn("k3", m.get())

        self.tearDown()

        # many to many foreign ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        MTMF1Model, MTMF1Collection = Entity("MTMF1", {
            "mongo_database": database_name,
            "mongo_collection": collection_name,
            "references": {
                "foo": {
                    "entity": "MTMF1",
                    "type": "many_to_many"
                }
            }
        })

        m25 = MTMF1Model()
        m25.save()
        m26 = MTMF1Model()
        m26.save()
        m27 = MTMF1Model()
        m27.set("bar", [m25.get(m25.id_attribute)])
        m27.save()
        m28 = MTMF1Model()
        m28.set("bar", [m25.get(m25.id_attribute), m26.get(m26.id_attribute)])
        m28.save()

        m29 = MTMF1Model(m28.get(m28.id_attribute))
        m29.find(projection={"foo": 2})

        self.assertEqual(type(m29.ref("foo")), MTMF1Collection)
        for m in m29.ref("foo"):
            self.assertEqual(type(m), MTMF1Model)

        self.tearDown()

        # many to many foreign, projection ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        MTMF3Model, MTMF3Collection = Entity("MTMF3", {
            "mongo_database": database_name,
            "mongo_collection": collection_name,
            "references": {
                "foo": {
                    "entity": "MTMF3",
                    "type": "many_to_many",
                    "foreign_key": "bar"
                }
            }
        })

        m30 = MTMF3Model()
        m30.save()
        m31 = MTMF3Model()
        m31.save()

        m32 = MTMF3Model()
        m32.set("bar", [m30.get(m30.id_attribute)])
        m32.set({"k1": "v", "k2": "v", "k3": "v"})
        m32.save()

        m33 = MTMF3Model()
        m33.set("bar", [m30.get(m30.id_attribute), m31.get(m31.id_attribute)])
        m33.set({"k1": "v", "k2": "v", "k3": "v"})
        m33.save()

        m34 = MTMF3Model(m30.get(m30.id_attribute))
        m34.find(projection={"foo": {"k1": 1}})
        self.assertEqual(type(m34.ref("foo")), MTMF3Collection)
        for m in m34.ref("foo"):
            self.assertIn("k1", m.get())
            self.assertNotIn("k2", m.get())
            self.assertNotIn("k3", m.get())

        self.tearDown()

    def test_reference_models(self):
        m1 = TestModel()
        m1.save()
        m2 = TestModel()
        m2.save()
        c1 = TestCollection()
        c1.add(m1)
        c1.add(m2)
        m3 = TestModel()
        m3.set("r", c1)
        data = m3.reference_models(m3.attributes)
        self.assertIn("r", data)
        for v in data["r"]:
            self.assertEqual(type(v), bson.objectid.ObjectId)

    def test_hooks(self):

        # pre find hook ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class PFH1Abstract(object):
            def pre_find_hook(self):
                m = self.__entity__["model"]()
                m.set("unique_key", "unique_value")
                self.add(m)

        PFH1Model, PFH1Collection = Entity("PFH1", {
            "mongo_database": database_name,
            "mongo_collection": collection_name
        }, {
            "methods": PFH1Abstract
        })

        c1 = PFH1Collection()
        c1.find()

        self.assertEqual(len(c1), 1)
        self.assertEqual(type(c1.collection[0]), PFH1Model)

        self.tearDown()

        # post find hook ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        PFH2Model, PFH2Collection = Entity("PFH2", {
            "mongo_database": database_name,
            "mongo_collection": collection_name
        })

        class PFH3Abstract(object):
            def post_find_hook(self):
                self.collection = []

        PFH3Model, PFH3Collection = Entity("PFH3", {
            "mongo_database": database_name,
            "mongo_collection": collection_name
        }, {
            "methods": PFH3Abstract
        })

        m1 = PFH2Model()
        m1.save()
        m2 = PFH2Model()
        m2.save()
        m3 = PFH2Model()
        m3.save()

        c2 = PFH2Collection()
        c2.find()
        self.assertEqual(len(c2), 3)

        c3 = PFH3Collection()
        c3.find()
        self.assertEqual(len(c3), 0)

        self.tearDown()

        # pre modify hook ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class PMH1Abstract(object):
            def pre_modify_hook(self):
                m = self.__entity__["model"]()
                m.set("k", "hook_v")
                self.add(m)

        PMH1Model, PMH1Collection = Entity("PMH1", {
            "mongo_database": database_name,
            "mongo_collection": collection_name
        }, {
            "methods": PMH1Abstract
        })

        m4 = PMH1Model()
        m4.set("k", "v")
        m4 = PMH1Model()
        c1 = PMH1Collection()
        c1.add(m4)
        c1.save()
        self.assertEqual(len(c1), 2)
        for m in c1:
            self.assertIn(m.id_attribute, m.attributes)

        self.tearDown()

        # post modify hook ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class PMH2Abstract(TestCollection):
            def post_modify_hook(self):
                self.collection = []

        PMH2Model, PMH2Collection = Entity("PMH2", {
            "mongo_database": database_name,
            "mongo_collection": collection_name
        }, {
            "methods": PMH2Abstract
        })

        m1 = PMH2Model()
        m1.set("k", "v")
        m2 = PMH2Model()
        m2.set("k", "v")
        m3 = PMH2Model()
        m3.set("k", "v")
        c = PMH2Collection()
        c.add(m1)
        c.add(m2)
        c.add(m3)
        self.assertEqual(len(c), 3)

        c.save()
        self.assertEqual(len(c), 0)

        self.tearDown()

        # model find hooks ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class MFH1Abstract(object):
            def pre_find_hook(self):
                pass

            def post_find_hook(self):
                pass

        MFH1Model, MFH1Collection = Entity("MFH1", {
            "mongo_database": database_name,
            "mongo_collection": collection_name,
            "methods": MFH1Abstract
        })

        m8 = MFH1Model()
        m8.save()
        c6 = MFH1Collection()
        c6.set_target(m8.get(m8.id_attribute))
        c6.find()

        self.tearDown()

        # model insert hooks ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class MFH2Abstract(object):
            def pre_insert_hook(self):
                pass

            def post_insert_hook(self):
                pass

        MFH2Model, MFH2Collection = Entity("MFH2", {
            "mongo_database": database_name,
            "mongo_collection": collection_name,
            "methods": MFH2Abstract
        })

        c = MFH2Collection()
        c.add(MFH2Model())
        c.save()

        self.tearDown()

        # model update hooks ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class MUH1Abstract(TestModel):
            def pre_update_hook(self):
                pass

            def post_update_hook(self):
                pass

        MUH1Model, MUH1Collection = Entity("MUH1", {
            "mongo_database": database_name,
            "mongo_collection": collection_name,
            "methods": MUH1Abstract
        })

        mymodel = MUH1Model()
        mymodel.save()

        c = MUH1Collection()
        c.add(mymodel)
        c.set("key", "value")
        c.save()

        self.tearDown()

        # model delete hooks ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class MDH1Abstract(TestModel):
            def pre_delete_hook(self):
                pass

            def post_delete_hook(self):
                pass

        MDH1Model, MDH1Collection = Entity("MDH1", {
            "mongo_database": database_name,
            "mongo_collection": collection_name,
            "methods": MDH1Abstract
        })

        mymodel = MDH1Model()
        mymodel.save()

        c = MDH1Collection()
        c.add(mymodel)
        c.delete()
        c.save()

        self.tearDown()


if __name__ == "__main__":
    unittest.main()
