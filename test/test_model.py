
import sys; sys.path.append("../") # noqa

import unittest
import copy
import pymongo
import datetime
import bson

from baemo.connection import Connections
from baemo.delimited import DelimitedDict
from baemo.references import References
from baemo.projection import Projection

from baemo.entity import Entity

from baemo.exceptions import ModelTargetNotSet
from baemo.exceptions import ModelNotUpdated
from baemo.exceptions import ModelNotFound
from baemo.exceptions import ModelNotDeleted
from baemo.exceptions import ProjectionTypeMismatch
from baemo.exceptions import DereferenceError


class TestModel(unittest.TestCase):

    def setUp(self):
        global connection_name, collection_name, TestModel

        connection_name = "baemo"
        collection_name = "{}_{}".format(self.__class__.__name__, self._testMethodName)

        connection = pymongo.MongoClient(connect=False)[connection_name]
        Connections.set(connection_name, connection)

        TestModel, TestCollection = Entity("TestModel", {
            "connection": connection_name,
            "collection": collection_name
        })

    def tearDown(self):
        global connection_name, collection_name
        Connections.get(connection_name).drop_collection(collection_name)

    # __init__

    def test___init____no_params(self):
        m = TestModel()
        self.assertEqual(m.id_attribute, "_id")
        self.assertEqual(type(m.collection), str)
        self.assertEqual(type(m.target), DelimitedDict)
        self.assertEqual(type(m.attributes), DelimitedDict)
        self.assertEqual(type(m.references), References)

        self.assertEqual(type(m.find_projection), Projection)
        self.assertEqual(type(m.get_projection), Projection)

        self.assertEqual(m._delete, False)
        self.assertEqual(type(m.original), DelimitedDict)
        self.assertEqual(type(m.updates), DelimitedDict)

    def test___init____dict_target_param(self):
        m = TestModel({"k": "v"})
        self.assertEqual(m.target.get(), {"k": "v"})

    def test___init____target_param(self):
        m = TestModel("value")
        self.assertEqual(m.target.get(), {"_id": "value"})

    # __copy__

    def test___copy__(self):
        m1 = TestModel({"k": "v"})
        m2 = copy.copy(m1)
        self.assertIsNot(m1, m2)
        self.assertEqual(m1.attributes, m2.attributes)
        m1.attributes["k"] = "bar"
        self.assertEqual(m1.attributes, m2.attributes)

    # __deepcopy__

    def test___deepcopy__(self):
        m1 = TestModel({"k": "v"})
        m2 = copy.deepcopy(m1)
        self.assertIsNot(m1, m2)
        self.assertEqual(m1.attributes, m2.attributes)
        m1.attributes["k"] = "bar"
        self.assertNotEqual(m1.attributes, m2.attributes)

    # __eq__

    def test___eq____same_attributes__returns_True(self):
        m1 = TestModel()
        m1.attributes({"k": "v"})
        m2 = TestModel()
        m2.attributes({"k": "v"})
        self.assertTrue(m1 == m2)

    def test___eq____different_attributes__returns_False(self):
        m1 = TestModel()
        m1.attributes({"foo": "bar"})
        m2 = TestModel()
        m2.attributes({"baz": "qux"})
        self.assertFalse(m1 == m2)

    def test___eq____different_types__returns_False(self):
        m1 = TestModel()
        m1.attributes({"k": "v"})
        m2 = object()
        self.assertFalse(m1 == m2)

    # __ne__

    def test___ne____same_attributes__returns_False(self):
        m1 = TestModel()
        m1.attributes({"k": "v"})
        m2 = TestModel()
        m2.attributes({"k": "v"})
        self.assertFalse(m1 != m2)

    def test___ne____different_attributes__returns_True(self):
        m1 = TestModel()
        m1.attributes({"foo": "bar"})
        m2 = TestModel()
        m2.attributes({"baz": "qux"})
        self.assertTrue(m1 != m2)

    def test___ne____different_types__returns_True(self):
        m1 = TestModel({"foo": "bar"})
        m2 = object()
        self.assertTrue(m1 != m2)

    # set_target

    def test_set_target__dict_param(self):
        m = TestModel()
        m.set_target({"k": "v"})
        self.assertEqual(m.target.get(), {"k": "v"})

    def test_set_target__string_param(self):
        m = TestModel()
        m.set_target("foo")
        self.assertEqual(m.target.get(), {"_id": "foo"})

    # get_target

    def test_get_target__target_not_set__returns_None(self):
        m = TestModel()
        self.assertEqual(m.get_target(), None)

    def test_get_target__target_set__returns_dict(self):
        m = TestModel()
        m.target = DelimitedDict({"k": "v"})
        self.assertEqual(m.get_target(), {"k": "v"})

    def test_get_id__id_not_set__returns_None(self):
        m = TestModel()
        self.assertEqual(m.get_id(), None)

    def test_get_id__id_set__returns_id_type(self):
        m = TestModel()
        m.target = DelimitedDict({"_id": "foo"})
        self.assertEqual(m.get_id(), "foo")

    # find

    def test_find(self):
        original = TestModel()
        original.attributes({"k": "v"})
        original_id = original.save().get(original.id_attribute)

        m = TestModel()
        m.target({original.id_attribute: original_id})
        m.find()

        self.assertIn("k", m.attributes)
        self.assertEqual(m.attributes["k"], "v")

    def test_find__raises_ModelTargetNotSet(self):
        m = TestModel()
        with self.assertRaises(ModelTargetNotSet):
            m.find()

    def test_find__default_find_projection(self):
        global connection_name, collection_name

        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name,
            "find_projection": {
                "k1": 0
            }
        })

        original = TestModel()
        original.attributes({"k1": "v", "k2": "v", "k3": "v"})
        original_id = original.save().attributes[TestModel().id_attribute]

        m = TestModel()
        m.target({original.id_attribute: original_id})
        m.find()

        self.assertEqual(m.attributes.get(), {
            TestModel.id_attribute: original_id,
            "k2": "v",
            "k3": "v"
        })

    def test_find__projection_param(self):
        original = TestModel()
        original.attributes({"k1": "v", "k2": "v", "k3": "v"})
        original_id = original.save().attributes[TestModel.id_attribute]

        m = TestModel()
        m.target({original.id_attribute: original_id})
        m.find(projection={"k1": 0})

        self.assertEqual(m.attributes.get(), {
            original.id_attribute: original_id,
            "k2": "v",
            "k3": "v"
        })

    def test_find__default_find_projection__projection_param(self):

        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name,
            "find_projection": {
                "k1": 0
            }
        })

        original = TestModel()
        original.attributes({"k1": "v", "k2": "v", "k3": "v"})
        original_id = original.save().attributes[TestModel.id_attribute]

        m = TestModel()
        m.target({original.id_attribute: original_id})
        m.find(projection={"k3": 0}, default=True)
        self.assertEqual(m.attributes.get(), {
            original.id_attribute: original_id, "k2": "v"
        })

        self.tearDown()

    def test_find__pre_find_hook(self):
        class ModelAbstract(object):
            def pre_find_hook(self):
                self.target({"k": "v"})

        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name,
            "find_projection": {
                "k1": 0
            },
            "bases": ModelAbstract
        })

        m = TestModel()
        m.target({"foo": "baz"})
        try:
            m.find()
        except:
            pass

        self.assertEqual(m.target.get(), {"k": "v"})

    def test_find__post_find_hook(self):
        class ModelAbstract(object):
            def post_find_hook(self):
                self.target({"k": "v"})

        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name,
            "bases": ModelAbstract
        })

        m = TestModel()
        m.set("foor", "bar")
        m.save()

        copy = TestModel(m.get("_id"))
        copy.find()

        self.assertEqual(copy.target.get(), {"k": "v"})

    # ref

    def test_ref__no_params(self):
        value = "v"
        m = TestModel()
        m.attributes({"k": value})
        self.assertIs(m.ref()["k"], value)

    def test_ref__string_param(self):
        value = "v"
        m = TestModel()
        m.attributes({"k": value})
        self.assertIs(m.ref("k"), value)

    def test_ref__delimited_string_param(self):
        value = "v"
        m = TestModel()
        m.attributes({"k1": {"k2": {"k3": value}}})
        self.assertIs(m.ref("k1.k2.k3"), value)

    def test_ref__handle_dereference_error(self):
        m = TestModel()
        m.attributes({"k": DereferenceError()})
        self.assertIsInstance(m.ref("k"), DereferenceError)

    def test_ref__nested_entity(self):
        value = "v"
        child = TestModel()
        child.attributes({"k": value})
        parent = TestModel()
        parent.attributes({"child": child})
        self.assertIs(child.ref("k"), value)
        self.assertIs(parent.ref("child.k"), value)

    def test_ref__string_key_True_create_params__creates_missing_attributes(self):
        m = TestModel()
        m.ref("k", create=True)
        self.assertEqual(m.attributes.get(), {"k": {}})

    def test_ref__delimited_string_key_True_create_params__creates_missing_keys(self):
        m = TestModel()
        m.ref("k1.k2.k3", create=True)
        self.assertEqual(m.attributes.get(), {
            "k1": {
                "k2": {
                    "k3": {}
                }
            }
        })

    # has

    def test_has__string_param__key_exists__returns_True(self):
        m = TestModel()
        m.attributes({"k": "v"})
        self.assertTrue(m.has("k"))

    def test_has__string_param__key_does_not_exist__returns_False(self):
        m = TestModel()
        m.attributes({"k": "v"})
        self.assertFalse(m.has("foo"))

    def test_has__delimited_string_param__key_exists__returns_True(self):
        m = TestModel()
        m.attributes({"k1": {"k2": {"k3": "v"}}})
        self.assertTrue(m.has("k1.k2.k3"))

    def test_has__delimited_string_param__key_does_not_exist__returns_False(self):
        m = TestModel()
        m.attributes({"k1": {"k2": {"k3": "v"}}})
        self.assertFalse(m.has("k1.k2.foo"))

    def test_has__nested_entity__key_exists__returns_True(self):
        child = TestModel()
        child.attributes({"k": "v"})
        parent = TestModel()
        parent.attributes({"child": child})
        self.assertTrue(parent.has("child.k"))

    def test_has__nested_entity__key_does_not_exist__returns_False(self):
        child = TestModel()
        child.attributes({"k": "v"})
        parent = TestModel()
        parent.attributes({"child": child})
        self.assertFalse(parent.has("child.foo"))

    def test_has__delimited_string_param__dereference_error__returns_False(self):
        m = TestModel()
        m.attributes({"k": DereferenceError()})
        self.assertFalse(m.has("k.foo"))

    # get

    def test_get__no_params__returns_value_copy(self):
        value = {"k1": "v", "k2": "v", "k3": "v"}
        m = TestModel()
        m.attributes(value)
        self.assertEqual(m.get(), {"k1": "v", "k2": "v", "k3": "v"})
        self.assertIsNot(m.get(), value)

    def test_get__exclusive_default_get_projection(self):
        TestModel, TestCollection = Entity("Test", {
            "get_projection": {
                "k1": 0
            }
        })

        m = TestModel()
        m.attributes({"k1": "v", "k2": "v"})
        self.assertEqual(m.get(), {
            "k2": "v"
        })

    def test_get__exclusive_default_get_projection__projection_param(self):
        TestModel, TestCollection = Entity("Test", {
            "get_projection": {
                "k1": 0
            }
        })

        m = TestModel()
        m.attributes({"k1": "v", "k2": "v"})
        self.assertEqual(m.get(projection={"k3": 0}), {
            "k2": "v"
        })

    def test_get__inclusive_default_get_projection(self):
        TestModel, TestCollection = Entity("Test", {
            "get_projection": {
                "k1": 1
            }
        })

        m = TestModel()
        m.attributes({"k1": "v", "k2": "v"})
        self.assertEqual(m.get(), {
            "k1": "v"
        })

    def test_get__inclusive_default_get_projection__projection_param(self):
        TestModel, TestCollection = Entity("Test", {
            "get_projection": {
                "k1": 1
            }
        })

        m = TestModel()
        m.attributes({"k1": "v", "k2": "v", "k3": "v"})
        self.assertEqual(m.get(projection={"k3": 1}), {
            "k1": "v",
            "k3": "v"
        })

    def test_get__nested_projection_param(self):
        m = TestModel()
        m.attributes({
            "k1": {
                "k2": "v",
                "k3": "v",
                "k4": "v"
            }
        })

        self.assertEqual(m.get(projection={"k1": {"k2": 0}}), {
            "k1": {
                "k3": "v",
                "k4": "v"
            }
        })

    def test_get__string_param__returns_value(self):
        m = TestModel()
        m.attributes({"k": "v"})
        self.assertEqual(m.get("k"), "v")

    def test_get__string_and_default_params__returns_default_value(self):
        m = TestModel()
        self.assertEqual(m.get("k", "Default"), "Default")

    def test_get__delimited_string__returns_value(self):
        m = TestModel()
        m.attributes({"k1": {"k2": {"k3": "v"}}})
        self.assertEqual(m.get("k1.k2.k3"), "v")

    def test_get__delimited_string__projection_param(self):
        m = TestModel()
        m.attributes({"k1": {"k2": {"k3": {"k4": "v", "k5": "v", "k6": "v"}}}})
        self.assertEqual(
            m.get("k1.k2.k3", projection={"k1.k2.k3.k5": 0}),
            {"k4": "v", "k6": "v"}
        )

    def test_get__nested_entity__no_params(self):
        child = TestModel()
        child.attributes({"k": "v"})
        parent = TestModel()
        parent.attributes({"child": child})
        self.assertEqual(parent.get(), {"child": {"k": "v"}})

    def test_get__nested_entity__delimited_string_param(self):
        child = TestModel()
        child.attributes({"k": "v"})
        parent = TestModel()
        parent.attributes({"child": child})
        self.assertEqual(parent.get("child.k"), "v")

    def test_get__nested_entity__delimited_string_and_projection_params(self):
        child = TestModel()
        child.attributes({"k1": "v", "k2": "v", "k3": "v"})
        parent = TestModel()
        parent.attributes({"child": child})
        self.assertEqual(parent.get("child", projection={"child.k1": 0}), {
            "k2": "v",
            "k3": "v"
        })

    def test_get__DereferenceError(self):
        child = TestModel()
        child.attributes({"k": DereferenceError(data={"k": "v"})})
        parent = TestModel()
        parent.attributes({"child": child})
        self.assertEqual(parent.get("child.k"), {
            "message": "Dereference error",
            "data": {
                "k": "v"
            }
        })

    # generate_id

    def test_generate_id(self):
        self.assertIsInstance(TestModel().generate_id(), TestModel.id_type)

    # set

    def test_set__string_param(self):
        m = TestModel()
        m.set("k", "v")
        self.assertEqual(m.attributes.get(), {"k": "v"})

    def test_set__dict_param(self):
        m = TestModel()
        m.set({"k": "v"})
        self.assertEqual(m.attributes.get(), {"k": "v"})

    def test_set__nested_dict_param(self):
        m = TestModel()
        m.set("k", {"foo": {"bar": {"baz": "qux"}}})
        self.assertEqual(m.attributes.get(), {"k": {"foo": {"bar": {"baz": "qux"}}}})

    def test_set__delimited_string_param(self):
        m = TestModel()
        m.set("k1.k2.k3", "v")
        self.assertEqual(m.attributes.get(), {"k1": {"k2": {"k3": "v"}}})

    def test_set__nested_entity(self):
        child = TestModel()
        child.attributes({"k": "v"})
        parent = TestModel()
        parent.attributes({"child": child})
        parent.set("child.k", "foo")
        self.assertEqual(child.attributes.get(), {"k": "foo"})

    def test_set__DereferenceError(self):
        m = TestModel()
        m.attributes({"k": DereferenceError()})
        m.set("k", "v")
        self.assertEqual(m.get(), {"k": "v"})

    def test_set__False_create_param__raises_KeyError(self):
        m = TestModel()
        with self.assertRaises(KeyError):
            m.set("k", "v", create=False)

    def test_set__False_create_Eparam_raises_TypeError(self):
        m = TestModel()
        m.attributes({"k1": {"k2": "v"}})
        with self.assertRaises(TypeError):
            m.set("k1.k2.k3", "v", create=False)

    def test_set__False_create_param_DereferenceError__raisesTypeError(self):
        m = TestModel()
        m.attributes({"k1": DereferenceError()})
        with self.assertRaises(TypeError):
            m.set("k1.k2", "v", create=False)

    # unset

    def test_unset__string_param(self):
        m = TestModel()
        m.attributes({"k1": "v", "k2": "v", "k3": "v"})
        m.unset("k1")
        self.assertEqual(m.attributes.get(), {"k2": "v", "k3": "v"})

    def test_unset__delimited_string_param(self):
        m = TestModel()
        m.attributes({"k1": {"k2": "v"}, "k3": "v"})
        m.unset("k1.k2")
        self.assertEqual(m.attributes.get(), {"k1": {}, "k3": "v"})

    def test_unset__nested_entity(self):
        child = TestModel()
        child.attributes({"k1": "v", "k2": "v", "k3": "v"})
        parent = TestModel()
        parent.attributes({"child": child})
        parent.unset("child.k2")
        self.assertEqual(child.attributes.get(), {"k1": "v", "k3": "v"})

    def test_unset__True_force_param__no_exception_raised(self):
        m = TestModel()
        m.original({"k": "v"})
        try:
            m.unset("k", force=True)
        except Exception:
            self.fail("exception raised")

    def test_unset__string_param__raises_KeyError(self):
        m = TestModel()
        m.original({"k": "v"}) # force state
        with self.assertRaises(KeyError):
            m.unset("k")

    def test_unset__delimited_string_param__raises_TypeError(self):
        m = TestModel()
        m.attributes({"k1": "v"})
        m.original({"k1": "v"}) # force state
        with self.assertRaises(TypeError):
            m.unset("k1.k2.k3")

    def test_unset__DereferenceError__raises_TypeError(self):
        m = TestModel()
        m.attributes({"k1": DereferenceError()})
        m.original({"k1": "v"}) # force state
        with self.assertRaises(TypeError):
            m.unset("k1.k2.k3")

    # unset_many

    def test_unset_many(self):
        m = TestModel()
        m.attributes({"k1": "v", "k2": "v", "k3": "v"})
        m.unset_many(["k1", "k2"])
        self.assertEqual(m.attributes.get(), {"k3": "v"})

    # push

    def test_push(self):
        m = TestModel()
        m.attributes({"k": []})
        m.push("k", "v")
        self.assertEqual(m.get(), {"k": ["v"]})

    def test_push__create_container(self):
        m = TestModel()
        m.push("k", "v")
        self.assertEqual(m.get(), {"k": ["v"]})

    def test_push__handle_existing_values(self):
        m = TestModel()
        m.attributes({"k": "foo"})
        m.push("k", "bar")
        self.assertEqual(m.get(), {"k": ["foo", "bar"]})

    def test_push__dot_notation_string_param(self):
        m = TestModel()
        m.attributes({"k1": {"k2": {"k3": ["foo"]}}})
        m.push("k1.k2.k3", "bar")
        self.assertEqual(m.attributes.get(), {"k1": {"k2": {"k3": ["foo", "bar"]}}})

    def test_push__False_create_param__raises_KeyError(self):
        m = TestModel()
        with self.assertRaises(KeyError):
            m.push("k1.k2.k3", "v", create=False)

    def test_push__False_create_param__raises_TypeError(self):
        m = TestModel()
        m.attributes({"k1": {"k2": "v"}})
        with self.assertRaises(TypeError):
            m.push("k1.k2.k3", "v", create=False)

    def test_push__nested_entity(self):
        child = TestModel()
        child.attributes({"k": ["foo"]})
        parent = TestModel()
        parent.attributes({"child": child})
        parent.push("child.k", "bar")
        self.assertEqual(child.attributes.get(), {"k": ["foo", "bar"]})

    # push_many

    def test_push_many(self):
        m = TestModel()
        m.push_many("k", ["v1", "v2", "v3"])
        self.assertEqual(m.attributes.get(), {"k": ["v1", "v2", "v3"]})

    # pull

    def test_pull__string_param(self):
        m = TestModel()
        m.attributes({"k": ["v1", "v2", "v3"]})
        m.pull("k", "v2")
        self.assertEqual(m.attributes.get(), {"k": ["v1", "v3"]})

    def test_pull__delimited_string_param(self):
        m = TestModel()
        m.attributes({"k1": {"k2": {"k3": ["foo", "bar"]}}})
        m.pull("k1.k2.k3", "foo")
        self.assertEqual(m.attributes.get(), {"k1": {"k2": {"k3": ["bar"]}}})

    def test_pull__missing_key__raises_KeyError(self):
        m = TestModel()
        m.attributes({"foo": "bar"})
        m.original(m.attributes)
        with self.assertRaises(KeyError):
            m.pull("k", "v")

    def test_pull__True_force_param__KeyError_not_raised(self):
        m = TestModel()
        m.attributes({"foo": "bar"})
        m.original(m.attributes) # force state
        try:
            m.pull("k", "v", force=True)
        except Exception:
            self.fail("exception raised")

    def test_pull__incorrect_type__raises_TypeError(self):
        m = TestModel()
        m.attributes({"k": "v"})
        m.original(m.attributes) # force state
        with self.assertRaises(TypeError):
            m.pull("k", "v")

    def test_pull__delimited_string_param__incorrect_type__raises_TypeError(self):
        m = TestModel()
        m.attributes({"k1": {"k2": "v"}})
        m.original(m.attributes) # force state
        with self.assertRaises(TypeError):
            m.pull("k1.k2.k3", "v")

    def test_pull__True_force_param__TypeError_not_raised(self):
        m = TestModel()
        m.attributes({"k": "v"})
        try:
            m.pull("k", "v", force=True)
        except Exception:
            self.fail("exception raised")

    def test_pull__missing_value__raises_ValueError(self):
        m = TestModel()
        m.attributes({"k": ["foo"]})
        m.original(m.attributes) # force state
        with self.assertRaises(ValueError):
            m.pull("k", "bar")

    def test_pull__True_force_param__ValueError_not_raised(self):
        m = TestModel()
        m.attributes({"k": ["foo"]})
        try:
            m.pull("k", "bar", force=True)
        except Exception:
            self.fail("exception raised")

    def test_pull__nested_entity(self):
        child = TestModel()
        child.attributes({"k": ["foo", "bar"]})
        parent = TestModel()
        parent.attributes({"child": child})
        parent.pull("child.k", "bar")
        self.assertEqual(child.attributes.get(), {"k": ["foo"]})

    # pull_many

    def test_pull_many(self):
        m = TestModel()
        m.attributes({"k": ["v1", "v2", "v3"]})
        m.pull_many("k", ["v1", "v3"])
        self.assertEqual(m.attributes.get(), {"k": ["v2"]})

    # delete

    def test_delete(self):
        m = TestModel()
        self.assertFalse(m._delete)
        m.delete()
        self.assertTrue(m._delete)

    def test_delete__cascade(self):

        p = TestModel()
        c = TestModel()

        p.set("c", c)

        self.assertFalse(p._delete)
        self.assertFalse(c._delete)

        p.delete(cascade=True)

        self.assertTrue(p._delete)
        self.assertTrue(c._delete)

    # reset

    def test_reset(self):
        m = TestModel()
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

    # record_update

    def test_record_update__set__string(self):
        m = TestModel()
        self.assertEqual(m.original.get(), {})
        m.set("k", "v")
        self.assertEqual(m.updates.get(), {"$set": {"k": "v"}})

    def test_record_update__set__delimited_string(self):
        m = TestModel()
        m.set("k1.k2.k3", "v")
        self.assertEqual(m.updates.get(), {
            "$set": {"k1": {"k2": {"k3": "v"}}}
        })

    def test_record_update__set__False_record_param(self):
        m = TestModel()
        m.set("k", "v", record=False)
        self.assertEqual(m.attributes.get(), {"k": "v"})
        self.assertEqual(m.updates.get(), {})

    def test_record_update__set__original_not_set(self):
        m = TestModel()
        self.assertEqual(m.original.get(), {})
        m.set("k", "v")
        self.assertEqual(m.updates.get(), {"$set": {"k": "v"}})

    def test_record_update__set__original_set(self):
        m = TestModel()
        m.original({"k": "v"})
        self.assertEqual(m.original.get(), {"k": "v"})
        m.set("k", "v")
        self.assertEqual(m.updates.get(), {})
        m.set("k", "foo")
        self.assertEqual(m.updates.get(), {"$set": {"k": "foo"}})
        m.set("k", "v")
        self.assertEqual(m.updates.get(), {})

    def test_record_update__unset__string(self):
        m = TestModel()
        m.attributes({"k": "v"})
        m.unset("k")
        self.assertEqual(m.updates.get(), {"$unset": {"k": ""}})

    def test_record_update__unset__delimited_string(self):
        m = TestModel()
        m.attributes({"k1": {"k2": {"k3": "v"}}})
        m.unset("k1.k2.k3")
        self.assertEqual(m.updates.get(), {
            "$unset": {"k1": {"k2": {"k3": ""}}}
        })

    def test_record_update__unset__False_record_param(self):
        m = TestModel()
        m.attributes({"k": "v"})
        m.unset("k", record=False)
        self.assertEqual(m.attributes.get(), {})
        self.assertEqual(m.updates.get(), {})

    def test_record_update__unset__original_not_set(self):
        m = TestModel()
        m.unset("k")
        self.assertEqual(m.updates.get(), {"$unset": {"k": ""}})

    def test_record_update__unset__original_set(self):
        m = TestModel()
        m.attributes({"k": "v"})
        m.original(m.attributes)
        with self.assertRaises(KeyError):
            m.unset("foo")

    def test_record_update__unset__True_force_param(self):
        m = TestModel()
        m.attributes({"k": "v"})
        m.unset("foo", force=True)
        self.assertEqual(m.updates.get(), {"$unset": {"foo": ""}})

    def test_record_update__push__string(self):
        m = TestModel()
        m.push("k", "v")
        self.assertEqual(m.updates.get(), {"$push": {"k": "v"}})

    def test_record_update__push__dict(self):
        m = TestModel()
        m.set("k", [{"k": "v"}])
        m.save()
        m.push("k", {"k": "v"})
        self.assertEqual(m.updates.get(), {"$push": {"k": {"k": "v"}}})

    def test_record_update__push__delimited_string(self):
        m = TestModel()
        m.push("k1.k2.k3", "v")
        self.assertEqual(m.updates.get(), {
            "$push": {"k1": {"k2": {"k3": "v"}}}
        })

    def test_record_update__push__False_record_param(self):
        m = TestModel()
        m.push("k", "v", record=False)
        self.assertEqual(m.attributes.get(), {"k": ["v"]})
        self.assertEqual(m.updates.get(), {})

    def test_record_update__push__set_iterator(self):
        m = TestModel()
        m.push("k", "v1")
        self.assertEqual(m.updates.get(), {"$push": {"k": "v1"}})

        m.push("k", "v2")
        self.assertEqual(m.updates.get(), {
            "$push": {"k": {"$each": ["v1", "v2"]}}
        })

    def test_record_update__push__intersect_pull(self):
        m = TestModel()
        m.attributes({"k": ["v1", "v2", "v3"]})
        m.pull("k", "v1")
        m.pull("k", "v2")
        m.pull("k", "v3")

        self.assertEqual(m.updates.get(), {
            "$pull": {"k": {"$in": ["v1", "v2", "v3"]}}
        })

        m.push("k", "v2")
        self.assertEqual(m.updates.get(), {
            "$push": {"k": "v2"},
            "$pull": {"k": {"$in": ["v1", "v3"]}}
        })

    def test_record_update__push__intersect_pull_remove_iterator(self):
        m = TestModel()
        m.attributes({"k": ["v1", "v2"]})
        m.pull("k", "v1")
        m.pull("k", "v2")
        self.assertEqual(m.updates.get(), {
            "$pull": {"k": {"$in": ["v1", "v2"]}}
        })

        m.push("k", "v2")
        self.assertEqual(m.updates.get(), {
            "$push": {"k": "v2"},
            "$pull": {"k": "v1"}
        })

    def test_record_update__push__intersect_pull_remove_operator(self):
        m = TestModel()
        m.attributes({"k": ["v1"]})
        m.pull("k", "v1")
        self.assertEqual(m.updates.get(), {"$pull": {"k": "v1"}})

        m.push("k", "v1")
        self.assertEqual(m.updates.get(), {"$push": {"k": "v1"}})

    def test_record_update__pull__string(self):
        m = TestModel()
        m.attributes({"k": ["v"]})
        m.pull("k", "v")
        self.assertEqual(m.updates.get(), {"$pull": {"k": "v"}})

    def test_record_update__pull__delimited_string(self):
        m = TestModel()
        m.attributes({"k1": {"k2": {"k3": ["v"]}}})
        m.pull("k1.k2.k3", "v")
        self.assertEqual(m.updates.get(), {
            "$pull": {"k1": {"k2": {"k3": "v"}}}
        })

    def test_record_update__pull__False_record_param(self):
        m = TestModel()
        m.attributes({"k": ["v"]})
        m.pull("k", "v", record=False)
        self.assertEqual(m.attributes.get(), {"k": []})
        self.assertEqual(m.updates.get(), {})

    def test_record_update__pull__set_iterator(self):
        m = TestModel()
        m.push("k", "v1")
        self.assertEqual(m.updates.get(), {"$push": {"k": "v1"}})

        m.push("k", "v2")
        self.assertEqual(m.updates.get(), {
            "$push": {"k": {"$each": ["v1", "v2"]}}
        })

    def test_record_update__pull__intersect_push(self):
        m = TestModel()
        m.attributes({"k": ["v1", "v2", "v3"]})
        m.pull("k", "v1")
        m.pull("k", "v2")
        m.pull("k", "v3")
        self.assertEqual(m.updates.get(), {
            "$pull": {"k": {"$in": ["v1", "v2", "v3"]}}
        })

        m.push("k", "v2")
        self.assertEqual(m.updates.get(), {
            "$push": {"k": "v2"},
            "$pull": {"k": {"$in": ["v1", "v3"]}}
        })

    def test_record_update__pull__intersect_push_remove_iterator(self):
        m = TestModel()
        m.attributes({"k": ["v1", "v2"]})
        m.pull("k", "v1")
        m.pull("k", "v2")
        self.assertEqual(m.updates.get(), {
            "$pull": {"k": {"$in": ["v1", "v2"]}}
        })

        m.push("k", "v2")
        self.assertEqual(m.updates.get(), {
            "$push": {"k": "v2"},
            "$pull": {"k": "v1"}
        })

    def test_record_update__pull__inersect_push_remove_operator(self):
        m = TestModel()
        m.attributes({"k": ["v1"]})
        m.pull("k", "v1")
        self.assertEqual(m.updates.get(), {"$pull": {"k": "v1"}})

        m.push("k", "v1")
        self.assertEqual(m.updates.get(), {"$push": {"k": "v1"}})

    # save

    def test_save__insert(self):
        m = TestModel()
        m.attributes({"k": "v"})
        m.save()

        find_result = Connections.get(
            m.connection,
            m.collection
        ).find_one()

        self.assertEqual(find_result, m.attributes.get())

    def test_save__insert__protected_post_insert_hook(self):
        m = TestModel()
        m.attributes({"k": "v"})
        m.save()
        self.assertIn(m.id_attribute, m.attributes)
        self.assertEqual(
            type(m.attributes[m.id_attribute]),
            bson.objectid.ObjectId
        )
        self.assertEqual(m.attributes, m.original)
        self.assertEqual(m.updates.get(), {})
        self.assertEqual(
            {m.id_attribute: m.attributes[m.id_attribute]},
            m.target.get()
        )

    def test_save__insert__target_set__updates_empty(self):
        m = TestModel()
        m.attributes({"k": "v"})
        m.save()
        self.assertEqual(
            {m.id_attribute: m.attributes[m.id_attribute]},
            m.target.get()
        )
        self.assertEqual(m.updates.get(), {})

        try:
            m.save()
        except Exception:
            self.fail("exception raised")

    def test_save__update(self):
        original = TestModel()
        original.attributes({"k1": "v"})
        original_id = original.save().get(original.id_attribute)

        m = TestModel()
        m.set_target(original_id)
        m.find()
        m.set("k2", "v")
        m.save()

        copy = TestModel()
        copy.set_target(original_id)
        copy.find()
        self.assertEqual(m.attributes, copy.attributes)

    def test_save__update__push_pull_iterators(self):
        m = TestModel()
        m.save()
        m.set("k1.k2.k3", "v")
        m.push_many("k", ["v", "v", "v"])
        m.save()

        copy = TestModel(m.get_target()).find()
        self.assertEqual(m.attributes, copy.attributes)

    def test_save__update__without_find(self):
        original = TestModel()
        original.set("k1", "v")
        original_id = original.save().get(original.id_attribute)

        m = TestModel()
        m.set_target(original_id)
        m.set("k2", "v")
        m.save()

        copy = TestModel(original_id)
        copy.find()

        self.assertEqual(copy.get(), {
            original.id_attribute: original_id,
            "k1": "v",
            "k2": "v"
        })

    def test_save__update__protected_post_update_hook(self):
        m = TestModel()
        m.set("k", "v")
        self.assertEqual(m.target.get(), {})
        self.assertEqual(m.original.get(), {})
        self.assertEqual(m.updates.get(), {"$set": {"k": "v"}})

        m.save()
        self.assertEqual(
            type(m.target[m.id_attribute]),
            bson.objectid.ObjectId
        )
        self.assertEqual(
            m.original.get(),
            {
                m.id_attribute: m.attributes[m.id_attribute],
                "k": "v"
            }
        )
        self.assertEqual(m.updates.get(), {})

    def test_save__update__raises_ModelNotUpdated(self):
        m = TestModel()
        m.set_target(bson.objectid.ObjectId())
        m.set("k", "v")
        m.original({"k": "v"})
        with self.assertRaises(ModelNotUpdated):
            m.save()

    def test_save__delete(self):
        m = TestModel()
        m.save()
        m.delete()
        m.save()

        copy = TestModel()
        copy.set_target(m.get_target())
        with self.assertRaises(ModelNotFound):
            copy.find()

    def test_save__delete__raises_ModelNotDeleted(self):
        m = TestModel()
        m.set("k", "v")
        m.save()
        m.delete()
        self.assertEqual(m._delete, True)

        m.save()

        copy = TestModel()
        copy.set_target(m.get_target())
        copy.delete()
        with self.assertRaises(ModelNotDeleted):
            copy.save()

    def test_save__delete__raises_ModelTargetNotSet(self):
        m = TestModel()
        m.save()
        m.target = {}
        m.delete()

        with self.assertRaises(ModelTargetNotSet):
            m.save()

    def test_save__insert__pre_insert_hook(self):
        global connection_name, collection_name

        class ModelAbstract(object):
            def pre_insert_hook(self):
                self.set("created", datetime.datetime.today())

        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name,
            "bases": ModelAbstract
        })

        m = TestModel()
        m.save()
        self.assertIn("created", m.attributes.get())
        self.assertEqual(datetime.datetime, type(m.attributes["created"]))

    def test_save__insert__post_insert_hook(self):
        global connection_name, collection_name

        class ModelAbstract(object):
            def post_insert_hook(self):
                self.set_baz()

            def set_baz(self):
                baz = "{} {}".format(self.get("foo"), self.get("bar"))
                self.set("baz", baz)

        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name,
            "bases": ModelAbstract
        })

        m = TestModel()
        m.set("foo", "Foo")
        m.set("bar", "Bar")
        m.save()
        self.assertEqual(m.get("baz"), "Foo Bar")

    def test_save__update__pre_update_hook(self):
        global connection_name, collection_name

        class ModelAbstract(object):
            def pre_update_hook(self):
                self.set("updated", datetime.datetime.today())

        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name,
            "bases": ModelAbstract
        })

        m = TestModel()
        m.save()
        self.assertNotIn("updated", m.attributes)

        m.set("k", "v")
        m.save()
        self.assertIn("updated", m.attributes)
        self.assertEqual(datetime.datetime, type(m.attributes["updated"]))

    def test_save__update__post_update_hook(self):
        global connection_name, collection_name

        class ModelAbstract(object):
            def post_update_hook(self):
                self.set_baz()

            def set_baz(self):
                baz = "{} {}".format(self.get("foo"), self.get("bar"))
                self.set("baz", baz)

        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name,
            "bases": ModelAbstract
        })

        m = TestModel()
        m.save()
        self.assertNotIn("baz", m.attributes)

        m.set("foo", "Foo")
        m.set("bar", "Bar")
        m.save()
        self.assertEqual(m.get("baz"), "Foo Bar")

    def test_save__delete__post_delete_hook(self):
        global connection_name, collection_name

        class ModelAbstract(object):
            def pre_delete_hook(self):
                m = TestModel()
                m.set_target(self.get_target())
                m.find()
                self.set("d", m.get())

        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name,
            "bases": ModelAbstract
        })

        m = TestModel()
        m.set("k", "v")
        m.save()
        self.assertNotIn("d", m.attributes)

        m.delete()
        m.save()
        self.assertIn("d", m.attributes)
        self.assertEqual(m.get("d"), {
            m.id_attribute: m.attributes[m.id_attribute],
            "k": "v"
        })

        copy = TestModel(m.attributes[m.id_attribute])
        with self.assertRaises(ModelNotFound):
            copy.find()

    def test_save__deleete__post_delete_hook(self):
        global connection_name, collection_name

        class ModelAbstract(object):
            def post_delete_hook(self):
                m = TestModel()
                m.set(m.id_attribute, self.get_id())
                m.save()

        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name,
            "bases": ModelAbstract
        })

        m = TestModel()
        m.set("k1", "v")
        m.set("k2", "v")
        m.set("k3", "v")
        m.save()
        m.delete()
        m.save()

        copy = TestModel(m.get(m.id_attribute))
        copy.find()
        self.assertEqual(copy.attributes.get(), {
            copy.id_attribute: m.get(copy.id_attribute)
        })

    # dereference_entities

    def test_dereference_entities__local_one(self):
        global connection_name, collection_name

        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name,
            "references": {
                "r": {
                    "entity": "Test",
                    "type": "local_one",
                    "foreign_key": "_id"
                }
            }
        })

        original = TestModel()
        original.set("k", "v")
        original.save()

        m = TestModel()
        m.set("k", "v")
        m.set("r", original.get_id())
        m.save()

        copy = TestModel(m.get_id()).find(projection={"r": 2})

        self.assertEqual(type(copy.attributes["r"]), TestModel)
        self.assertEqual(copy.get("r._id"), original.get("_id"))

    def test_dereference_entities__local_one__with_projection(self):
        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name,
            "references": {
                "r": {
                    "entity": "Test",
                    "type": "local_one",
                    "foreign_key": "_id"
                }
            }
        })

        original = TestModel()
        original.set("k", "v")
        original.save()

        m = TestModel()
        m.set("k", "v")
        m.set("r", original.get_id())
        m.save()

        copy = TestModel(m.get_id()).find(projection={"r": {"k": 0}})

        self.assertEqual(type(copy.attributes["r"]), TestModel)
        self.assertEqual(copy.get("r._id"), original.get("_id"))
        self.assertEqual(copy.get("r"), {"_id": original.get("_id")})

    def test_dereference_entities__local_one__delimited_string_key(self):
        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name,
            "references": {
                "r1.r2.r3": {
                    "entity": "Test",
                    "type": "local_one",
                }
            }
        })

        original = TestModel()
        original.set("k", "v")
        original.save()

        m = TestModel()
        m.set("k", "v")
        m.set("r1.r2.r3", original.get_id())
        m.save()

        copy = TestModel(m.get_id()).find(projection={"r1.r2.r3": 2})

        self.assertEqual(type(copy.attributes["r1.r2.r3"]), TestModel)
        self.assertEqual(copy.get("r1.r2.r3._id"), original.get("_id"))

    # def test_dereference_entities__many_to_one_local(self):
    #     TestModel, TestCollection = Entity("Test", {
    #         "connection": connection_name,
    #         "collection": collection_name,
    #         "references": {
    #             "r": {
    #                 "entity": "Test",
    #                 "type": "many_to_one",
    #             }
    #         }
    #     })
    #
    #     original = TestModel()
    #     original.set("k", "v")
    #     original.save()
    #
    #     m = TestModel()
    #     m.set("k", "v")
    #     m.set("r", original.get_id())
    #     m.save()
    #
    #     copy = TestModel(m.get_id()).find(projection={"r": 2})
    #
    #     self.assertEqual(type(copy.attributes["r"]), TestModel)
    #     self.assertEqual(copy.get("r._id"), original.get("_id"))

    def test_dereference_entities__foreign_one(self):
        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name,
            "references": {
                "r": {
                    "entity": "Test",
                    "type": "foreign_one",
                    "foreign_key": "r"
                }
            }
        })

        original = TestModel()
        original.set("k", "v")
        original.save()

        m = TestModel()
        m.set("k", "v")
        m.set("r", original.get_id())
        m.save()

        copy = TestModel(original.get_id()).find(projection={"r": 2})

        self.assertEqual(type(copy.attributes["r"]), TestModel)
        self.assertEqual(copy.get("r._id"), m.get("_id"))

    # def test_dereference_entities__one_to_one_foreign(self):
    #     TestModel, TestCollction = Entity("Test", {
    #         "connection": connection_name,
    #         "collection": collection_name,
    #         "references": {
    #             "r": {
    #                 "entity": "Test",
    #                 "type": "one_to_one",
    #                 "foreign_key": "r"
    #             }
    #         }
    #     })
    #
    #     original = TestModel()
    #     original.set("k", "v")
    #     original.save()
    #
    #     m = TestModel()
    #     m.set("k1", "v")
    #     m.set("k2", "v")
    #     m.set("k3", "v")
    #     m.set("r", original.get_id())
    #     m.save()
    #
    #     copy = TestModel(original.get_id()).find(projection={
    #         "r": {"k2": 1}
    #     })
    #
    #     # assert resolved relationship
    #     self.assertEqual(type(copy.attributes["r"]), TestModel)
    #     self.assertEqual(copy.get("r._id"), m.get("_id"))
    #     self.assertEqual(copy.get("r"), {
    #       "_id": m.get("_id"),
    #       "k2": "v"
    #     })
    #
    # def test_dereference_entities__many_to_one_foreign(self):
    #     TestModel, TestCollection = Entity("Test", {
    #         "connection": connection_name,
    #         "collection": collection_name,
    #         "references": {
    #             "r": {
    #                 "entity": "Test",
    #                 "type": "many_to_one",
    #                 "foreign_key": "r"
    #             }
    #         }
    #     })
    #
    #     original = TestModel()
    #     original.set("k", "v")
    #     original.save()
    #
    #     m = TestModel()
    #     m.set("k", "v")
    #     m.set("r", original.get_id())
    #     m.save()
    #
    #     copy = TestModel(original.get_id()).find(projection={"r": 2})
    #
    #     self.assertEqual(type(copy.attributes["r"]), TestModel)
    #     self.assertEqual(copy.get("r._id"), m.get("_id"))

    def test_dereference_entities__local_one__returns_DereferenceError(self):
        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name,
            "references": {
                "r": {
                    "entity": "Test",
                    "type": "local_one",
                }
            }
        })

        original = TestModel()
        original.save()

        m = TestModel()
        m.set("r", original.get_id())
        m.save()

        original.delete()
        original.save()

        copy = TestModel(m.get_id()).find(projection={"r": 2})

        self.assertEqual(
            type(copy.attributes["r"]),
            DereferenceError
        )

    def test_dereference_entities__foreign_one__returns_DereferenceError(self):
        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name,
            "references": {
                "r": {
                    "entity": "Test",
                    "type": "foreign_one",
                    "foreign_key": "r"
                }
            }
        })

        original = TestModel()
        original.save()

        m = TestModel(original.get("_id"))
        m.find(projection={"r": 2})

        self.assertEqual(m.get("r"), None)

    # reference entities

    def test_reference_entities(self):
        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name,
            "references": {
                "r": {
                    "entity": "Test",
                    "type": "local_one",
                }
            }
        })

        child = TestModel()
        child.save()

        parent = TestModel()
        parent.set("r", child)
        parent.save()

        copy = TestModel(parent.get_id()).find()

        self.assertEqual(type(copy.attributes["r"]), bson.objectid.ObjectId)
        self.assertEqual(copy.get("r"), child.get(child.id_attribute))

    def test_reference_entities__foreign_key(self):
        TestModel, TestCollection = Entity("Test", {
            "connection": connection_name,
            "collection": collection_name,
            "references": {
                "foo": {
                    "entity": "Test",
                    "type": "local_one",
                    "foreign_key": "bar"
                }
            }
        })

        child = TestModel()
        child.set("bar", "something")
        child.save()

        parent = TestModel()
        parent.set("foo", child)
        parent.save()


if __name__ == "__main__":
    unittest.main()
