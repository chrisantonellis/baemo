
import sys; sys.path.append("../")

import unittest
import copy
import pymongo
import bson

from collections import OrderedDict

from baemo.connection import Connections
from baemo.sort import Sort
from baemo.model import Model
from baemo.collection import Collection
from baemo.entity import Entity

from baemo.exceptions import ModelNotFound
from baemo.exceptions import ModelTargetNotSet
from baemo.exceptions import CollectionModelClassMismatch
from baemo.exceptions import CollectionModelNotPresent
from baemo.exceptions import DereferenceError


class TestCollection(unittest.TestCase):

    def setUp(self):
        global connection_name, collection_name, TestModel, TestCollection
        connection_name = "baemo"
        collection_name = "{}_{}".format(
            self.__class__.__name__,
            self._testMethodName
        )

        connection = pymongo.MongoClient(connect=False)[connection_name]
        Connections.set(connection_name, connection)

        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name
        })

    def tearDown(self):
        global connection_name, collection_name
        Connections.get(connection_name).drop_collection(collection_name)

    # __init__

    def test___init__(self):
        c = Collection()
        self.assertEqual(c.models, [])

        self.assertEqual(c.target.get(), {})
        self.assertEqual(c.sort, Sort())

        self.assertEqual(c.find_projection.get(), {})
        self.assertEqual(c.get_projection.get(), {})

    def test___init____target_param(self):
        c = TestCollection({"foo": "bar"})
        self.assertEqual(c.target.get(), {"foo": "bar"})

    # __copy__

    def test___copy__(self):
        c = TestCollection()
        c.add(TestModel())
        _copy = copy.copy(c)
        self.assertIsNot(c, _copy)
        self.assertEqual(c.models, _copy.models)

        _copy.models.append(TestModel())
        self.assertEqual(c.models, _copy.models)

    # __deepcopy__

    def test___deepcopy__(self):
        c = TestCollection()
        c.add(TestModel())
        _copy = copy.deepcopy(c)
        self.assertIsNot(c, _copy)
        self.assertEqual(c.models, _copy.models)

        _copy.models.append(TestModel())
        self.assertNotEqual(c.models, _copy.models)

    # __eq__

    def test___eq____same_models__returns_True(self):
        c1 = TestCollection()
        c2 = TestCollection()
        self.assertTrue(c1 == c2)

    def test___eq____different_models__returns_False(self):
        c1 = TestCollection()
        c2 = TestCollection()
        c2.models.append(TestModel())
        self.assertFalse(c1 == c2)

    # __ne__

    def test___ne____same_models__returns_False(self):
        c1 = TestCollection()
        c2 = TestCollection()
        self.assertFalse(c1 != c2)

    def test___ne____different_models__returns_True(self):
        c1 = TestCollection()
        c2 = TestCollection()
        c2.models.append(TestModel())
        self.assertTrue(c1 != c2)

    # __len__

    def test___len__(self):
        c = TestCollection()
        self.assertEqual(len(c), 0)
        c.models.append(TestModel())
        c.models.append(TestModel())
        c.models.append(TestModel())
        self.assertEqual(len(c), 3)

    # __iter__

    def test___iter__(self):
        c = TestCollection()
        c.add(TestModel())
        c.add(TestModel())
        c.add(TestModel())
        for m in c:
            self.assertEqual(type(m), TestModel)

    # __setitem__

    def test___setitem__(self):
        c = TestCollection()
        m1 = TestModel()
        c.add(m1)
        m2 = TestModel()
        c[0] = m2
        self.assertEqual(c.models, [m2])

        with self.assertRaises(CollectionModelClassMismatch):
            c[0] = Model()

    # __getitem__

    def test___getitem__(self):
        m = TestModel()
        c = TestCollection()
        c.add(m)
        self.assertEqual(c[0], m)

    # __delitem__

    def test___delitem__(self):
        m = TestModel()
        c = TestCollection()
        c.add(m)
        del c[0]
        self.assertEqual(c.models, [])

    # __reversed__

    def test___reversed__(self):
        m1 = TestModel()
        m2 = TestModel()
        m3 = TestModel()
        c = TestCollection()
        c.add(m1)
        c.add(m2)
        c.add(m3)
        self.assertEqual(c.models, [m1, m2, m3])
        self.assertEqual(list(reversed(c)), [m3, m2, m1])

    # set_target

    def test_set_target__string_param__sets_iterator__id_key(self):
        c = TestCollection()
        c.set_target("v")
        self.assertEqual(c.target.get(), {"_id": {"$in": ["v"]}})

    def test_set_target__string_and_key_params__sets_iterator__custom_key(self):
        c = TestCollection()
        c.set_target("v", key="k")
        self.assertEqual(c.target.get(), {"k": {"$in": ["v"]}})

    def test_set_target__list_param__sets_iterator__id_key(self):
        c = TestCollection()
        c.set_target(["v1", "v2", "v3"])
        self.assertEqual(c.target.get(), {"_id": {"$in": ["v1", "v2", "v3"]}})

    def test_set_Target__list_and_key_param__sets_iterator__custom_key(self):
        c = TestCollection()
        c.set_target(["v1", "v2", "v3"], key="k")
        self.assertEqual(c.target.get(), {"k": {"$in": ["v1", "v2", "v3"]}})

    def test_set_target__dict_param(self):
        c = TestCollection()
        c.set_target({"k": "v"})
        self.assertEqual(c.target.get(), {"k": "v"})

    # get_target

    def test_get_target(self):
        c = TestCollection()
        self.assertEqual(c.get_target(), None)
        c.set_target({"k": "v"})
        self.assertEqual(c.get_target(), {"k": "v"})

    # get_targets

    def test_get_targets(self):
        m1 = Model(bson.objectid.ObjectId())
        m2 = Model(bson.objectid.ObjectId())
        c = TestCollection()
        c.collection = [m1, m2]
        targets = c.get_targets()
        self.assertEqual(type(targets), list)
        for t in targets:
            self.assertEqual(type(t), dict)

    # get_ids

    def test_get_ids(self):
        m1 = Model(bson.objectid.ObjectId())
        m2 = Model(bson.objectid.ObjectId())
        c = TestCollection()
        c.collection = [m1, m2]
        ids = c.get_ids()
        self.assertEqual(type(ids), list)

        for id_ in ids:
            self.assertEqual(type(id_), bson.objectid.ObjectId)

    # find

    def test_find__target_not_set(self):
        m1 = TestModel()
        m1.save()
        m2 = TestModel()
        m2.save()
        c = TestCollection()
        self.assertEqual(c.target.get(), {})
        c.find()
        self.assertEqual(len(c), 2)

        for m in c:
            self.assertEqual(type(m), TestModel)

    def test_find__target_set(self):
        m1 = TestModel()
        m1.set("k", "v1")
        m1.save()
        m2 = TestModel()
        m2.set("k", "v2")
        m2.save()
        c = TestCollection()
        c.set_target({"k": "v2"})
        c.find()
        self.assertEqual(len(c), 1)
        self.assertEqual(c.models[0], m2)

    def test_find__projection_param(self):
        m1 = TestModel()
        m1.set("k1", "v")
        m1.set("k2", "v")
        m1.set("k3", "v")
        m1.save()
        m2 = TestModel()
        m2.set("k1", "v")
        m2.set("k2", "v")
        m2.set("k3", "v")
        m2.save()
        c = TestCollection()
        c.find(projection={"k2": 1})
        self.assertEqual(len(c.models), 2)
        for m in c:
            self.assertEqual(type(m), TestModel)
            self.assertNotIn("k1", m.attributes.get())
            self.assertIn("k2", m.attributes.get())
            self.assertNotIn("k3", m.attributes.get())

    def test_find__target_set__projection_param(self):
        m1 = TestModel()
        m1.set("k1", "v1")
        m1.set("k2", "v1")
        m1.set("k3", "v1")
        m1.save()
        m2 = TestModel()
        m2.set("k1", "v2")
        m2.set("k2", "v2")
        m2.set("k3", "v2")
        m2.save()
        c = TestCollection({"k1": "v1"})
        c.find(projection={"k3": 0})
        self.assertEqual(len(c.models), 1)
        for m in c:
            self.assertEqual(type(m), TestModel)
            self.assertIn("k1", m.attributes.get())
            self.assertIn("k2", m.attributes.get())
            self.assertNotIn("k3", m.attributes.get())

    def test_find__target_with_iterator(self):
        m1 = TestModel()
        m1.set("k", ["v1", "v2"])
        m1.save()
        m2 = TestModel()
        m2.set("k", ["v1"])
        m2.save()
        c = TestCollection()
        c.set_target("v2", key="k")
        c.find()
        self.assertEqual(len(c.models), 1)
        for m in c:
            self.assertEqual(type(m), TestModel)
            self.assertEqual(m.get("k"), ["v1", "v2"])

    def test_find__default_get_projection(self):
        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name,
        }, {
            "get_projection": {
                "k1": 0
            }
        })

        m = TestModel()
        m.set({"k1": "v", "k2": "v", "k3": "v"})
        m.save()
        c = TestCollection()
        c.set_target(m.get_id())
        c.find()

        for m in c.get():
            self.assertNotIn("k1", m)
            self.assertIn("k2", m)
            self.assertIn("k3", m)

    def test_find__default_find_projection(self):
        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name
        }, {
            "find_projection": {
                "k1": 0
            }
        })

        m = TestModel()
        m.set({"k1": "v", "k2": "v", "k3": "v"})
        m.save()
        c = TestCollection()
        c.set_target(m.get_id())
        c.find()

        for m in c:
            self.assertNotIn("k1", m.get())
            self.assertIn("k2", m.get())
            self.assertIn("k3", m.get())

    def test_find__default_model_projection(self):
        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name,
            "find_projection": {
                "k1": 1
            }
        })

        m = TestModel()
        m.set({"k1": "v", "k2": "v", "k3": "v"})
        m.save()
        c = TestCollection()
        c.find(default_model_projection=True)
        self.assertEqual(c.get(), [{
            m.id_attribute: m.get(m.id_attribute),
            "k1": "v"
        }])

    def test_find__default_sort(self):
        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name
        }, {
            "sort": [("k2", 1)]
        })

        m1 = TestModel()
        m1.set({"k1": "v1", "k2": 2, "k3": "v1"})
        m1.save()
        m2 = TestModel()
        m2.set({"k1": "v2", "k2": 3, "k3": "v2"})
        m2.save()
        m3 = TestModel()
        m3.set({"k1": "v3", "k2": 1, "k3": "v3"})
        m3.save()
        c = TestCollection()
        c.find()

        self.assertEqual(c.get(), [
            {
                m3.id_attribute: m3.get(m3.id_attribute),
                "k1": "v3",
                "k2": 1,
                "k3": "v3"
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

    def test_find__sort_param(self):
        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name
        })

        m1 = TestModel()
        m1.set({"k1": "v1", "k2": 2, "k3": "v1"})
        m1.save()
        m2 = TestModel()
        m2.set({"k1": "v2", "k2": 3, "k3": "v2"})
        m2.save()
        m3 = TestModel()
        m3.set({"k1": "v3", "k2": 1, "k3": "v3"})
        m3.save()
        c = TestCollection()
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

    def test_find__default_limit(self):
        TestModel, TestCollection = Entity("DL", {
            "connection": connection_name,
            "collection": collection_name
        }, {
            "limit": 2
        })

        m1 = TestModel()
        m1.set({"k": "v"})
        m1.save()
        m2 = TestModel()
        m2.set({"k": "v"})
        m2.save()
        m3 = TestModel()
        m3.set({"k": "v"})
        m3.save()
        c = TestCollection()
        c.find()

        self.assertEqual(len(c.get()), 2)

    def test_find__limit_param(self):
        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name
        })

        m1 = TestModel()
        m1.set({"k": "v"})
        m1.save()
        m2 = TestModel()
        m2.set({"k": "v"})
        m2.save()
        m3 = TestModel()
        m3.set({"k": "v"})
        m3.save()
        c = TestCollection()
        c.find(limit=2)

        self.assertEqual(len(c.get()), 2)

    def test_find__default_skip(self):
        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name
        }, {
            "skip": 2
        })

        m1 = TestModel()
        m1.set({"k": "v1"})
        m1.save()
        m2 = TestModel()
        m2.set({"k": "v2"})
        m2.save()
        m3 = TestModel()
        m3.set({"k": "v3"})
        m3.save()
        c = TestCollection()
        c.find()

        self.assertEqual(len(c.get()), 1)
        for m in c:
            self.assertEqual(m.get("k"), "v3")

    def test_find__skip_param(self):
        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name
        })

        m1 = TestModel()
        m1.set({"k": "v1"})
        m1.save()
        m2 = TestModel()
        m2.set({"k": "v2"})
        m2.save()
        m3 = TestModel()
        m3.set({"k": "v3"})
        m3.save()
        c = TestCollection()
        c.find(skip=2)

        self.assertEqual(len(c.get()), 1)
        for m in c:
            self.assertEqual(m.get("k"), "v3")

    def test_find__total_count(self):
        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name
        })

        m1 = TestModel()
        m1.set({"k": "v1"})
        m1.save()
        m2 = TestModel()
        m2.set({"k": "v2"})
        m2.save()
        m3 = TestModel()
        m3.set({"k": "v3"})
        m3.save()
        c = TestCollection()
        c.find(skip=2)

        self.assertEqual(c.total_count, 3)

    # ref

    def test_ref(self):
        m = TestModel()
        m.set("k", "v")
        c = TestCollection()
        c.add(m)
        self.assertEqual(c.ref()[0], m.attributes.get())

    # has

    def test_has(self):
        m1 = Model()
        m1.set("k", "v")
        m2 = Model()
        c = Collection()
        c.models.append(m1)
        c.models.append(m2)
        self.assertEqual(c.has("k"), [True, False])

    # get

    def test_get__no_params(self):
        m1 = TestModel()
        m1.set("k", "v")
        m2 = TestModel()
        m2.set("k", "v")
        c1 = TestCollection()
        c1.add(m1)
        c1.add(m2)
        self.assertEqual(c1.get(), [{"k": "v"}, {"k": "v"}])

    def test_get__string_param(self):
        m1 = TestModel()
        m1.set("k1", "v")
        m1.set("k2", "v")
        m2 = TestModel()
        m2.set("k1", "v")
        m2.set("k2", "v")
        c = TestCollection()
        c.add(m1)
        c.add(m2)
        self.assertEqual(c.get("k2"), ["v", "v"])

    def test_get__projection_param(self):
        m = TestModel()
        m.set({"k1": "v", "k2": "v", "k3": "v"})
        c = TestCollection()
        c.add(m)
        self.assertEqual(c.get(projection={"k1": 1}), [{"k1": "v"}])

    # set

    def test_set(self):
        m1 = TestModel()
        m2 = TestModel()
        c = TestCollection()
        c.add(m1)
        c.add(m2)
        c.set("k", "v")
        self.assertEqual(m1.get(), {"k": "v"})
        self.assertEqual(m2.get(), {"k": "v"})
        self.assertEqual(c.get(), [{"k": "v"}, {"k": "v"}])

    # unset

    def test_unset(self):
        m1 = TestModel()
        m1.set("k", "v")
        self.assertIn("k", m1.attributes)
        m2 = TestModel()
        m2.set("k", "v")
        self.assertIn("k", m2.attributes)
        c = TestCollection()
        c.add(m1)
        c.add(m2)
        c.unset("k")
        self.assertEqual(m1.get(), {})
        self.assertEqual(m2.get(), {})

    # unset_many

    def test_unset_many(self):
        m1 = TestModel()
        m1.set("k1", "v")
        m1.set("k2", "v")
        m1.set("k3", "v")
        m2 = TestModel()
        m2.set("k1", "v")
        m2.set("k2", "v")
        m2.set("k3", "v")
        c = TestCollection()
        c.add(m1)
        c.add(m2)
        c.unset_many(["k1", "k2"])
        self.assertEqual(m1.get(), {"k3": "v"})
        self.assertEqual(m2.get(), {"k3": "v"})

    # push

    def test_push(self):
        m1 = TestModel()
        m2 = TestModel()
        c = TestCollection()
        c.add(m1)
        c.add(m2)
        c.push("k", "v")
        self.assertEqual(m1.get(), {"k": ["v"]})
        self.assertEqual(m2.get(), {"k": ["v"]})

    # push_many

    def test_push_many(self):
        m1 = TestModel()
        m2 = TestModel()
        c = TestCollection()
        c.add(m1)
        c.add(m2)
        c.push_many("k", ["v1", "v2"])
        self.assertEqual(m1.get(), {"k": ["v1", "v2"]})
        self.assertEqual(m2.get(), {"k": ["v1", "v2"]})

    # pull

    def test_pull(self):
        m1 = TestModel()
        m1.set("k", ["v1", "v2", "v3"])
        m2 = TestModel()
        m2.set("k", ["v1", "v2", "v3"])
        c = TestCollection()
        c.add(m1)
        c.add(m2)
        c.pull("k", "v1")
        self.assertEqual(m1.get(), {"k": ["v2", "v3"]})
        self.assertEqual(m2.get(), {"k": ["v2", "v3"]})

    # pull_many

    def test_pull_many(self):
        m1 = TestModel()
        m1.set("k", ["v1", "v2", "v3"])
        m2 = TestModel()
        m2.set("k", ["v1", "v2", "v3"])
        c = TestCollection()
        c.add(m1)
        c.add(m2)
        c.pull_many("k", ["v1", "v2"])
        self.assertEqual(m1.get(), {"k": ["v3"]})
        self.assertEqual(m2.get(), {"k": ["v3"]})

    # delete

    def test_delete(self):
        m1 = TestModel()
        m2 = TestModel()
        c = TestCollection()
        c.add(m1)
        c.add(m2)
        for m in c:
            self.assertEqual(m._delete, False)

        c.delete()
        for m in c:
            self.assertEqual(m._delete, True)

    # reset

    def test_reset(self):
        m1 = TestModel()
        m1.set("k", "v")
        c = TestCollection()
        c.reset()
        self.assertEqual(c.target.get(), {})
        self.assertEqual(c.models, [])

    # save

    def test_save__insert(self):
        m = TestModel()
        m.set("k", "v")
        c = TestCollection()
        c.add(m)
        c.save()

        _copy = TestModel(m.get(m.id_attribute))
        _copy.find()
        self.assertEqual(_copy.get(), {
            "_id": m.get("_id"),
            "k": "v"
        })

    def test_save__update(self):
        pass

    def test_save__delete(self):
        global TestModel, TestCollection

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

    # add

    def test_add(self):
        global TestModel, TestCollection

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

    # remove

    def test_remove(self):
        m = TestModel()
        c = TestCollection()
        c.add(m)
        c.remove(m)
        self.assertNotIn(m, c)

    def test_remove__raises_CollectionModelNotPresent(self):
        with self.assertRaises(CollectionModelNotPresent):
            TestCollection().remove(Model())

    # dereference_entities

    def test_dereference_entities__local_many(self):
        global connection_name, collection_name

        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name,
            "references": {
                "r": {
                    "entity": "Test",
                    "type": "local_many",
                    "foreign_key": "_id"
                }
            }
        })

        m1 = TestModel()
        m1.save()
        m2 = TestModel()
        m2.save()
        m3 = TestModel()

        m3.set("r", [m1.get(m1.id_attribute), m2.get(m2.id_attribute)])
        m3.save()

        m4 = TestModel(m3.get(m3.id_attribute))
        self.assertEqual(m4.attributes.get(), {})

        m4.find(projection={"r": 2})
        self.assertEqual(type(m4.attributes["r"]), TestCollection)
        for m in m4.attributes["r"]:
            self.assertEqual(type(m), TestModel)

    def test_dereference_entities__local_many__projection_param(self):
        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name,
            "references": {
                "r": {
                    "entity": "Test",
                    "type": "local_many"
                }
            }
        })

        m1 = TestModel()
        m1.set("k1", "v")
        m1.set("k2", "v")
        m1.set("k3", "v")
        m1.save()

        m2 = TestModel()
        m2.set("k1", "v")
        m2.set("k2", "v")
        m2.set("k3", "v")
        m2.save()

        m3 = TestModel()
        m3.set("r", [m1.get(m1.id_attribute), m2.get(m2.id_attribute)])
        m3.save()
        m4 = TestModel(m3.get(m3.id_attribute))
        self.assertEqual(m4.attributes.get(), {})

        m4.find(projection={"r": {"k2": 0}})
        for m in m4.ref("r"):
            self.assertIn("k1", m.attributes)
            self.assertNotIn("k2", m.attributes)
            self.assertIn("k3", m.attributes)

    def test_dereference_entities__local_many__dereference_error(self):
        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name,
            "references": {
                "r": {
                    "entity": "Test",
                    "type": "local_many"
                }
            }

        })

        m1 = TestModel()
        m1.save()

        m2 = TestModel()
        m2.set("r", [m1.get(m1.id_attribute)])
        m2.save()

        m1.delete()
        m1.save()

        m3 = TestModel(m2.get(m2.id_attribute))
        self.assertEqual(m3.attributes.get(), {})

        m3.find(projection={"r": 2})
        for m in m3.ref("r"):
            self.assertEqual(type(m), DereferenceError)

    def test_dereference_entities__foreign_many(self):
        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name,
            "references": {
                "foo": {
                    "entity": "Test",
                    "type": "foreign_many",
                    "foreign_key": "bar"
                }
            }
        })

        m1 = TestModel()
        m1.save()
        m2 = TestModel()

        m2.set("bar", m1.get(m1.id_attribute))
        m2.save()
        m3 = TestModel()
        m3.set("bar", m1.get(m1.id_attribute))
        m3.save()

        m4 = TestModel(m3.get(m3.id_attribute))

        m4.find(projection={"foo": 2})

        for m in m4.ref("foo"):
            self.assertEqual(type(m), TestModel())

    def test_dereference_entities__foreign_many__projection_param(self):
        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name,
            "references": {
                "foo": {
                    "entity": "Test",
                    "type": "foreign_many"
                }
            }
        })

        m1 = TestModel()
        m1.set({"k1": "v", "k2": "v", "k3": "v"})
        m1.save()
        m2 = TestModel()
        m2.set("bar", m1.get(m1.id_attribute))
        m2.set({"k1": "v", "k2": "v", "k3": "v"})
        m2.save()
        m3 = TestModel()
        m3.set("bar", m1.get(m1.id_attribute))
        m3.set({"k1": "v", "k2": "v", "k3": "v"})
        m3.save()

        m4 = TestModel(m1.get(m1.id_attribute))
        m4.find(projection={"foo": {"k1": 1, "k2": 1}})

        self.assertEqual(type(m4.attributes["foo"]), TestCollection)
        for m in m4.ref("foo"):
            self.assertIn("k1", m.get())
            self.assertIn("k2", m.get())
            self.assertNotIn("k3", m.get())

    # reference_entities

    def test_reference_entities(self):
        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name,
            "references": {
                "r": {
                    "entity": "Test",
                    "type": "local_many"
                }
            }
        })

        m1 = TestModel()
        m1.save()
        m2 = TestModel()
        m2.save()
        c = TestCollection()
        c.add(m1)
        c.add(m2)
        m3 = TestModel()
        m3.set("r", c)
        data = m3.reference_entities(m3.attributes)
        self.assertIn("r", data)
        for v in data["r"]:
            self.assertEqual(type(v), bson.objectid.ObjectId)

    # pre_find_hook

    def test_pre_find_hook(self):
        class ModelAbstract(object):
            def pre_find_hook(self):
                m = self.__entity__["model"]()
                m.set("unique_key", "unique_value")
                self.add(m)

        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name
        }, {
            "bases": ModelAbstract
        })

        c = TestCollection()
        c.find()

        self.assertEqual(len(c), 1)
        self.assertEqual(type(c.models[0]), TestModel)

    def test_post_find_hook(self):
        class CollectionAbstract(object):
            def post_find_hook(self):
                self.models = []

        TestModel2, TestCollection2 = Entity("Test2", {
            "connection": connection_name,
            "collection": collection_name
        }, {
            "bases": CollectionAbstract
        })

        m1 = TestModel()
        m1.save()
        m2 = TestModel()
        m2.save()
        m3 = TestModel()
        m3.save()

        c2 = TestCollection()
        c2.find()
        self.assertEqual(len(c2), 3)

        c3 = TestCollection2()
        c3.find()
        self.assertEqual(len(c3), 0)

    def test_pre_modify_hook(self):
        class CollectionAbstract(object):
            def pre_modify_hook(self):
                m = self.__entity__["model"]()
                m.set("k", "hook_v")
                self.add(m)

        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name
        }, {
            "bases": CollectionAbstract
        })

        m1 = TestModel()
        m1.set("k", "v")
        m1 = TestModel()
        c = TestCollection()
        c.add(m1)
        c.save()
        self.assertEqual(len(c), 2)
        for m in c:
            self.assertIn(m.id_attribute, m.attributes)

    def test_post_modify_hook(self):
        class CollectionAbstract(object):
            def post_modify_hook(self):
                self.models = []

        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name
        }, {
            "bases": CollectionAbstract
        })

        m1 = TestModel()
        m1.set("k", "v")
        m2 = TestModel()
        m2.set("k", "v")
        m3 = TestModel()
        m3.set("k", "v")
        c = TestCollection()
        c.add(m1)
        c.add(m2)
        c.add(m3)
        self.assertEqual(len(c), 3)

        c.save()
        self.assertEqual(len(c), 0)

    def test_model_find_hook(self):
        class ModelAbstract(object):
            def pre_find_hook(self):
                pass

            def post_find_hook(self):
                pass

        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name,
            "bases": ModelAbstract
        })

        m = TestModel()
        m.save()
        c = TestCollection()
        c.set_target(m.get(m.id_attribute))
        c.find()

    def test_model_insert_hook(self):
        class ModelAbstract(object):
            def pre_insert_hook(self):
                pass

            def post_insert_hook(self):
                pass

        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name,
            "bases": ModelAbstract
        })

        c = TestCollection()
        c.add(TestModel())
        c.save()

    def test_model_update_hook(self):
        class ModelAbstract(object):
            def pre_update_hook(self):
                pass

            def post_update_hook(self):
                pass

        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name,
            "bases": ModelAbstract
        })

        mymodel = TestModel()
        mymodel.save()

        c = TestCollection()
        c.add(mymodel)
        c.set("key", "value")
        c.save()

    def test_model_delete_hook(self):
        class ModelAbstract(object):
            def pre_delete_hook(self):
                pass

            def post_delete_hook(self):
                pass

        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name,
            "bases": ModelAbstract
        })

        mymodel = TestModel()
        mymodel.save()

        c = TestCollection()
        c.add(mymodel)
        c.delete()
        c.save()


if __name__ == "__main__":
    unittest.main()
