
import unittest
import copy
import pymongo
import bson

from pymongo_basemodel.sort import Sort

from pymongo_basemodel.model import Relationship
from pymongo_basemodel.model import Model

from pymongo_basemodel.collection import Collection

from pymongo_basemodel.exceptions import ModelNotFound
from pymongo_basemodel.exceptions import ModelTargetNotSet
from pymongo_basemodel.exceptions import CollectionModelClassMismatch
from pymongo_basemodel.exceptions import CollectionModelNotPresent
from pymongo_basemodel.exceptions import RelationshipResolutionError


class TestCollection(unittest.TestCase):

    def setUp(self):
        global client, collection_name, TestModel, TestCollection
        client = pymongo.MongoClient(connect=False)
        collection_name = "{}_{}".format(
            self.__class__.__name__,
            self._testMethodName
        )

        class TestModel(Model):
            pymongo_collection = client["pymongo_basemodel"][collection_name]

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

        class TestCollection(Collection):
            model = TestModel

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

    def tearDown(self):
        client["pymongo_basemodel"].drop_collection(collection_name)

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
        self.assertNotEqual(c1.collection, c2.collection)

        c2.collection.append(TestModel())
        self.assertNotEqual(c1.collection, c2.collection)

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
        self.assertEqual(c2.collection[0].__dict__, m4.__dict__)

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
        class DefaultGetProjection(TestCollection):
            def __init__(self):
                super().__init__()
                self.default_get_projection({"k1": 0})

        m11 = TestModel()
        m11.set({"k1": "v", "k2": "v", "k3": "v"})
        m11.save()
        c6 = DefaultGetProjection()
        c6.set_target(m11.get_id())
        c6.find()

        for m in c6.get():
            self.assertNotIn("k1", m)
            self.assertIn("k2", m)
            self.assertIn("k3", m)

        self.tearDown()

        # default find projection ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class DefaultFindProjection(TestCollection):
            def __init__(self):
                super().__init__()
                self.default_find_projection({"k1": 0})

        m12 = TestModel()
        m12.set({"k1": "v", "k2": "v", "k3": "v"})
        m12.save()
        c7 = DefaultFindProjection()
        c7.set_target(m12.get_id())
        c7.find()

        for m in c7:
            self.assertNotIn("k1", m.get())
            self.assertIn("k2", m.get())
            self.assertIn("k3", m.get())

        self.tearDown()

        # default model projection ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class DefaultFindProjection(TestModel):
            def __init__(self):
                super().__init__()
                self.default_find_projection({"k1": 1})

        class DefaultFindProjectionCollection(TestCollection):
            model = DefaultFindProjection

        m1 = DefaultFindProjection()
        m1.set({"k1": "v", "k2": "v", "k3": "v"})
        m1.save()
        c = DefaultFindProjectionCollection()
        c.find(default_model_projection=True)
        self.assertEqual(c.get(), [{
            m1.id_attribute: m1.get(m1.id_attribute),
            "k1": "v"
        }])

        self.tearDown()

        # default sort ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class DefaultSort(TestModel):
            def __init__(self):
                super().__init__()

        class DefaultSortCollection(TestCollection):
            model = DefaultSort
            def __init__(self):
                super().__init__()
                self.default_sort([("k2", 1)])

        m1 = DefaultSort()
        m1.set({"k1": "v1", "k2": 2, "k3": "v1"})
        m1.save()
        m2 = DefaultSort()
        m2.set({"k1": "v2", "k2": 3, "k3": "v2"})
        m2.save()
        m3 = DefaultSort()
        m3.set({"k1": "v3", "k2": 1, "k3": "v3"})
        m3.save()
        c = DefaultSortCollection()
        c.find()

        self.assertEqual(c.get(), [
            {
                m3.id_attribute: m3.get(m3.id_attribute),
                "k1": "v3",
                "k2": 1,
                "k3":
                "v3"
            },{
                m1.id_attribute: m1.get(m1.id_attribute),
                "k1": "v1",
                "k2": 2,
                "k3": "v1"
            },{
                m2.id_attribute: m2.get(m2.id_attribute),
                "k1": "v2",
                "k2": 3,
                "k3": "v2"
            }
        ])

        self.tearDown()

        # argument sort ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class ArgumentSort(TestModel):
            def __init__(self):
                super().__init__()

        class ArgumentSortCollection(TestCollection):
            model = ArgumentSort
            def __init__(self):
                super().__init__()

        m1 = ArgumentSort()
        m1.set({"k1": "v1", "k2": 2, "k3": "v1"})
        m1.save()
        m2 = ArgumentSort()
        m2.set({"k1": "v2", "k2": 3, "k3": "v2"})
        m2.save()
        m3 = ArgumentSort()
        m3.set({"k1": "v3", "k2": 1, "k3": "v3"})
        m3.save()
        c = ArgumentSortCollection()
        c.find(sort=[("k2", 1)])

        self.assertEqual(c.get(), [
            {
                m3.id_attribute: m3.get(m3.id_attribute),
                "k1": "v3",
                "k2": 1,
                "k3":
                "v3"
            },{
                m1.id_attribute: m1.get(m1.id_attribute),
                "k1": "v1",
                "k2": 2,
                "k3": "v1"
            },{
                m2.id_attribute: m2.get(m2.id_attribute),
                "k1": "v2",
                "k2": 3,
                "k3": "v2"
            }
        ])

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

    def test_remove(self):
        m1 = TestModel()
        c1 = TestCollection()
        c1.add(m1)
        c1.remove(m1)
        self.assertNotIn(m1, c1)

        # raise exception ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        with self.assertRaises(CollectionModelNotPresent):
            TestCollection().remove(Model())

    def test_dereference_nested_models(self):

        # one to many local ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class OneToMany1(TestModel):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.relationships({
                    "r": Relationship({
                        "type": "one_to_many",
                        "model": OneToMany1Collection,
                        "local_key": "r",
                        "foreign_key": OneToMany1.id_attribute
                    })
                })

        class OneToMany1Collection(TestCollection):
            model = OneToMany1

        m1 = OneToMany1()
        m1.save()
        m2 = OneToMany1()
        m2.save()
        m3 = OneToMany1()

        m3.set("r", [m1.get(m1.id_attribute), m2.get(m2.id_attribute)])
        m3.save()

        m4 = OneToMany1(m3.get(m3.id_attribute))
        self.assertEqual(m4.attributes.get(), {})

        m4.find(projection={"r": 2})
        self.assertEqual(type(m4.attributes["r"]), OneToMany1Collection)
        for m in m4.attributes["r"]:
            self.assertEqual(type(m), OneToMany1)

        self.tearDown()

        # one to many local, without local key ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class OneToMany1(TestModel):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.relationships({
                    "r": Relationship({
                        "type": "one_to_many",
                        "model": OneToMany1Collection,
                        "foreign_key": OneToMany1.id_attribute
                    })
                })

        class OneToMany1Collection(TestCollection):
            model = OneToMany1

        m1 = OneToMany1()
        m1.save()
        m2 = OneToMany1()
        m2.save()
        m3 = OneToMany1()

        m3.set("r", [m1.get(m1.id_attribute), m2.get(m2.id_attribute)])
        m3.save()

        m4 = OneToMany1(m3.get(m3.id_attribute))
        self.assertEqual(m4.attributes.get(), {})

        m4.find(projection={"r": 2})
        self.assertEqual(type(m4.attributes["r"]), OneToMany1Collection)
        for m in m4.attributes["r"]:
            self.assertEqual(type(m), OneToMany1)

        self.tearDown()

        # one to many local, without foreign key ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class OneToMany1(TestModel):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.relationships({
                    "r": Relationship({
                        "type": "one_to_many",
                        "model": OneToMany1Collection,
                        "local_key": "r"
                    })
                })

        class OneToMany1Collection(TestCollection):
            model = OneToMany1

        m1 = OneToMany1()
        m1.save()
        m2 = OneToMany1()
        m2.save()
        m3 = OneToMany1()

        m3.set("r", [m1.get(m1.id_attribute), m2.get(m2.id_attribute)])
        m3.save()

        m4 = OneToMany1(m3.get(m3.id_attribute))
        self.assertEqual(m4.attributes.get(), {})

        m4.find(projection={"r": 2})
        self.assertEqual(type(m4.attributes["r"]), OneToMany1Collection)
        for m in m4.attributes["r"]:
            self.assertEqual(type(m), OneToMany1)

        self.tearDown()

        # one to many local, projection ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class OneToMany2(TestModel):
            def __init__(self, *args, **kwargs):
                super(OneToMany2, self).__init__(*args, **kwargs)
                self.relationships({
                    "r": Relationship({
                        "type": "one_to_many",
                        "model": OneToMany2Collection,
                        "local_key": "r",
                        "foreign_key": OneToMany2.id_attribute
                    })
                })

        class OneToMany2Collection(TestCollection):
            model = OneToMany2

        m5 = OneToMany2()
        m5.set("k1", "v")
        m5.set("k2", "v")
        m5.set("k3", "v")
        m5.save()

        m6 = OneToMany2()
        m6.set("k1", "v")
        m6.set("k2", "v")
        m6.set("k3", "v")
        m6.save()

        m7 = OneToMany2()
        m7.set("r", [m5.get(m5.id_attribute), m6.get(m6.id_attribute)])
        m7.save()
        m8 = OneToMany2(m7.get(m7.id_attribute))
        self.assertEqual(m8.attributes.get(), {})

        m8.find(projection={"r": {"k2": 0}})
        for m in m8.ref("r"):
            self.assertIn("k1", m.attributes)
            self.assertNotIn("k2", m.attributes)
            self.assertIn("k3", m.attributes)

        self.tearDown()

        # one to many local, relationship resolution error ~~~~~~~~~~~~~~~~~~~~
        class OneToMany3(TestModel):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.relationships({
                    "r": Relationship({
                        "type": "one_to_many",
                        "model": OneToMany3Collection,
                        "local_key": "r",
                        "foreign_key": OneToMany3.id_attribute
                    })
                })

        class OneToMany3Collection(TestCollection):
            model = OneToMany3

        m9 = OneToMany3()
        m9.save()

        m10 = OneToMany3()
        m10.set("r", [m9.get(m9.id_attribute)])
        m10.save()

        m9.delete()
        m9.save()

        m11 = OneToMany3(m10.get(m10.id_attribute))
        self.assertEqual(m11.attributes.get(), {})

        m11.find(projection={"r": 2})
        for m in m11.ref("r"):
            self.assertEqual(type(m), RelationshipResolutionError)

        self.tearDown()

        # many to many local ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class ManyToMany1(TestModel):
            def __init__(self, *args, **kwargs):
                super(ManyToMany1, self).__init__(*args, **kwargs)
                self.relationships({
                    "r": Relationship({
                        "type": "many_to_many",
                        "model": ManyToMany1Collection,
                        "local_key": "r",
                        "foreign_key": ManyToMany1.id_attribute
                    })
                })

        class ManyToMany1Collection(TestCollection):
            model = ManyToMany1

        m12 = ManyToMany1()
        m12.save()
        m13 = ManyToMany1()
        m13.save()
        m14 = ManyToMany1()
        m14.set("r", [m12.get(m12.id_attribute), m13.get(m13.id_attribute)])
        m14.save()
        m15 = ManyToMany1()
        m15.set("r", [m12.get(m12.id_attribute), m13.get(m13.id_attribute)])
        m15.save()
        m16 = ManyToMany1(m14.get(m14.id_attribute))
        m16.find(projection={"r": 2})
        self.assertEqual(len(m16.ref("r")), 2)
        for m in m16.ref("r"):
            self.assertEqual(type(m), ManyToMany1)

        self.tearDown()

        # one to many foreign ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class OneToMany4(TestModel):
            def __init__(self, *args, **kwargs):
                super(OneToMany4, self).__init__(*args, **kwargs)
                self.relationships({
                    "foo": Relationship({
                        "type": "one_to_many",
                        "model": OneToMany4Collection,
                        "local_key": OneToMany4.id_attribute,
                        "foreign_key": "bar"
                    })
                })

        class OneToMany4Collection(TestCollection):
            model = OneToMany4

        m17 = OneToMany4()
        m17.save()
        m18 = OneToMany4()
        m18.set("bar", m17.get(m17.id_attribute))
        m18.save()
        m19 = OneToMany4()
        m19.set("bar", m17.get(m17.id_attribute))
        m19.save()

        m20 = OneToMany4(m19.get(m19.id_attribute))
        m20.find(projection={"foo": 2})
        for m in m20.ref("foo"):
            self.assertEqual(type(m), OneToMany4())

        self.tearDown()

        # one to many foreign, projection ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class OneToMany5(TestModel):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.relationships({
                    "foo": Relationship({
                        "type": "one_to_many",
                        "model": OneToMany5Collection,
                        "local_key": OneToMany5.id_attribute,
                        "foreign_key": "bar"
                    })
                })

        class OneToMany5Collection(TestCollection):
            model = OneToMany5

        m21 = OneToMany5()
        m21.set({"k1": "v", "k2": "v", "k3": "v"})
        m21.save()
        m22 = OneToMany5()
        m22.set("bar", m21.get(m21.id_attribute))
        m22.set({"k1": "v", "k2": "v", "k3": "v"})
        m22.save()
        m23 = OneToMany5()
        m23.set("bar", m21.get(m21.id_attribute))
        m23.set({"k1": "v", "k2": "v", "k3": "v"})
        m23.save()

        m24 = OneToMany5(m21.get(m21.id_attribute))
        m24.find(projection={"foo": {"k1": 1, "k2": 1}})

        self.assertEqual(type(m24.attributes["foo"]), OneToMany5Collection)
        for m in m24.ref("foo"):
            self.assertIn("k1", m.get())
            self.assertIn("k2", m.get())
            self.assertNotIn("k3", m.get())

        self.tearDown()

        # many to many foreign ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class ManyToMany2(TestModel):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.relationships({
                    "foo": Relationship({
                        "type": "many_to_many",
                        "model": ManyToMany2Collection,
                        "local_key": ManyToMany2.id_attribute,
                        "foreign_key": "bar"
                    })
                })

        class ManyToMany2Collection(TestCollection):
            model = ManyToMany2

        m25 = ManyToMany2()
        m25.save()
        m26 = ManyToMany2()
        m26.save()
        m27 = ManyToMany2()
        m27.set("bar", [m25.get(m25.id_attribute)])
        m27.save()
        m28 = ManyToMany2()
        m28.set("bar", [m25.get(m25.id_attribute), m26.get(m26.id_attribute)])
        m28.save()

        m29 = ManyToMany2(m28.get(m28.id_attribute))
        m29.find(projection={"foo": 2})

        self.assertEqual(type(m29.ref("foo")), ManyToMany2Collection)
        for m in m29.ref("foo"):
            self.assertEqual(type(m), ManyToMany2)

        self.tearDown()

        # many to many foreign, projection ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class ManyToMany3(TestModel):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.relationships({
                    "foo": Relationship({
                        "type": "many_to_many",
                        "model": ManyToMany3Collection,
                        "local_key": ManyToMany3.id_attribute,
                        "foreign_key": "bar"
                    })
                })

        class ManyToMany3Collection(TestCollection):
            model = ManyToMany3

        m30 = ManyToMany3()
        m30.save()
        m31 = ManyToMany3()
        m31.save()

        m32 = ManyToMany3()
        m32.set("bar", [m30.get(m30.id_attribute)])
        m32.set({"k1": "v", "k2": "v", "k3": "v"})
        m32.save()

        m33 = ManyToMany3()
        m33.set("bar", [m30.get(m30.id_attribute), m31.get(m31.id_attribute)])
        m33.set({"k1": "v", "k2": "v", "k3": "v"})
        m33.save()

        m34 = ManyToMany3(m30.get(m30.id_attribute))
        m34.find(projection={"foo": {"k1": 1}})
        self.assertEqual(type(m34.ref("foo")), ManyToMany3Collection)
        for m in m34.ref("foo"):
            self.assertIn("k1", m.get())
            self.assertNotIn("k2", m.get())
            self.assertNotIn("k3", m.get())

        self.tearDown()

    def test_reference_nested_models(self):
        m1 = TestModel()
        m1.save()
        m2 = TestModel()
        m2.save()
        c1 = TestCollection()
        c1.add(m1)
        c1.add(m2)
        m3 = TestModel()
        m3.set("r", c1)
        data = m3.reference_nested_models()
        self.assertIn("r", data)
        for v in data["r"]:
            self.assertEqual(type(v), bson.objectid.ObjectId)

    def test_hooks(self):

        # pre find hook ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class PreFindHook1(TestCollection):
            def pre_find_hook(self):
                m = TestModel()
                m.set("unique_key", "unique_value")
                self.add(m)

        c1 = PreFindHook1()
        c1.find()

        self.assertEqual(len(c1), 1)
        self.assertEqual(type(c1.collection[0]), TestModel)

        self.tearDown()

        # post find hook ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m1 = TestModel()
        m1.save()
        m2 = TestModel()
        m2.save()
        m3 = TestModel()
        m3.save()

        class PostFindHook2(TestCollection):
            def post_find_hook(self):
                self.collection = []

        c2 = TestCollection()
        c2.find()
        self.assertEqual(len(c2), 3)

        c3 = PostFindHook2()
        c3.find()
        self.assertEqual(len(c3), 0)

        self.tearDown()

        # pre modify hook ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class PreModifyHook(TestCollection):
            def pre_modify_hook(self):
                m = TestModel()
                m.set("k", "hook_v")
                self.add(m)

        m4 = TestModel()
        m4.set("k", "v")
        m4 = TestModel()
        c1 = PreModifyHook()
        c1.add(m4)
        c1.save()
        self.assertEqual(len(c1), 2)
        for m in c1:
            self.assertIn(m.id_attribute, m.attributes)

        self.tearDown()

        # post modify hook ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class PostModifyHook(TestCollection):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
            def post_modify_hook(self):
                self.collection = []

        m1 = TestModel()
        m1.set("k", "v")
        m2 = TestModel()
        m2.set("k", "v")
        m3 = TestModel()
        m3.set("k", "v")
        c = PostModifyHook()
        c.add(m1)
        c.add(m2)
        c.add(m3)
        self.assertEqual(len(c), 3)

        c.save()
        self.assertEqual(len(c), 0)

        self.tearDown()

        # model find hooks ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class ModelFindHooks(TestModel):
            def pre_find_hook(self):
                pass
            def post_find_hook(self):
                pass

        class ModelFindHooksCollection(TestCollection):
            model = ModelFindHooks

        m8 = ModelFindHooks()
        m8.save()
        c6 = ModelFindHooksCollection()
        c6.set_target(m8.get(m8.id_attribute))
        c6.find()

        self.tearDown()

        # model insert hooks ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class ModelInsertHooks(TestModel):
            def pre_insert_hook(self):
                pass
            def post_insert_hook(self):
                pass

        class ModelInsertHooksCollection(TestCollection):
            model = ModelInsertHooks

        c = ModelInsertHooksCollection()
        c.add(ModelInsertHooks())
        c.save()

        self.tearDown()

        # model update hooks ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class ModelUpdateHooks(TestModel):
            def pre_update_hook(self):
                pass
            def post_update_hook(self):
                pass

        class ModelUpdateHooksCollection(TestCollection):
            model = ModelUpdateHooks

        mymodel = ModelUpdateHooks()
        mymodel.save()

        c = ModelUpdateHooksCollection()
        c.add(mymodel)
        c.set("key", "value")
        c.save()

        self.tearDown()

        # model delete hooks ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class ModelDeleteHooks(TestModel):
            def pre_delete_hook(self):
                pass
            def post_delete_hook(self):
                pass

        class ModelDeleteHooksCollection(TestCollection):
            model = ModelDeleteHooks

        mymodel = ModelDeleteHooks()
        mymodel.save()

        c = ModelDeleteHooksCollection()
        c.add(mymodel)
        c.delete()
        c.save()

        self.tearDown()
