
import sys; sys.path.append("../")

import unittest
import copy

from baemo.delimited import DelimitedStr
from baemo.delimited import DelimitedDict


class TestDelimitedStr(unittest.TestCase):

    # __init__

    def test___init___no_params(self):
        d = DelimitedStr()
        self.assertEqual(d.keys, [])
        self.assertIsInstance(d, DelimitedStr)

    def test___init___delimited_string_param(self):
        d = DelimitedStr("k1.k2.k3")
        self.assertEqual(d.keys, ["k1", "k2", "k3"])

    def test___init___delimited_string_and_delimiter_params(self):
        d = DelimitedStr("k1*k2*k3", delimiter="*")
        self.assertEqual(d.keys, ["k1", "k2", "k3"])

    # __call__

    def test___call___no_params(self):
        d = DelimitedStr("k1.k2.k3")
        self.assertEqual(d.keys, ["k1", "k2", "k3"])
        d()
        self.assertEqual(d.keys, [])

    def test___call___delimited_string_param(self):
        d = DelimitedStr()
        self.assertEqual(d.keys, [])
        d("k1.k2.k3")
        self.assertEqual(d.keys, ["k1", "k2", "k3"])

    # __eq__

    def test___eq____returns_True(self):
        d1 = DelimitedStr("k1.k2.k3")
        d2 = DelimitedStr("k1.k2.k3")
        self.assertTrue(d1 == d2)

    def test___eq____same_class__returns_False(self):
        d1 = DelimitedStr("foo.bar")
        d2 = DelimitedStr("bar.foo")
        self.assertFalse(d1 == d2)

    def test___eq____different_class__returns_False(self):
        d1 = DelimitedStr("foo.bar")
        d2 = object()
        self.assertFalse(d1 == d2)

    # __ne__

    def test___ne____returns_True(self):
        d1 = DelimitedStr("foo.bar")
        d2 = DelimitedStr("bar.foo")
        self.assertTrue(d1 != d2)

    def test___ne____returns_False(self):
        d1 = DelimitedStr("k1.k2.k3")
        d2 = DelimitedStr("k1.k2.k3")
        self.assertFalse(d1 != d2)

    # __hash__

    def test___hash__(self):
        h1 = hash(DelimitedStr("k1.k2.k3"))
        h2 = hash(DelimitedStr("k1.k2.k3"))
        self.assertEqual(type(h1), int)
        self.assertEqual(type(h2), int)
        self.assertEqual(h1, h2)

    # __len__

    def test___len__(self):
        d2 = DelimitedStr("k1.k2.k3")
        self.assertEqual(len(d2), 3)

    # __bool__

    def test___bool____returns_False(self):
        d1 = DelimitedStr()
        self.assertFalse(bool(d1))

    def test___bool____returns_True(self):
        d1 = DelimitedStr("k1.k2.k3")
        self.assertTrue(bool(d1))

    # __str__

    def test___str__(self):
        d = DelimitedStr("k1.k2.k3")
        self.assertEqual(str(d), "k1.k2.k3")

    # __iter__

    def test___iter__(self):
        d = DelimitedStr("a.a.a")
        for i in d:
            self.assertEqual(i, "a")

    # __reversed__

    def test___reversed__(self):
        d = DelimitedStr("k1.k2.k3")
        self.assertEqual(list(reversed(d)), ["k3", "k2", "k1"])

    # __contains__

    def test___contains__(self):
        d = DelimitedStr("k1.k2.k3")
        self.assertTrue("k1" in d)
        self.assertTrue("k2" in d)
        self.assertTrue("k3" in d)
        self.assertFalse("foo" in d)

    # __getitem__

    def test___getitem__int_index(self):
        d = DelimitedStr("k1.k2.k3")
        self.assertEqual(d[1], "k2")

    def test___getitem__slice_index(self):
        d = DelimitedStr("k1.k2.k3")
        self.assertEqual(d[:-1], "k1.k2")

    # __setitem__

    def test___setitem__int_index(self):
        d = DelimitedStr("k1.k2.k3")
        d[1] = "foo"
        self.assertEqual(d.keys, ["k1", "foo", "k3"])

    def test___setitem__slice_index(self):
        d = DelimitedStr("k1.k2.k3")
        d[:-1] = ["foo", "bar"]
        self.assertEqual(d.keys, ["foo", "bar", "k3"])

    # __delitem__

    def test___delitem__int_index(self):
        d = DelimitedStr("k1.k2.k3")
        del d[1]
        self.assertEqual(d.keys, ["k1", "k3"])

    def test___delitem__slice_index(self):
        d = DelimitedStr("k1.k2.k3")
        del d[:-1]
        self.assertEqual(d.keys, ["k3"])


class TestDelimitedDict(unittest.TestCase):

    # __init__

    def test___init____no_params(self):
        d = DelimitedDict()
        self.assertEqual(d.__dict__, {})
        self.assertIsInstance(d, DelimitedDict)

    def test___init____dict_param(self):
        d = DelimitedDict({"k1.k2.k3": "v"})
        self.assertEqual(d.__dict__, {
            "k1": {
                "k2": {
                    "k3": "v"
                }
            }
        })

    # __call__

    def test___call____no_params(self):
        d = DelimitedDict({"k1.k2.k3": "v"})
        d()
        self.assertEqual(d.__dict__, {})

    def test___call____dict_param(self):
        d = DelimitedDict()
        d({"k1.k2.k3": "v"})
        self.assertEqual(d.__dict__, {
            "k1": {
                "k2": {
                    "k3": "v"
                }
            }
        })

    def test___call____delimited_dict_param(self):
        d = DelimitedDict()
        d(DelimitedDict({"k1.k2.k3": "v"}))
        self.assertEqual(d.__dict__, {
            "k1": {
                "k2": {
                    "k3": "v"
                }
            }
        })

    def test___call____raises_TypeError(self):
        d = DelimitedDict()
        with self.assertRaises(TypeError):
            d(1)

    # __bool__

    def test___bool____empty_dict__returns_False(self):
        self.assertFalse(bool(DelimitedDict()))

    def test___bool___non_empty_dict__returns_True(self):
        self.assertTrue(bool(DelimitedDict({"k1.k2.k3": "v"})))

    # __str__

    def test___str__(self):
        d = DelimitedDict({"k1.k2.k3": "v"})
        self.assertEqual(str(d), "{'k1': {'k2': {'k3': 'v'}}}")

    # __eq__

    def test___eq____returns_True(self):
        d1 = DelimitedDict({"k1.k2.k3": "v"})
        d2 = DelimitedDict({"k1.k2.k3": "v"})
        self.assertTrue(d1 == d2)

    def test___eq____same_class__returns_False(self):
        d1 = DelimitedDict({"foo.bar": "baz"})
        d2 = DelimitedDict({"bar.baz": "foo"})
        self.assertFalse(d1 == d2)

    def test___eq____different_class__returns_False(self):
        d1 = DelimitedDict({"foo.bar": "baz"})
        d2 = object()
        self.assertFalse(d1 == d2)

    # __ne__

    def test___ne____returns_True(self):
        d1 = DelimitedDict({"foo.bar": "baz"})
        d2 = DelimitedDict({"bar.baz": "foo"})
        self.assertTrue(d1 != d2)

    def test___ne____returns_False(self):
        d1 = DelimitedDict({"k1.k2.k3": "v"})
        d2 = DelimitedDict({"k1.k2.k3": "v"})
        self.assertFalse(d1 != d2)

    # __hash__

    def test___hash__(self):
        h1 = hash(DelimitedDict({"k1.k2.k3": "v"}))
        h2 = hash(DelimitedDict({"k1.k2.k3": "v"}))
        self.assertTrue(h1 == h2)

    # __iter__

    def test___iter__(self):
        d = DelimitedDict({"a.a.a": "v"})
        for k in d:
            self.assertEqual(k, "a")

    # __contains__

    def test___contains__(self):
        d = DelimitedDict({"k1.k2.k3": "v"})
        self.assertTrue("k1" in d)

    # __getitem__

    def test___getitem__string_param__returns_value(self):
        d = DelimitedDict({"k1.k2.k3": "v"})
        self.assertEqual(d["k1"], {
            "k2": {
                "k3": "v"
            }
        })

    def test___getitem__delimited_string_param__returns_value(self):
        d = DelimitedDict({"k1.k2.k3": "v"})
        self.assertEqual(d["k1.k2.k3"], "v")

    # __setitem__

    def test___setitem__string_param__sets_value(self):
        d = DelimitedDict({"k1.k2.k3": "v"})
        d["k1"] = "foo"
        self.assertEqual(d.__dict__, {"k1": "foo"})

    def test___setitem__delimited_string_param__sets_value(self):
        d = DelimitedDict({"k1.k2.k3": "v"})
        d["k1.k2.k3"] = "foo"
        self.assertEqual(d.__dict__, {
            "k1": {
                "k2": {
                    "k3": "foo"
                }
            }
        })

    # __delitem__

    def test___delitem__string_param__deletes_value(self):
        d = DelimitedDict({"k1.k2.k3": "v"})
        del d["k1"]
        self.assertEqual(d.__dict__, {})

    def test___delitem__delimited_string_param__deletes_value(self):
        d = DelimitedDict({"k1.k2.k3": "v"})
        del d["k1.k2"]
        self.assertEqual(d.__dict__, {"k1": {}})

    # __len__

    def test___len__(self):
        d = DelimitedDict({
            "k": "v",
            "j": "v",
            "l": "v"
        })
        self.assertEqual(len(d), 3)

    # __copy__

    def test___copy__(self):
        d1 = DelimitedDict({"k1.k2.k3": "v"})
        d2 = copy.copy(d1)
        self.assertIsNot(d1, d2)
        self.assertEqual(d1, d2)
        d1.set("k1.k2", "bar")
        self.assertEqual(d1, d2)

    # __deepcopy__

    def test___deepcopy__(self):
        d1 = DelimitedDict({"k1.k2.k3": "v"})
        d2 = copy.deepcopy(d1)
        self.assertIsNot(d1, d2)
        self.assertEqual(d1, d2)
        d1.set("k1.k2", "bar")
        self.assertNotEqual(d1, d2)

    # __items__

    def test___items___for_item__yields_tuple(self):
        d = DelimitedDict({
            "k": "v",
            "k": "v",
            "k": "v"
        })
        for item in d.items():
            self.assertEqual(item, ("k", "v"))

    def test___items___for_k_v__yields_k_v_pair(self):
        d = DelimitedDict({
            "k": "v",
            "k": "v",
            "k": "v"
        })
        for k, v in d.items():
            self.assertEqual(k, "k")
            self.assertEqual(v, "v")

    # __keys__

    def test___keys___yields_keys(self):
        d = DelimitedDict({
            "k": "v",
            "k": "v",
            "k": "v"
        })
        for k in d.keys():
            self.assertEqual(k, "k")

    # __values__

    def test___values___yields_values(self):
        d = DelimitedDict({
            "k": "v",
            "k": "v",
            "k": "v"
        })
        for v in d.values():
            self.assertEqual(v, "v")

    # ref

    def test_ref__no_params__returns_all_values(self):
        d = DelimitedDict({"k": "v"})
        v = d.ref()
        self.assertEqual(v, {"k": "v"})
        v["k"] = "foo"
        self.assertEqual(d.__dict__, v)

    def test_ref__string_param__returns_value(self):
        d = DelimitedDict({"k": "v"})
        self.assertEqual(d.ref("k"), "v")

    def test_ref__string_param__raises_KeyError(self):
        d = DelimitedDict()
        with self.assertRaises(KeyError):
            d.ref("k")

    def test_ref__string_param__raises_ValueError(self):
        d = DelimitedDict({"k1.k2": "v"})
        with self.assertRaises(TypeError):
            d.ref("k1.k2.k3")

    def test_ref__delimited_string_param__returns_value(self):
        d = DelimitedDict({"k1.k2.k3": "v"})
        self.assertEqual(d.ref("k1.k2"), {"k3": "v"})

    def test_ref__True_create_param_key_missing__creates_missing_containers(self):
        d = DelimitedDict()
        d.ref("k", create=True)
        self.assertEqual(d.__dict__, {"k": {}})

    def test_ref__True_create_param_wrong_type__creates_missing_containers(self):
        d = DelimitedDict({"k": 1})
        d.ref("k", create=True)
        self.assertEqual(d.__dict__, {"k": {}})

    def test_ref__True_create_param_nested_wrong_type__creates_missing_containers(self):
        d = DelimitedDict({"k1": 1})
        d.ref("k1.k2.k3", create=True)
        self.assertEqual(d.__dict__, {
            "k1": {
                "k2": {
                    "k3": {}
                }
            }})

    # get

    def test_get__no_params__returns_all_values(self):
        d = DelimitedDict({"k": "v"})
        v = d.get()
        self.assertEqual(v, {"k": "v"})
        v["k"] = "foo"
        self.assertNotEqual(d.__dict__, v)

    def test_get__string_param__returns_value(self):
        d = DelimitedDict({"k": "v"})
        self.assertEqual(d.get("k"), "v")

    def test_get__string_param_missing_key__returns_default_value(self):
        d = DelimitedDict()
        self.assertEqual(d.get("k", "foo"), "foo")

    def test_get__string_param_wrong_type__returns_default_value(self):
        d = DelimitedDict({"k1.k2": 1})
        self.assertEqual(d.get("k1.k2.k3", "foo"), "foo")

    def test_get__string_param__raises_KeyError(self):
        d = DelimitedDict()
        with self.assertRaises(KeyError):
            d.get("k")

    def test_get__string_param__raises_ValueError(self):
        d = DelimitedDict({"k1.k2": "v"})
        with self.assertRaises(TypeError):
            d.get("k1.k2.k3")

    def test_get__delimited_string_param__returns_value(self):
        d = DelimitedDict({"k1.k2.k3": "v"})
        self.assertEqual(d.get("k1.k2"), {"k3": "v"})

    # has

    def test_has__no_params__returns_True(self):
        self.assertTrue(DelimitedDict({"k": "v"}).has())

    def test_has__no_params__returns_False(self):
        self.assertFalse(DelimitedDict().has())

    def test_has__string_param__returns_True(self):
        d = DelimitedDict({"k1.k2.k3": "v"})
        self.assertTrue(d.has("k1"))

    def test_has__string_param__returns_False(self):
        d = DelimitedDict({"k1.k2.k3": "v"})
        self.assertFalse(d.has("foo"))

    def test_has__delimited_string_param__returns_True(self):
        d = DelimitedDict({"k1.k2.k3": "v"})
        self.assertTrue(d.has("k1.k2.k3"))

    def test_has__delimited_string_param__returns_False(self):
        d = DelimitedDict({"k1.k2.k3": "v"})
        self.assertFalse(d.has("k1.k2.foo"))

    # spawn

    def test_spawn(self):
        d1 = DelimitedDict({"k1.k2.k3": "v"})
        d2 = d1.spawn()
        self.assertEqual(d1, d2)
        d1["k1"] = "foo"
        self.assertEqual(d1, d2)

    # clone

    def test_clone(self):
        d1 = DelimitedDict({"k1.k2.k3": "v"})
        d2 = d1.clone()
        self.assertEqual(d1, d2)
        d1["k1"] = "foo"
        self.assertNotEqual(d1, d2)

    # set

    def test_set__string_key_param(self):
        d = DelimitedDict()
        d.set("k", "v")
        self.assertEqual(d.__dict__, {"k": "v"})

    def test_set__delimited_string_key_param(self):
        d = DelimitedDict()
        d.set("k1.k2.k3", "v")
        self.assertEqual(d.__dict__, {
            "k1": {
                "k2": {
                    "k3": "v"
                }
            }
        })

    def test_set__create_False_missing_delimited_key__raises_KeyError(self):
        d = DelimitedDict({"k1.k2": "v"})
        with self.assertRaises(KeyError):
            d.set("k1.k2.k3", "v", create=False)

    def test_set__create_False_missing_key__raises_KeyError2(self):
        d = DelimitedDict()
        with self.assertRaises(KeyError):
            d.set("k", "v", create=False)

    # push

    def test_push__string_key_param(self):
        d = DelimitedDict({"k": []})
        d.push("k", "v")
        self.assertEqual(d.__dict__, {"k": ["v"]})

    def test_push__string_key_param__convert_existing_value(self):
        d = DelimitedDict({"k": "v"})
        d.push("k", "v")
        self.assertEqual(d.__dict__, {"k": ["v", "v"]})

    def test_push__delimited_string_key_param(self):
        d = DelimitedDict({"k1.k2.k3": []})
        d.push("k1.k2.k3", "v")
        self.assertEqual(d.__dict__, {
            "k1": {
                "k2": {
                    "k3": ["v"]
                }
            }
        })

    def test_push__True_create_param__creates_list(self):
        d = DelimitedDict()
        d.push("k", "v")
        self.assertEqual(d.__dict__, {"k": ["v"]})

    def test_push__create_False__raises_KeyError(self):
        d = DelimitedDict()
        with self.assertRaises(KeyError):
            d.push("k", "v", create=False)

    def test_psuh__create_False__raises_TypeError(self):
        d = DelimitedDict({"k": "v"})
        with self.assertRaises(TypeError):
            d.push("k", "v", create=False)

    # pull

    def test_pull__string_key_param(self):
        d = DelimitedDict({"k": ["v"]})
        d.pull("k", "v")
        self.assertEqual(d.__dict__, {"k": []})

    def test_pull__cleanup_True__removes_empty_containers(self):
        d = DelimitedDict({"k": ["v"]})
        d.pull("k", "v", cleanup=True)
        self.assertEqual(d.__dict__, {})

    def test_pull__delimited_string_key_param(self):
        d = DelimitedDict({"k1.k2.k3": ["v"]})
        d.pull("k1.k2.k3", "v")
        self.assertEqual(d.__dict__, {
            "k1": {
                "k2": {
                    "k3": []
                }
            }
        })

    def test_pull__string_key_param__raises_KeyError(self):
        d = DelimitedDict()
        with self.assertRaises(KeyError):
            d.pull("k", "v")

    def test_pull__string_key_param__raises_ValueError(self):
        d = DelimitedDict({"k": []})
        with self.assertRaises(ValueError):
            d.pull("k", "v")

    def test_pull__string_key_param__raises_TypeError(self):
        d = DelimitedDict({"k": "v"})
        with self.assertRaises(TypeError):
            d.pull("k", "v")

    # unset

    def test_unset__string_key_param(self):
        d = DelimitedDict({"k": "v"})
        d.unset("k")
        self.assertEqual(d.__dict__, {})

    def test_unset__cleanup_True__removes_empty_containers(self):
        d = DelimitedDict({"k1.k2.k3": "v"})
        d.unset("k1.k2.k3", cleanup=True)
        self.assertEqual(d.__dict__, {})

    def test_unset__delimited_key_param(self):
        d = DelimitedDict({"k1.k2.k3": "v"})
        d.unset("k1.k2.k3")
        self.assertEqual(d.__dict__, {
            "k1": {
                "k2": {}
            }
        })

    def test_usnet__string_key_param__raises_KeyError(self):
        d = DelimitedDict({"k": "v"})
        with self.assertRaises(KeyError):
            d.unset("foo")

    # _merge

    def test__merge__dict_params(self):
        d1 = {"k1": "v"}
        d2 = {"k2": "v"}
        d = DelimitedDict._merge(d1, d2)
        self.assertEqual(type(d), dict)
        self.assertEqual(d, {
            "k1": "v",
            "k2": "v"
        })

    def test__merge__nested_dict_params(self):
        d1 = {"foo": "v", "bar": {"baz": "v"}}
        d2 = {"bar": {"qux": "v"}}
        d = DelimitedDict._merge(d1, d2)
        self.assertEqual(type(d), dict)
        self.assertEqual(d, {
            "foo": "v",
            "bar": {
                "baz": "v",
                "qux": "v"
            }
        })

    def test__merge__DelimitedDict_params(self):
        d1 = DelimitedDict({"k1": "v"})
        d2 = DelimitedDict({"k2": "v"})
        d = DelimitedDict._merge(d1, d2)
        self.assertEqual(type(d), DelimitedDict)
        self.assertEqual(d, DelimitedDict({
            "k1": "v",
            "k2": "v"
        }))

    # merge

    def test_merge__dict_param(self):
        d = DelimitedDict({"k1": "v"})
        m = d.merge({"k2": "v"})
        self.assertEqual(m, {
            "k1": "v",
            "k2": "v"
        })

    def test_merge__DelimitedDict_param(self):
        d = DelimitedDict({"k1": "v"})
        m = d.merge(DelimitedDict({"k2": "v"}))
        self.assertEqual(m, {
            "k1": "v",
            "k2": "v"
        })

    # update

    def test_update__dict_param(self):
        d = DelimitedDict({"k1": "v"})
        d.update({"k2": "v"})
        self.assertEqual(d.__dict__, {
            "k1": "v",
            "k2": "v"
        })

    def test_update__DelimitedDict_param(self):
        d = DelimitedDict({"k1": "v"})
        d.update(DelimitedDict({"k2": "v"}))
        self.assertEqual(d.__dict__, {
            "k1": "v",
            "k2": "v"
        })

    # _collapse_delimited_notation

    def test__collapse_delimited_notation(self):
        d = {
            "k1": {
                "k2": {
                    "k3": "v"
                }
            }
        }
        c = DelimitedDict._collapse_delimited_notation(d)
        self.assertEqual(type(c), type(d))
        self.assertEqual(c, {"k1.k2.k3": "v"})

    def test__collapse_delimited_notation__empty_dict(self):
        d = {
            "k1": {
                "k2": {
                    "k3": {}
                }
            }
        }
        c = DelimitedDict._collapse_delimited_notation(d)
        self.assertEqual(type(c), type(d))
        self.assertEqual(c, {"k1.k2.k3": {}})

    # collapse

    def test_collapse(self):
        d = DelimitedDict({
            "k1": {
                "k2": {
                    "k3": "v"
                }
            }
        })
        self.assertEqual(d.collapse(), {"k1.k2.k3": "v"})

    # _expand_delimited_notatoin

    def test__expand_delimited_notation(self):
        d = {"k1.k2.k3": "v"}
        e = DelimitedDict._expand_delimited_notation(d)
        self.assertEqual(type(e), type(d))
        self.assertEqual(e, {
            "k1": {
                "k2": {
                    "k3": "v"
                }
            }
        })

    def test__expand_delimited_notation__overlapping_delimited_string(self):
        d = {
            "k1.k2.k3": "v",
            "k1.k2.k4": "v"
        }
        e = DelimitedDict._expand_delimited_notation(d)
        self.assertEqual(type(e), type(d))
        self.assertEqual(e, {
            "k1": {
                "k2": {
                    "k3": "v",
                    "k4": "v"
                }
            }
        })

    # _format_keyerror

    def test__format_keyerror__string_key(self):
        needle = "k"
        key = DelimitedStr("k")
        self.assertEqual(
            DelimitedDict._format_keyerror(needle, key),
            "k"
        )

    def test__format_keyerror__delimited_string_key(self):
        needle = "k2"
        key = DelimitedStr("k1.k2.k3")
        self.assertEqual(
            DelimitedDict._format_keyerror(needle, key),
            "k2 in k1.k2.k3"
        )

    # _format_typeerror

    def test__format_typeerror__string_key(self):
        type_ = "v"
        needle = "k"
        key = DelimitedStr("k")
        self.assertEqual(
            DelimitedDict._format_typeerror(type_, needle, key),
            "Expected dict, found str for k"
        )

    def test__format_typeerror__delimited_string_key(self):
        type_ = ["v"]
        needle = "k2"
        key = DelimitedStr("k1.k2.k3")
        self.assertEqual(
            DelimitedDict._format_typeerror(type_, needle, key),
            "Expected dict, found list for k2 in k1.k2.k3"
        )

    # _format_valueerror

    def test__format_valueerror__string_key(self):
        needle = "k"
        key = DelimitedStr("k")
        value = "v"
        self.assertEqual(
            DelimitedDict._format_valueerror(needle, key, value),
            "v not in list for k"
        )

    def test__format_valueerror__delimited_string_key(self):
        needle = "k2"
        key = DelimitedStr("k1.k2.k3")
        value = "v"
        self.assertEqual(
            DelimitedDict._format_valueerror(needle, key, value),
            "v not in list for k2 in k1.k2.k3"
        )


if __name__ == "__main__":
    unittest.main()
