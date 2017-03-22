
import sys; sys.path.append("../")

import unittest
import copy
import pymongo
import datetime
import bson

from pymongo_basemodel.connection import add_connection, get_connection
from pymongo_basemodel.delimited import DelimitedDict
from pymongo_basemodel.projection import Projection
from pymongo_basemodel.undefined import Undefined
from pymongo_basemodel.model import Reference
from pymongo_basemodel.model import Model
from pymongo_basemodel.exceptions import ModelTargetNotSet
from pymongo_basemodel.exceptions import ModelNotUpdated
from pymongo_basemodel.exceptions import ModelNotFound
from pymongo_basemodel.exceptions import ModelNotDeleted
from pymongo_basemodel.exceptions import ProjectionTypeMismatch
from pymongo_basemodel.exceptions import DereferenceError


class TestModel(unittest.TestCase):

    def setUp(self):
        global database_name, collection_name, TestModel
        database_name = "pymongo_basemodel"
        collection_name = "{}_{}".format(
            self.__class__.__name__,
            self._testMethodName
        )

        connection = pymongo.MongoClient(connect=False)[database_name]
        add_connection(database_name, connection)

        class TestModel(Model):
            mongo_database = database_name
            mongo_collection = collection_name

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

    def tearDown(self):
        global database_name, collection_name
        get_connection(database_name).drop_collection(collection_name)

    def test_init(self):
        m = Model()
        self.assertEqual(m.id_attribute, "_id")
        self.assertEqual(m.mongo_collection, None)
        self.assertEqual(type(m.target), DelimitedDict)
        self.assertEqual(type(m.attributes), DelimitedDict)
        self.assertEqual(type(m.references), DelimitedDict)
        self.assertEqual(type(m.default_attributes), DelimitedDict)
        self.assertEqual(type(m.computed_attributes), DelimitedDict)

        self.assertEqual(type(m.default_find_projection), Projection)
        self.assertEqual(type(m.default_get_projection), Projection)

        self.assertEqual(m._delete, False)
        self.assertEqual(type(m.original), DelimitedDict)
        self.assertEqual(type(m.updates), DelimitedDict)

    def test_copy(self):
        m1 = Model()
        m1.attributes({"k1": "v", "k2": {"k3": "v"}})
        m2 = copy.copy(m1)
        self.assertIsNot(m1, m2)
        self.assertEqual(m1.attributes, m2.attributes)
        m1.attributes["k2"]["k3"] = "bar"
        self.assertEqual(m1.attributes, m2.attributes)

    def test_deepcopy(self):
        m1 = Model()
        m1.attributes({"k1": "v", "k2": {"k3": "v"}})
        m2 = copy.deepcopy(m1)
        self.assertIsNot(m1, m2)
        self.assertEqual(m1.attributes, m2.attributes)
        m1.attributes["k2"]["k3"] = "bar"
        self.assertNotEqual(m1.attributes, m2.attributes)

    def test_eq(self):
        m1 = Model()
        m2 = Model()
        self.assertEqual(True, m1 == m2)

    def test_ne(self):
        m1 = Model()
        m1.attributes({"k": "v"})
        m2 = Model()
        self.assertEqual(True, m1 != m2)

    def test_set_default_attributes(self):
        class TestModelWithDefaultAttributes(TestModel):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.default_attributes({
                    "k": "v"
                })

        m1 = TestModelWithDefaultAttributes()
        m1.save()

        self.assertIn("k", m1.attributes)
        self.assertEqual(m1.attributes["k"], "v")

        # callable default attribute ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class TestModelWithDefaultAttributes(TestModel):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.default_attributes({
                    "k": lambda: datetime.datetime.today()
                })

        m2 = TestModelWithDefaultAttributes()
        m2.save()

        self.assertIn("k", m2.attributes)
        self.assertIsInstance(m2.attributes["k"], datetime.datetime)

        # callable default attribute, raise exception ~~~~~~~~~~~~~~~~~~~~~~~~~
        class TestModelWithDefaultAttributes(TestModel):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.default_attributes({
                    "k": lambda: 0/0
                })

        m3 = TestModelWithDefaultAttributes()
        with self.assertRaises(ZeroDivisionError):
            m3.save()

        # default=False ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class TestModelWithDefaultAttributes(TestModel):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.default_attributes({"k": "v"})

        m4 = TestModelWithDefaultAttributes()
        m4.save(default=False)

        self.assertNotIn("k", m4.attributes)

        # inherit, overwrite ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class DefaultAttributesParent1(TestModel):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.default_attributes({"k1": "v"})

        class DefaultAttributesChild1(DefaultAttributesParent1):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.default_attributes({"k2": "v"})

        m5 = DefaultAttributesChild1()
        m5.save()

        self.assertNotIn("k1", m5.attributes)
        self.assertIn("k2", m5.attributes)
        self.assertEqual(m5.attributes["k2"], "v")

        # inherit, merge ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class DefaultAttributesParent2(TestModel):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.default_attributes({"k1": "v"})

        class DefaultAttributesChild2(DefaultAttributesParent2):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.default_attributes.merge({"k2": "v"})

        m6 = DefaultAttributesChild2()
        m6.save()

        self.assertIn("k1", m6.attributes)
        self.assertIn("k2", m6.attributes)
        self.assertEqual(m6.attributes["k1"], "v")
        self.assertEqual(m6.attributes["k2"], "v")

    def test_set_computed_attributes(self):

        class ComputedAttributes1(TestModel):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.computed_attributes({"k": "v"})

        m1 = ComputedAttributes1()
        self.assertEqual({}, m1.attributes.get())
        self.assertEqual({"k": "v"}, m1.get())
        self.assertEqual({}, m1.attributes.get())

        # callable ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class ComputedAttributes2(TestModel):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.computed_attributes({
                    "k": lambda: datetime.datetime.today()
                })

        m2 = ComputedAttributes2()

        self.assertEqual({}, m2.attributes.get())
        self.assertIn("k", m2.get())
        self.assertIsInstance(m2.get("k"), datetime.datetime)
        self.assertEqual({}, m2.attributes.get())

        # callable, raise exception ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class ComputedAttributes3(TestModel):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.computed_attributes({
                    "k": lambda: 0/0
                })

        m3 = ComputedAttributes3()
        self.assertEqual({}, m3.attributes.get())
        self.assertEqual({}, m3.get())

    def test_set_target(self):
        # string
        m2 = Model()
        m2.set_target("v")
        self.assertEqual(m2.target.get(), {m2.id_attribute: "v"})

        # dict
        m2 = Model()
        m2.set_target({"k": "v"})
        self.assertEqual(m2.target.get(), {"k": "v"})

        # string, instantiation
        m = Model("v")
        self.assertEqual(m.target.get(), {m.id_attribute: "v"})

        # dict, instantiation
        m = Model({"k": "v"})
        self.assertEqual(m.target.get(), {"k": "v"})

    def test_get_target(self):
        m1 = Model()
        m1.set_target("v")
        self.assertEqual(m1.get_target(), {m1.id_attribute: "v"})

        # raise exception
        m2 = Model()
        self.assertEqual(m2.get_target(), None)

    def test_get_id(self):
        m = Model()
        self.assertEqual(m.get_id(), None)
        m.target({m.id_attribute: bson.objectid.ObjectId()})
        self.assertIsInstance(m.get_id(), bson.objectid.ObjectId)

    def test_find(self):

        # find ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        tm1 = TestModel()
        tm1.attributes({"k": "v"})
        tm1_id = tm1.save().get(tm1.id_attribute)

        m1 = TestModel()
        m1.target({tm1.id_attribute: tm1_id})
        m1.find()

        self.assertIn("k", m1.attributes)
        self.assertEqual(m1.attributes["k"], "v")

        self.tearDown()

        # raise exception ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m2 = TestModel()
        with self.assertRaises(ModelTargetNotSet):
            m2.find()

        # default find projection ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        tm3 = TestModel()
        tm3.attributes({"k1": "v", "k2": "v", "k3": "v"})
        tm3_id = tm3.save().attributes[TestModel.id_attribute]

        class DefaultFindProjection1(TestModel):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.default_find_projection({"k1": 0})

        m3 = DefaultFindProjection1()
        m3.target({tm3.id_attribute: tm3_id})
        m3.find()

        self.assertEqual(m3.attributes.get(), {
            TestModel.id_attribute: tm3_id,
            "k2": "v",
            "k3": "v"
        })

        self.tearDown()

        # argument projection ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        tm4 = TestModel()
        tm4.attributes({"k1": "v", "k2": "v", "k3": "v"})
        tm4_id = tm4.save().attributes[TestModel.id_attribute]

        m4 = TestModel()
        m4.target({tm4.id_attribute: tm4_id})
        m4.find(projection={"k1": 0})

        self.assertEqual(m4.attributes.get(), {
            tm4.id_attribute: tm4_id,
            "k2": "v",
            "k3": "v"
        })

        self.tearDown()

        # default find projection, argument projection ~~~~~~~~~~~~~~~~~~~~~~~~
        tm5 = TestModel()
        tm5.attributes({"k1": "v", "k2": "v", "k3": "v"})
        tm5_id = tm5.save().attributes[TestModel.id_attribute]

        class DefaultFindProjection2(TestModel):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.default_find_projection({
                    "k1": 0
                })

        m5 = DefaultFindProjection2()
        m5.target({tm5.id_attribute: tm5_id})
        m5.find(projection={"k3": 0}, default=True)
        self.assertEqual(m5.attributes.get(), {
            tm5.id_attribute: tm5_id, "k2": "v"
        })

        self.tearDown()

        # default find projection, argument projection, raise exception ~~~~~~~
        tm6 = TestModel()
        tm6.attributes({"k1": "v", "k2": "v", "k3": "v"})
        tm6_id = tm6.save().attributes[TestModel.id_attribute]

        class DefaultFindProjection3(TestModel):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.default_find_projection({
                    "k1": 0
                })

        m6 = DefaultFindProjection3()
        m6.target({tm6.id_attribute: tm6_id})
        with self.assertRaises(ProjectionTypeMismatch):
            m6.find(projection={"k3": 1}, default=True)

        self.tearDown()

        # extendable pre find hook ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class PreFindHook1(TestModel):
            def pre_find_hook(self):
                self.target({"k": "v"})

        m7 = PreFindHook1()
        m7.target({"foo": "baz"})
        try:
            m7.find()
        except:
            pass

        self.assertEqual(m7.target.get(), {"k": "v"})

        self.tearDown()

        # extendable post find hook ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class PostFindHook1(TestModel):
            def post_find_hook(self):
                self.target({"k": "v"})

        m8 = PostFindHook1()
        m8.set("foor", "bar")
        m8.save()

        m9 = PostFindHook1(m8.get("_id"))
        m9.find()

        self.assertEqual(m9.target.get(), {"k": "v"})

        self.tearDown()

    def test_dereference_nested_models(self):
        # one to one local ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class OneToOneLocal1(TestModel):
            def __init__(self, *args, **kwargs):
                super(OneToOneLocal1, self).__init__(*args, **kwargs)
                self.references({
                    "r": Reference({
                        "type": "one_to_one",
                        "model": OneToOneLocal1,
                        "local_key": "r",
                        "foreign_key": OneToOneLocal1.id_attribute
                    })
                })

        m2 = OneToOneLocal1()
        m2.set("k", "v")
        m2.save()

        m1 = OneToOneLocal1()
        m1.set("k", "v")
        m1.set("r", m2.get_id())
        m1.save()

        m3 = OneToOneLocal1(m1.get_id()).find(projection={"r": 2})

        self.assertEqual(type(m3.attributes["r"]), OneToOneLocal1)
        self.assertEqual(m3.get("r._id"), m2.get("_id"))

        # one to one local with projection ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class OneToOneLocal2(TestModel):
            def __init__(self, *args, **kwargs):
                super(OneToOneLocal2, self).__init__(*args, **kwargs)
                self.references({
                    "r": Reference({
                        "type": "one_to_one",
                        "model": OneToOneLocal2,
                        "local_key": "r",
                        "foreign_key": OneToOneLocal2.id_attribute
                    })
                })

        m5 = OneToOneLocal2()
        m5.set("k", "v")
        m5.save()

        m4 = OneToOneLocal2()
        m4.set("k", "v")
        m4.set("r", m5.get_id())
        m4.save()

        m6 = OneToOneLocal2(m4.get_id()).find(projection={"r": {"k": 0}})

        self.assertEqual(type(m6.attributes["r"]), OneToOneLocal2)
        self.assertEqual(m6.get("r._id"), m5.get("_id"))
        self.assertEqual(m6.get("r"), {"_id": m5.get("_id")})

        # one to one local without local key ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class OneToOneLocal3(TestModel):
            def __init__(self, *args, **kwargs):
                super(OneToOneLocal3, self).__init__(*args, **kwargs)
                self.references({
                    "r": Reference({
                        "type": "one_to_one",
                        "model": OneToOneLocal3,
                        "foreign_key": OneToOneLocal3.id_attribute
                    })
                })

        m8 = OneToOneLocal3()
        m8.set("k", "v")
        m8.save()

        m7 = OneToOneLocal3()
        m7.set("k", "v")
        m7.set("r", m8.get_id())
        m7.save()

        m9 = OneToOneLocal3(m7.get_id()).find(projection={"r": 2})

        self.assertEqual(type(m9.attributes["r"]), OneToOneLocal3)
        self.assertEqual(m9.get("r._id"), m8.get("_id"))

        # one to one local without forgien key ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class OneToOneLocal4(TestModel):
            def __init__(self, *args, **kwargs):
                super(OneToOneLocal4, self).__init__(*args, **kwargs)
                self.references({
                    "r": Reference({
                        "type": "one_to_one",
                        "model": OneToOneLocal4,
                        "local_key": "r"
                    })
                })

        m11 = OneToOneLocal4()
        m11.set("k", "v")
        m11.save()

        m10 = OneToOneLocal4()
        m10.set("k", "v")
        m10.set("r", m11.get_id())
        m10.save()

        m12 = OneToOneLocal4(m10.get_id()).find(projection={"r": 2})

        self.assertEqual(type(m12.attributes["r"]), OneToOneLocal4)
        self.assertEqual(m12.get("r._id"), m11.get("_id"))

        # one to one local, dot notation ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class OneToOneLocal5(TestModel):
            def __init__(self, *args, **kwargs):
                super(OneToOneLocal5, self).__init__(*args, **kwargs)
                self.references({
                    "r1.r2.r3": Reference({
                        "type": "one_to_one",
                        "model": OneToOneLocal5,
                        "local_key": "r1.r2.r3",
                        "foreign_key": OneToOneLocal5.id_attribute
                    })
                })

        m2 = OneToOneLocal5()
        m2.set("k", "v")
        m2.save()

        m1 = OneToOneLocal5()
        m1.set("k", "v")
        m1.set("r1.r2.r3", m2.get_id())
        m1.save()

        m3 = OneToOneLocal5(m1.get_id()).find(projection={"r1.r2.r3": 2})

        self.assertEqual(type(m3.attributes["r1.r2.r3"]), OneToOneLocal5)
        self.assertEqual(m3.get("r1.r2.r3._id"), m2.get("_id"))

        # many to one local ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class ManyToOneLocal(TestModel):
            def __init__(self, *args, **kwargs):
                super(ManyToOneLocal, self).__init__(*args, **kwargs)
                self.references({
                    "r": Reference({
                        "type": "many_to_one",
                        "model": ManyToOneLocal,
                        "local_key": "r",
                        "foreign_key": ManyToOneLocal.id_attribute
                    })
                })

        m14 = ManyToOneLocal()
        m14.set("k", "v")
        m14.save()

        m13 = ManyToOneLocal()
        m13.set("k", "v")
        m13.set("r", m14.get_id())
        m13.save()

        m15 = ManyToOneLocal(m13.get_id()).find(projection={"r": 2})

        self.assertEqual(type(m15.attributes["r"]), ManyToOneLocal)
        self.assertEqual(m15.get("r._id"), m14.get("_id"))

        # many to one foreign ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class ManyToOneForeign(TestModel):
            def __init__(self, *args, **kwargs):
                super(ManyToOneForeign, self).__init__(*args, **kwargs)
                self.references({
                    "r": Reference({
                        "type": "one_to_one",
                        "model": ManyToOneForeign,
                        "local_key": ManyToOneForeign.id_attribute,
                        "foreign_key": "r"
                    })
                })

        m17 = ManyToOneForeign()
        m17.set("k", "v")
        m17.save()

        m16 = ManyToOneForeign()
        m16.set("k", "v")
        m16.set("r", m17.get_id())
        m16.save()

        m18 = ManyToOneForeign(m17.get_id()).find(projection={"r": 2})

        self.assertEqual(type(m18.attributes["r"]), ManyToOneForeign)
        self.assertEqual(m18.get("r._id"), m16.get("_id"))

        # one to one foreign ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class OneToOneForeign1(TestModel):
            def __init__(self, *args, **kwargs):
                super(OneToOneForeign1, self).__init__(*args, **kwargs)
                self.references({
                    "r": Reference({
                        "type": "one_to_one",
                        "model": OneToOneForeign1,
                        "local_key": OneToOneForeign1.id_attribute,
                        "foreign_key": "r"
                    })
                })

        m20 = OneToOneForeign1()
        m20.set("k", "v")
        m20.save()

        m19 = OneToOneForeign1()
        m19.set("k1", "v")
        m19.set("k2", "v")
        m19.set("k3", "v")
        m19.set("r", m20.get_id())
        m19.save()

        m21 = OneToOneForeign1(m20.get_id()).find(projection={
            "r": {"k2": 1}
        })

        # assert resolved relationship
        self.assertEqual(type(m21.attributes["r"]), OneToOneForeign1)
        self.assertEqual(m21.get("r._id"), m19.get("_id"))
        self.assertEqual(m21.get("r"), {
          "_id": m19.get("_id"),
          "k2": "v"
        })

        # many to one foreign ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class ManyToOneForeign(TestModel):
            def __init__(self, *args, **kwargs):
                super(ManyToOneForeign, self).__init__(*args, **kwargs)
                self.references({
                    "r": Reference({
                        "type": "many_to_one",
                        "model": ManyToOneForeign,
                        "local_key": ManyToOneForeign.id_attribute,
                        "foreign_key": "r"
                    })
                })

        m23 = ManyToOneForeign()
        m23.set("k", "v")
        m23.save()

        m22 = ManyToOneForeign()
        m22.set("k", "v")
        m22.set("r", m23.get_id())
        m22.save()

        m24 = ManyToOneForeign(m23.get_id()).find(projection={"r": 2})

        self.assertEqual(type(m24.attributes["r"]), ManyToOneForeign)
        self.assertEqual(m24.get("r._id"), m22.get("_id"))

        # one to one local relationship resolution error ~~~~~~~~~~~~~~~~~~~~~~
        class OneToOneLocal5(TestModel):
            def __init__(self, *args, **kwargs):
                super(OneToOneLocal5, self).__init__(*args, **kwargs)
                self.references({
                    "r": Reference({
                        "type": "one_to_one",
                        "model": OneToOneLocal5,
                        "local_key": "r",
                        "foreign_key": OneToOneLocal5.id_attribute
                    })
                })

        m26 = OneToOneLocal5()
        m26.save()

        m25 = OneToOneLocal5()
        m25.set("r", m26.get_id())
        m25.save()

        m26.delete()
        m26.save()

        m27 = OneToOneLocal5(m25.get_id()).find(projection={"r": 2})

        self.assertEqual(
            type(m27.attributes["r"]),
            DereferenceError
        )

        # one to one foreign relationship resolution error ~~~~~~~~~~~~~~~~~~~~
        class OneToOneForeign2(TestModel):
            def __init__(self, *args, **kwargs):
                super(OneToOneForeign2, self).__init__(*args, **kwargs)
                self.references({
                    "r": Reference({
                        "type": "one_to_one",
                        "model": OneToOneForeign2,
                        "local_key": OneToOneForeign2.id_attribute,
                        "foreign_key": "r"
                    })
                })

        m28 = OneToOneForeign2()
        m28.save()

        m29 = OneToOneForeign2(m28.get("_id"))
        m29.find(projection={"r": 2})

        self.assertEqual(m29.get("r"), None)

    def test_ref(self):

        # ref ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        v = "v"
        m1 = Model()
        m1.attributes({"k": v})
        self.assertIs(m1.ref("k"), v)

        # dot notation ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        v = "v"
        m2 = Model()
        m2.attributes({"k1": {"k2": {"k3": "v"}}})
        self.assertIs(m2.ref("k1.k2.k3"), v)

        # undefined ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m3 = Model()
        m3.attributes({"k": "v"})
        self.assertIsInstance(m3.ref("foo"), Undefined)
        self.assertIsInstance(m3.ref("foo.bar"), Undefined)

        m4 = Model()
        m4.attributes({"k": DereferenceError()})
        self.assertIsInstance(m4.ref("k"), DereferenceError)
        self.assertIsInstance(m4.ref("k.bar"), Undefined)

        # nested model ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        v = "v"
        m6 = Model()
        m6.attributes({"k": v})
        m5 = Model()
        m5.attributes({"r": m6})

        self.assertIs(m5.ref("r"), m6)
        self.assertIs(m6.ref("k"), v)
        self.assertIs(m5.ref("r.k"), v)

        # create=True ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m7 = Model()
        self.assertEqual(m7.ref("k", create=True), {})
        self.assertEqual(m7.attributes.get(), {"k": {}})

        m8 = Model()
        m8.attributes({"k1": "v"})
        self.assertEqual(m8.ref("k1.k2", create=True), {})
        self.assertEqual(m8.attributes.get(), {"k1": {"k2": {}}})

    def test_has(self):

        # has ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m1 = Model()
        m1.attributes({"k": "v"})
        self.assertEqual(m1.has("k"), True)

        # dot notation ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m2 = Model()
        m2.attributes({"k1.k2.k3": "v"})
        self.assertEqual(m2.has("k1.k2.k3"), True)

        # return false ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m3 = Model()
        m3.attributes({"k": "v"})
        self.assertEqual(m3.has("foo"), False)
        self.assertEqual(m3.has("k.k2.k3"), False)

        # nested model ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m5 = Model()
        m5.attributes({"k": "v"})
        m4 = Model()
        m4.attributes({"r": m5})
        self.assertEqual(m4.has("r"), True)
        self.assertEqual(m4.has("r.k"), True)
        self.assertEqual(m4.has("r.foo"), False)

        # relationship resolution error ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m6 = Model()
        m6.attributes({"k1": DereferenceError()})
        self.assertEqual(m6.has("k1"), True)
        self.assertEqual(m6.has("k1.k2.k3"), False)

    def test_get(self):

        # undefined ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m1 = Model()
        self.assertEqual(type(m1.get("k")), Undefined)

        # all attributes ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m2 = Model()
        m2.attributes({"k": "v"})
        self.assertEqual(m2.get(), {"k": "v"})

        # default projection with dot notation syntax ~~~~~~~~~~~~~~~~~~~~~~~~~
        class DefaultGetProjection1(Model):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.default_get_projection({
                    "k": 1,
                    "k1.k2": 1
                })

        m3 = DefaultGetProjection1()
        m3.attributes({"k": "v", "k1": {"k2": "v", "k3": "v"}})
        self.assertEqual(m3.get(), {"k": "v", "k1": {"k2": "v"}})

        # inclusive default get projection ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class DefaultGetProjection2(Model):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.default_get_projection({
                    "k1": 1
                })

        m4 = DefaultGetProjection2()
        m4.attributes({"k1": "v", "k2": "v"})
        self.assertEqual(m4.get(), {"k1": "v"})

        # inclusive default get projection, keyword projection ~~~~~~~~~~~~~~~~
        class DefaultGetProjection3(Model):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.default_get_projection({
                    "k1": 1
                })

        m5 = DefaultGetProjection3()
        m5.attributes({"k1": "v", "k2": "v", "k3": "v"})
        self.assertEqual(m5.get(projection={"k3": 1}, default=True), {
            "k1": "v",
            "k3": "v"
        })

        # exclusive default get projection ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class DefaultGetProjection4(Model):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.default_get_projection({
                    "k2": 0
                })

        m6 = DefaultGetProjection4()
        m6.attributes({"k1": "v", "k2": "v"})
        self.assertEqual(m6.get(), {"k1": "v"})

        # exclusive default get projection, keyword projection ~~~~~~~~~~~~~~~~
        class DefaultGetProjection5(Model):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.default_get_projection({
                    "k3": 0
                })

        m7 = DefaultGetProjection5()
        m7.attributes({"k1": "v", "k2": "v", "k3": "v"})
        self.assertEqual(m7.get(projection={"k1": 0}, default=True), {
          "k2": "v"
        })

        # string ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m8 = Model()
        m8.attributes({"k": "v"})
        self.assertEqual(m8.get("k"), "v")

        # dot notation ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m9 = Model()
        m9.attributes({"k1": "v1", "k2": "v2", "k3": "v3"})
        self.assertEqual(m9.get("k2"), "v2")

        # all attributes with nested model ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m11 = Model()
        m11.attributes({"k": "v2"})
        m10 = Model()
        m10.attributes({"k": "v1", "r": m11})
        self.assertEqual(m10.get(), {"k": "v1", "r": {"k": "v2"}})

        # attribute of nested model with dot notation syntax ~~~~~~~~~~~~~~~~~~
        m13 = Model()
        m13.attributes({"k": "v2"})
        m12 = Model()
        m12.attributes({"k": "v1", "r": m13})
        self.assertEqual(m12.get("r.k"), "v2")

        # all attributes with nested model with projection ~~~~~~~~~~~~~~~~~~~~
        m15 = Model()
        m15.attributes({"k1": "v2", "k2": "v2"})
        m14 = Model()
        m14.attributes({"k1": "v1", "k2": "v2", "r": m15})
        self.assertEqual(m14.get(projection={"k2": 0, "r": {"k1": 0}}), {
            "k1": "v1", "r": {"k2": "v2"}
        })

        # relationship resolution error ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m16 = Model()
        m16.attributes({
          "k1": {
            "k2": "value",
            "r": DereferenceError(data={"k": "v"})
          }
        })

        self.assertEqual(m16.get("k1.r"), {
          "message": "Dereference error",
          "data": {"k": "v"}
        })

    def test_generate_id(self):
        m = Model()
        self.assertEqual(type(m.generate_id()), bson.objectid.ObjectId)

    def test_set(self):

        # string ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m1 = Model()
        m1.set("k", "v")
        self.assertEqual(m1.attributes.get(), {"k": "v"})

        # dict ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m2 = Model()
        m2.set({"k": "v"})
        self.assertEqual(m2.attributes.get(), {"k": "v"})

        # dict with nested data ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m3 = Model()
        m3.set({"k1": {"k2": {"k3": "v"}}})
        self.assertEqual(m3.attributes.get(), {"k1": {"k2": {"k3": "v"}}})

        # dot notation syntax ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m4 = Model()
        m4.set("k1.k2.k3", "v")
        self.assertEqual(m4.attributes.get(), {"k1": {"k2": {"k3": "v"}}})

        # nested model ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m6 = Model()
        m5 = Model()
        m5.set("r", m6)
        m5.set("r.k", "v")
        self.assertEqual(m2.attributes.get(), {"k": "v"})

        # relationship resolution error ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m7 = Model()
        m7.set("k", DereferenceError())
        m7.set("k", "v")
        self.assertEqual(m7.attributes.get(), {"k": "v"})

        m8 = Model()
        m8.set("k1", DereferenceError())
        m8.set("k1.k2.k3", "v")
        self.assertEqual(m8.attributes.get(), {"k1": {"k2": {"k3": "v"}}})

        # overwrite value with nested data ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m9 = Model()
        m9.set("k1", "v")
        self.assertEqual(m9.attributes.get(), {"k1": "v"})
        m9.set("k1.k2", "v")
        self.assertEqual(m9.attributes.get(), {"k1": {"k2": "v"}})

        # create=False ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m10 = Model()
        with self.assertRaises(KeyError):
            m10.set("k", "v", create=False)

        m10.attributes({"k1": "v"})
        with self.assertRaises(TypeError):
            m10.set("k1.k2", "v", create=False)

        m10.attributes({"k1": DereferenceError()})
        with self.assertRaises(TypeError):
            m10.set("k1.k2", "v", create=False)

    def test_unset(self):

        # string ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m1 = Model()
        m1.attributes({"k1": "v", "k2": "v"})
        m1.original(m1.attributes)  # force state
        m1.unset("k1")
        self.assertEqual(m1.attributes.get(), {"k2": "v"})

        # dot notation syntax ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m2 = Model()
        m2.attributes({"k1": {"k2": {"k3": "v"}}, "k4": "v"})
        m2.original(m2.attributes)  # force state
        m2.unset("k1.k2.k3")
        self.assertEqual(m2.attributes.get(), {"k1": {"k2": {}}, "k4": "v"})

        with self.assertRaises(KeyError):
            m2.unset("k1.k6")

        # nested model ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m4 = Model()
        m4.attributes({"k1": "v", "k2": "v"})
        m4.original(m4.attributes)  # force state
        m3 = Model()
        m3.attributes({"r": m4})
        m3.original(m3.attributes)  # force state
        m3.unset("r.k1")
        self.assertEqual(m4.attributes.get(), {"k2": "v"})

        # force=True ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m5 = Model()
        m5.original({"k": "v"})
        m5.unset("k", force=True)

        # raise exception ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m6 = Model()
        m6.attributes({"k1": DereferenceError()})
        m6.original(m6.attributes)  # force state

        with self.assertRaises(TypeError):
            m6.unset("k1.k2.k3")

        m6.attributes({"k1": "v"})
        with self.assertRaises(TypeError):
            m6.unset("k1.k2.k3")

    def test_unset_many(self):
        m = Model()
        m.attributes({"k1": "v", "k2": "v", "k3": "v"})
        m.unset_many(["k1", "k2"])
        self.assertEqual(m.attributes.get(), {"k3": "v"})

    def test_push(self):

        # create list, append existing values ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m1 = Model()
        m1.attributes({"k1": "v1"})
        m1.push("k1", "v2")
        self.assertEqual(m1.attributes.get(), {"k1": ["v1", "v2"]})
        m1.push("k1.k2.k3", "v")
        self.assertEqual(m1.attributes.get(), {"k1": {"k2": {"k3": ["v"]}}})

        # dot notation syntax ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m2 = Model()
        m2.attributes({"k1": {"k2": ["v1"]}})
        m2.push("k1.k2", "v2")
        self.assertEqual(m2.attributes.get(), {"k1": {"k2": ["v1", "v2"]}})

        m3 = Model()
        m3.push("k1.k2.k3", "v")
        self.assertEqual(m3.attributes.get(), {"k1": {"k2": {"k3": ["v"]}}})

        # create=False ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m4 = Model()
        with self.assertRaises(KeyError):
            m4.push("k1.k2.k3", "v", create=False)

        m4.set("k1", "v")
        with self.assertRaises(TypeError):
            m4.push("k1.k2.k3", "v", create=False)

        # nested model ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m6 = Model()
        m5 = Model()
        m5.set("r", m6)
        m5.push("r.k", "v")
        self.assertEqual(m6.attributes.get(), {"k": ["v"]})

    def test_push_many(self):
        m1 = Model()
        m1.push_many("k", ["v1", "v2", "v3"])
        self.assertEqual(m1.attributes.get(), {"k": ["v1", "v2", "v3"]})

    def test_pull(self):

        # string ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m1 = Model()
        m1.attributes({"k": ["v1", "v2", "v3"]})
        m1.pull("k", "v2")
        self.assertEqual(m1.attributes.get(), {"k": ["v1", "v3"]})

        # dot notation syntax ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m2 = Model()
        m2.attributes({"k1": {"k2": {"k3": ["v1", "v2", "v3"]}}})
        m2.pull("k1.k2.k3", "v2")
        self.assertEqual(m2.attributes.get(), {
            "k1": {"k2": {"k3": ["v1", "v3"]}}
        })

        # raise exception ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m3 = Model()
        m3.attributes({"k": ["v1", "v2", "v3"]})
        m3.original(m3.attributes)  # force state

        with self.assertRaises(KeyError):
            m3.pull("foo", "bar")

        with self.assertRaises(ValueError):
            m3.pull("k", "bar")

        m4 = Model()
        m4.attributes({"k": "v"})
        m4.original(m4.attributes)  # force state
        with self.assertRaises(TypeError):
            m4.pull("k", "v")

        with self.assertRaises(TypeError):
            m4.pull("k.k2.k3", "v")

        # force=True ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m5 = Model()
        m5.original({"k": "v"})  # force state
        m5.pull("foo", "bar", force=True)
        m5.pull("k", "v", force=True)
        m5.pull("k1.k2.k3", "v", force=True)

        m5.set("k2", "v")
        m5.pull("k2", "v", force=True)

        # nested model ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m7 = Model()
        m7.attributes({"k": ["v1", "v2", "v3"]})
        m6 = Model()
        m6.attributes({"r": m7})
        m6.pull("r.k", "v2")

        self.assertEqual(m7.get("k"), ["v1", "v3"])

    def test_pull_many(self):
        m = Model()
        m.attributes({"k": ["v1", "v2", "v3"]})
        m.pull_many("k", ["v1", "v3"])
        self.assertEqual(m.attributes.get(), {"k": ["v2"]})

    def test_delete(self):
        m1 = Model()
        self.assertEqual(m1._delete, False)
        m1.delete()
        self.assertEqual(m1._delete, True)

        # cascade nested model, simple ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m3 = Model()
        m2 = Model()
        m2.attributes({"r": m3})
        m2.delete(cascade=True)
        self.assertEqual(m2._delete, True)
        self.assertEqual(m3._delete, True)

        # cascade nested model, advanced ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m5 = Model()
        m4 = Model()
        m4.set("r1.r2", m5)
        m4.delete(cascade=True)
        self.assertEqual(m4._delete, True)
        self.assertEqual(m5._delete, True)

    def test_reset(self):
        m = Model()
        m.attributes({"k": "v"})
        m.target({"k": "v"})
        m.delete()
        self.assertEqual(bool(m.target), True)
        self.assertEqual(bool(m.attributes), True)
        self.assertEqual(m._delete, True)

        m.reset()
        self.assertEqual(bool(m.target), False)
        self.assertEqual(bool(m.updates), False)
        self.assertEqual(bool(m.attributes), False)
        self.assertEqual(m._delete, False)

    def test_record_update(self):

        # set ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m1 = Model()
        self.assertEqual(m1.original.get(), {})
        m1.set("k", "v")
        self.assertEqual(m1.updates.get(), {"$set": {"k": "v"}})

        # set dot notation ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m2 = Model()
        m2.set("k1.k2.k3", "v")
        self.assertEqual(m2.updates.get(), {
            "$set": {"k1": {"k2": {"k3": "v"}}}
        })

        # set record=False ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m3 = Model()
        m3.set("k", "v", record=False)
        self.assertEqual(m3.attributes.get(), {"k": "v"})
        self.assertEqual(m3.updates.get(), {})

        # set, original not set ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m4 = Model()
        self.assertEqual(m4.original.get(), {})
        m4.set("k", "v")
        self.assertEqual(m4.updates.get(), {"$set": {"k": "v"}})

        # set, original set ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m5 = Model()
        m5.original({"k": "v"})
        self.assertEqual(m5.original.get(), {"k": "v"})
        m5.set("k", "v")
        self.assertEqual(m5.updates.get(), {})
        m5.set("k", "foo")
        self.assertEqual(m5.updates.get(), {"$set": {"k": "foo"}})
        m5.set("k", "v")
        self.assertEqual(m5.updates.get(), {})

        # unset ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m6 = Model()
        m6.attributes({"k": "v"})
        m6.unset("k")
        self.assertEqual(m6.updates.get(), {"$unset": {"k": ""}})

        # unset, dot notation ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m7 = Model()
        m7.attributes({"k1": {"k2": {"k3": "v"}}})
        m7.unset("k1.k2.k3")
        self.assertEqual(m7.updates.get(), {
            "$unset": {"k1": {"k2": {"k3": ""}}}
        })

        # unset, record=False ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m8 = Model()
        m8.attributes({"k": "v"})
        m8.unset("k", record=False)
        self.assertEqual(m8.attributes.get(), {})
        self.assertEqual(m8.updates.get(), {})

        # unset, original not set ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m9 = Model()
        m9.unset("k")
        self.assertEqual(m9.updates.get(), {"$unset": {"k": ""}})

        # unset, original set ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m10 = Model()
        m10.attributes({"k": "v"})
        m10.original(m10.attributes)
        with self.assertRaises(KeyError):
            m10.unset("foo")

        # unset, force=True ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m11 = Model()
        m11.attributes({"k": "v"})
        m11.unset("foo", force=True)
        self.assertEqual(m11.updates.get(), {"$unset": {"foo": ""}})

        # push ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m12 = Model()
        m12.push("k", "v")
        self.assertEqual(m12.updates.get(), {"$push": {"k": "v"}})

        # push, dot notation ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m13 = Model()
        m13.push("k1.k2.k3", "v")
        self.assertEqual(m13.updates.get(), {
            "$push": {"k1": {"k2": {"k3": "v"}}}
        })

        # push, record=False ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m14 = Model()
        m14.push("k", "v", record=False)
        self.assertEqual(m14.attributes.get(), {"k": ["v"]})
        self.assertEqual(m14.updates.get(), {})

        # push, iterator ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m15 = Model()
        m15.push("k", "v1")
        self.assertEqual(m15.updates.get(), {"$push": {"k": "v1"}})

        m15.push("k", "v2")
        self.assertEqual(m15.updates.get(), {
            "$push": {"k": {"$each": ["v1", "v2"]}}
        })

        # push, intersect pull ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m16 = Model()
        m16.attributes({"k": ["v1", "v2", "v3"]})
        m16.pull("k", "v1")
        m16.pull("k", "v2")
        m16.pull("k", "v3")

        self.assertEqual(m16.updates.get(), {
            "$pull": {"k": {"$in": ["v1", "v2", "v3"]}}
        })

        m16.push("k", "v2")
        self.assertEqual(m16.updates.get(), {
            "$push": {"k": "v2"},
            "$pull": {"k": {"$in": ["v1", "v3"]}}
        })

        # push, pull remove iterator ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m17 = Model()
        m17.attributes({"k": ["v1", "v2"]})
        m17.pull("k", "v1")
        m17.pull("k", "v2")
        self.assertEqual(m17.updates.get(), {
            "$pull": {"k": {"$in": ["v1", "v2"]}}
        })

        m17.push("k", "v2")
        self.assertEqual(m17.updates.get(), {
            "$push": {"k": "v2"},
            "$pull": {"k": "v1"}
        })

        # push, pull remove ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m18 = Model()
        m18.attributes({"k": ["v1"]})
        m18.pull("k", "v1")
        self.assertEqual(m18.updates.get(), {"$pull": {"k": "v1"}})

        m18.push("k", "v1")
        self.assertEqual(m18.updates.get(), {"$push": {"k": "v1"}})

        # pull ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m19 = Model()
        m19.attributes({"k": ["v"]})
        m19.pull("k", "v")
        self.assertEqual(m19.updates.get(), {"$pull": {"k": "v"}})

        # pull, dot notation ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m20 = Model()
        m20.attributes({"k1": {"k2": {"k3": ["v"]}}})
        m20.pull("k1.k2.k3", "v")
        self.assertEqual(m20.updates.get(), {
            "$pull": {"k1": {"k2": {"k3": "v"}}}
        })

        # pull, record=False ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m21 = Model()
        m21.attributes({"k": ["v"]})
        m21.pull("k", "v", record=False)
        self.assertEqual(m21.attributes.get(), {"k": []})
        self.assertEqual(m21.updates.get(), {})

        # pull, iterator ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m22 = Model()
        m22.push("k", "v1")
        self.assertEqual(m22.updates.get(), {"$push": {"k": "v1"}})

        m22.push("k", "v2")
        self.assertEqual(m22.updates.get(), {
            "$push": {"k": {"$each": ["v1", "v2"]}}
        })

        # pull, push intersect ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m23 = Model()
        m23.attributes({"k": ["v1", "v2", "v3"]})
        m23.pull("k", "v1")
        m23.pull("k", "v2")
        m23.pull("k", "v3")
        self.assertEqual(m23.updates.get(), {
            "$pull": {"k": {"$in": ["v1", "v2", "v3"]}}
        })

        m23.push("k", "v2")
        self.assertEqual(m23.updates.get(), {
            "$push": {"k": "v2"},
            "$pull": {"k": {"$in": ["v1", "v3"]}}
        })

        # pull, push remove iterator ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m24 = Model()
        m24.attributes({"k": ["v1", "v2"]})
        m24.pull("k", "v1")
        m24.pull("k", "v2")
        self.assertEqual(m24.updates.get(), {
            "$pull": {"k": {"$in": ["v1", "v2"]}}
        })

        m24.push("k", "v2")
        self.assertEqual(m24.updates.get(), {
            "$push": {"k": "v2"},
            "$pull": {"k": "v1"}
        })

        # pull, push remove ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m25 = Model()
        m25.attributes({"k": ["v1"]})
        m25.pull("k", "v1")
        self.assertEqual(m25.updates.get(), {"$pull": {"k": "v1"}})

        m25.push("k", "v1")
        self.assertEqual(m25.updates.get(), {"$push": {"k": "v1"}})

    def test_save(self):

        # save ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m1 = TestModel()
        m1.attributes({"k": "v"})
        m1.save()

        find_result = get_connection(
            TestModel.mongo_database,
            TestModel.mongo_collection
        ).find_one()

        self.assertEqual(find_result, m1.attributes.get())

        # protected pre insert, post insert hooks ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m2 = TestModel()
        m2.attributes({"k": "v"})
        m2.save()
        self.assertIn(m2.id_attribute, m2.attributes)
        self.assertEqual(
            type(m2.attributes[m2.id_attribute]),
            bson.objectid.ObjectId
        )
        self.assertEqual(m2.attributes, m2.original)
        self.assertEqual(m2.updates.get(), {})
        self.assertEqual(
            {m2.id_attribute: m2.attributes[m2.id_attribute]},
            m2.target.get()
        )

        # target set, changed empty ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m3 = TestModel()
        m3.attributes({"k": "v"})
        m3.save()
        self.assertEqual(
            {m3.id_attribute: m3.attributes[m3.id_attribute]},
            m3.target.get()
        )
        self.assertEqual(m3.updates.get(), {})

        # save model again, no exception raised
        m3.save()

        # update ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m4 = TestModel()
        m4.attributes({"k1": "v"})
        m4_id = m4.save().get(m4.id_attribute)

        m5 = TestModel()
        m5.set_target(m4_id)
        m5.find()
        m5.set("k2", "v")
        m5.save()

        m6 = TestModel()
        m6.set_target(m4_id)
        m6.find()

        self.assertEqual(m5.attributes, m6.attributes)

        # push, pull iterators ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m7 = TestModel()
        m7.save()
        m7.set("k1.k2.k3", "v")
        m7.push_many("k", ["v", "v", "v"])
        m7.save()

        m8 = TestModel(m7.get_target()).find()
        self.assertEqual(m7.attributes, m8.attributes)

        # update without find ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m9 = TestModel()
        m9.set("k1", "v")
        m9_id = m9.save().get(m9.id_attribute)

        m10 = TestModel()
        m10.set_target(m9_id)
        m10.set("k2", "v")
        m10.save()

        m11 = TestModel(m9_id)
        m11.find()

        self.assertEqual(m11.get(), {
            m9.id_attribute: m9_id,
            "k1": "v",
            "k2": "v"
        })

        # protected pre update, post update hooks ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m12 = TestModel()
        m12.set("k", "v")
        self.assertEqual(m12.target.get(), {})
        self.assertEqual(m12.original.get(), {})
        self.assertEqual(m12.updates.get(), {"$set": {"k": "v"}})

        m12.save()
        self.assertEqual(
            type(m12.target[m12.id_attribute]),
            bson.objectid.ObjectId
        )
        self.assertEqual(
            m12.original.get(),
            {
                m12.id_attribute: m12.attributes[m12.id_attribute],
                "k": "v"
            }
        )
        self.assertEqual(m12.updates.get(), {})

        # raise exception ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m13 = TestModel()
        m13.set_target(bson.objectid.ObjectId())
        m13.set("k", "v")
        m13.original({"k": "v"})
        with self.assertRaises(ModelNotUpdated):
            m13.save()

        # delete ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m14 = TestModel()
        m14.save()
        m14.delete()
        m14.save()

        m15 = TestModel()
        m15.set_target(m14.get_target())
        with self.assertRaises(ModelNotFound):
            m15.find()

        # raise exception, model not deleted ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m16 = TestModel()
        m16.set("k", "v")
        m16.save()
        m16.delete()
        self.assertEqual(m16._delete, True)

        m16.save()

        m17 = TestModel()
        m17.set_target(m16.get_target())
        m17.delete()
        with self.assertRaises(ModelNotDeleted):
            m17.save()

        # raise exception, model target not set ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        m18 = TestModel()
        m18.save()
        m18.target = {}
        m18.delete()

        with self.assertRaises(ModelTargetNotSet):
            m18.save()

        # extendable pre insert hook ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class PreInsertHook1(TestModel):
            def pre_insert_hook(self):
                self.set("created", datetime.datetime.today())

        m19 = PreInsertHook1()
        m19.save()
        self.assertIn("created", m19.attributes.get())
        self.assertEqual(datetime.datetime, type(m19.attributes["created"]))

        # extendable post insert hook ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class PostInsertHook1(TestModel):
            def post_insert_hook(self):
                self.set_baz()

            def set_baz(self):
                baz = "{} {}".format(self.get("foo"), self.get("bar"))
                self.set("baz", baz)

        m20 = PostInsertHook1()
        m20.set("foo", "Foo")
        m20.set("bar", "Bar")
        m20.save()
        self.assertEqual(m20.get("baz"), "Foo Bar")

        # extendable pre update hook ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class PreUpdateHook1(TestModel):
            def pre_update_hook(self):
                self.set("updated", datetime.datetime.today())

        m21 = PreUpdateHook1()
        m21.save()
        self.assertNotIn("updated", m21.attributes)

        m21.set("k", "v")
        m21.save()
        self.assertIn("updated", m21.attributes)
        self.assertEqual(datetime.datetime, type(m21.attributes["updated"]))

        # extendable post update hook ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class PostUpdateHook1(TestModel):
            def post_update_hook(self):
                self.set_baz()

            def set_baz(self):
                baz = "{} {}".format(self.get("foo"), self.get("bar"))
                self.set("baz", baz)

        m22 = PostUpdateHook1()
        m22.save()
        self.assertNotIn("baz", m22.attributes)

        m22.set("foo", "Foo")
        m22.set("bar", "Bar")
        m22.save()
        self.assertEqual(m22.get("baz"), "Foo Bar")

        # extendable pre delete hook ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class PreDeleteHook1(TestModel):
            def pre_delete_hook(self):
                m24 = TestModel()
                m24.set_target(self.get_target())
                m24.find()
                self.set("d", m24.get())

        m23 = PreDeleteHook1()
        m23.set("k", "v")
        m23.save()
        self.assertNotIn("d", m23.attributes)

        m23.delete()
        m23.save()
        self.assertIn("d", m23.attributes)
        self.assertEqual(m23.get("d"), {
            m23.id_attribute: m23.attributes[m23.id_attribute],
            "k": "v"
        })

        m24 = TestModel(m23.attributes[m23.id_attribute])
        with self.assertRaises(ModelNotFound):
            m24.find()

        # extendable post delete hook ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        class PostDeleteHook1(TestModel):
            def post_delete_hook(self):
                m26 = TestModel()
                m26.set(m26.id_attribute, self.get_id())
                m26.save()

        m25 = PostDeleteHook1()
        m25.set("k1", "v")
        m25.set("k2", "v")
        m25.set("k3", "v")
        m25.save()
        m25.delete()
        m25.save()

        m26 = PostDeleteHook1(m25.get(m25.id_attribute))
        m26.find()
        self.assertEqual(m26.attributes.get(), {
            m26.id_attribute: m25.get(m26.id_attribute)
        })

    def test_reference_nested_models(self):
        m2 = TestModel()
        m2.save()

        m1 = TestModel()
        m1.set("r", m2)
        m1.save()

        m3 = TestModel(m1.get_id()).find()

        self.assertEqual(type(m3.attributes["r"]), bson.objectid.ObjectId)
        self.assertEqual(m3.get("r"), m2.get(m2.id_attribute))


if __name__ == "__main__":
    unittest.main()
