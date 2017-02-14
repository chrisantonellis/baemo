
import unittest
import copy


from pymongo_basemodel.dot_notation import DotNotationString
from pymongo_basemodel.dot_notation import DotNotationContainer


class TestDotNotationString(unittest.TestCase):

    def test_init(self):
        dns1 = DotNotationString()
        self.assertIsInstance(dns1, DotNotationString)

        dns2 = DotNotationString("k")
        self.assertEqual(dns2.keys, ["k"])

        dns3 = DotNotationString(delimiter="*")
        self.assertEqual(dns3.delimiter, "*")
        dns3("k1*k2*k3")
        self.assertEqual(dns3.keys, ["k1", "k2", "k3"])

    def test_call(self):
        dns = DotNotationString()
        self.assertEqual(dns.keys, [])
        dns("k")
        self.assertEqual(dns.keys, ["k"])

    def test_eq(self):
        dns1 = DotNotationString()
        dns1("k1.k2.k3")
        dns2 = DotNotationString()
        dns2("k1.k2.k3")
        self.assertEqual(True, dns1 == dns2)
        dns3 = DotNotationString()
        dns3("k")
        self.assertEqual(False, dns1 == dns3)
        self.assertEqual(dns1 == str(""), False)

    def test_ne(self):
        dns1 = DotNotationString()
        dns1("k1.k2.k3")
        dns2 = DotNotationString()
        dns2("k4.k5.k6")
        self.assertEqual(True, dns1 != dns2)

    def test_hash(self):
        hash1 = hash(DotNotationString("k1.k2.k3"))
        hash2 = hash(DotNotationString("k1.k2.k3"))
        self.assertEqual(True, hash1 == hash2)

    def test_len(self):
        dns = DotNotationString()
        dns("k")
        self.assertEqual(len(dns), 1)
        dns("k1.k2.k3")
        self.assertEqual(len(dns), 3)

    def test_bool(self):
        dns = DotNotationString()
        self.assertEqual(bool(dns), False)
        dns("k")
        self.assertEqual(bool(dns), True)

    def test_repr(self):
        dns = DotNotationString("k1.k2.k3")
        self.assertEqual(str(dns), "k1.k2.k3")

    def test_iter(self):
        dns = DotNotationString("k.k.k")
        self.assertEqual(len(dns.keys), 3)
        for item in dns:
            self.assertEqual(item, "k")

    def test_reversed(self):
        dns = DotNotationString("k1.k2.k3")
        self.assertEqual(list(reversed(dns)), ["k3", "k2", "k1"])

    def test_contains(self):
        dns = DotNotationString("k1.k2.k3")
        self.assertIn("k1", dns)
        self.assertIn("k2", dns)
        self.assertIn("k3", dns)
        self.assertNotIn("key4", dns)

    def test_getitem(self):
        dns = DotNotationString()
        dns("k1.k2.k3")
        self.assertEqual(dns.keys, ["k1", "k2", "k3"])
        self.assertEqual(dns[0], "k1")
        self.assertEqual(dns[-1], "k3")
        self.assertEqual(dns[:-1], "k1.k2")

    def test_setitem(self):
        dns = DotNotationString("k1.k2.k3")
        dns[1] = "foo"
        self.assertEqual(str(dns), "k1.foo.k3")

    def test_delitem(self):
        dns = DotNotationString("k1.k2.k3")
        del dns[1]
        self.assertEqual(str(dns), "k1.k3")


class TestDotNotationContainer(unittest.TestCase):

    def test_init(self):
        dnc = DotNotationContainer()
        self.assertIsInstance(dnc, DotNotationContainer)
        dnc = DotNotationContainer({"k": "v"})
        self.assertEqual(dnc.__dict__, {"k": "v"})

        # raise exception ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        with self.assertRaises(TypeError):
            dnc = DotNotationContainer(1)

    def test_call(self):
        dnc = DotNotationContainer()
        self.assertEqual(dnc.__dict__, {})
        dnc({"k": "v"})
        self.assertEqual(dnc.__dict__, {"k": "v"})

    def test_bool(self):
        dnc1 = DotNotationContainer()
        self.assertEqual(bool(dnc1), False)
        dnc2 = DotNotationContainer({"k": "v"})
        self.assertEqual(bool(dnc2), True)

    def test_eq(self):
        dnc1 = DotNotationContainer()
        dnc1({"k": "v"})
        dnc2 = DotNotationContainer()
        dnc2({"k": "v"})
        self.assertEqual(dnc1, dnc2)
        self.assertEqual(bool(dnc1 == dnc2), True)
        dnc3 = DotNotationContainer()
        dnc3({"k": "foo"})
        self.assertNotEqual(dnc1, dnc3)
        self.assertEqual(dnc1 == dnc3, False)
        self.assertEqual(dnc1 == str(""), False)

    def test_ne(self):
        dnc1 = DotNotationContainer()
        dnc1({"k1.k2.k3": "v"})
        dnc2 = DotNotationContainer()
        dnc2({"k4.k5.k6": "v"})
        self.assertEqual(True, dnc1 != dnc2)

    def test_hash(self):
        hash1 = hash(DotNotationContainer({"k1.k2.k3": "v"}))
        hash2 = hash(DotNotationContainer({"k1.k2.k3": "v"}))
        self.assertEqual(True, hash1 == hash2)

    def test_iter(self):
        dnc = DotNotationContainer({"k1": "v", "k2": "v", "k3": "v"})
        for item in dnc:
            self.assertEqual(type(item), tuple)
        for key, val in dnc:
            self.assertEqual(type(key), str)
            self.assertEqual(type(val), str)
            self.assertEqual(val, "v")

    def test_contains(self):
        dnc = DotNotationContainer({"k": "v"})
        self.assertEqual("k" in dnc, True)
        self.assertEqual("j" in dnc, False)

    def test_getitem(self):
        dnc = DotNotationContainer()
        self.assertEqual(dnc.__dict__, {})

        dnc({"k1": {"k2": {"k3": "v"}}})

        self.assertEqual(dnc.__dict__, {"k1": {"k2": {"k3": "v"}}})

        self.assertEqual(dnc["k1.k2.k3"], "v")
        self.assertEqual(dnc["k1"]["k2"]["k3"], "v")
        self.assertEqual(dnc["k1.k2"]["k3"], "v")
        self.assertEqual(dnc["k1"]["k2.k3"], "v")

    def test_setitem(self):
        dnc = DotNotationContainer()
        dnc["k"] = "v"
        self.assertEqual(dnc.__dict__, {"k": "v"})
        dnc.clear()
        dnc["k1.k2.k3"] = "v"
        self.assertEqual(dnc.__dict__, {"k1": {"k2": {"k3": "v"}}})

    def test_copy(self):
        dnc1 = DotNotationContainer()
        dnc1({"k1": "v", "k2": {"k3": "v"}})
        dnc2 = copy.copy(dnc1)
        self.assertIsNot(dnc1, dnc2)
        self.assertEqual(dnc1, dnc2)
        dnc1.set("k2.k3", "v")
        self.assertEqual(dnc1, dnc2)

    def test_deepcopy(self):
        dnc1 = DotNotationContainer()
        dnc1({"k1": "v", "k2": {"k3": "v"}})
        dnc2 = copy.deepcopy(dnc1)
        self.assertIsNot(dnc1, dnc2)
        self.assertEqual(dnc1, dnc2)
        dnc1.set("k2.k3", "foo")
        self.assertNotEqual(dnc1, dnc2)

    def test_items(self):
        dnc = DotNotationContainer({"k1": "v", "k2": "v", "k3": "v"})
        for item in dnc.items():
            self.assertEqual(type(item), tuple)
        for key, val in dnc.items():
            self.assertEqual(type(key), str)
            self.assertEqual(type(val), str)
            self.assertEqual(val, "v")

    def test_keys(self):
        dnc = DotNotationContainer({"k": "v"})
        for key in dnc.keys():
            self.assertEqual(key, "k")
            self.assertEqual(type(key), str)

    def test_values(self):
        dnc = DotNotationContainer({"k": "v"})
        for val in dnc.values():
            self.assertEqual(val, "v")
            self.assertEqual(type(val), str)

    def test_clear(self):
        dnc = DotNotationContainer({"k1": "v", "k2": "v", "k3": "v"})
        self.assertEqual(dnc.__dict__, {"k1": "v", "k2": "v", "k3": "v"})
        dnc.clear()
        self.assertEqual(dnc.__dict__, {})

    def test_ref(self):
        dnc1 = DotNotationContainer()
        dnc1.set("k", "v")
        v = dnc1.ref("k")
        self.assertIs(dnc1.ref("k"), v)

        # dot notation
        dnc2 = DotNotationContainer()
        dnc2.set("k1.k2.k3", "v")
        v = dnc2.ref("k1.k2.k3")
        self.assertIs(dnc2.ref("k1.k2.k3"), v)

        # create
        dnc3 = DotNotationContainer()
        dnc3.ref("k1", create=True)
        self.assertEqual(dnc3.__dict__, {"k1": {}})

        dnc3({"k1": "v"})
        self.assertEqual(dnc3.__dict__, {"k1": "v"})

        dnc3.ref("k1.k2", create=True)
        self.assertEqual(dnc3.__dict__, {"k1": {"k2": {}}})

        dnc3({"k1": {"k2": "v"}})
        dnc3.ref("k1.k2", create=True)
        self.assertEqual(dnc3.__dict__, {"k1": {"k2": {}}})

        # raise keyerror
        dnc4 = DotNotationContainer()
        with self.assertRaises(KeyError):
            dnc4.ref("k")

        # raise valueerror
        dnc5 = DotNotationContainer()
        dnc5({"k1": "v"})
        with self.assertRaises(TypeError):
            dnc5.ref("k1.k2")

    def test_get(self):
        dnc1 = DotNotationContainer()
        dnc1.set("k", "v")
        self.assertEqual(dnc1.get("k"), "v")

        # get all
        dnc2 = DotNotationContainer()
        dnc2.set("k", "v")
        self.assertEqual(dnc2.get(), {"k": "v"})

        # dot notation
        dnc3 = DotNotationContainer()
        dnc3.set("k1", {"k2": {"k3": "v"}})
        self.assertEqual(dnc3.get("k1.k2.k3"), "v")

        # keyerror
        dnc4 = DotNotationContainer()
        with self.assertRaises(KeyError):
            dnc4.get("k2")

    def test_has(self):
        dnc1 = DotNotationContainer()
        dnc1.set("k", "v")
        self.assertEqual(dnc1.has("k"), True)
        self.assertEqual(dnc1.has("foo"), False)

        # dot notation
        dnc2 = DotNotationContainer()
        dnc2.set("k1.k2", "v")
        self.assertEqual(dnc2.has("k1.k2"), True)
        self.assertEqual(dnc2.has("k1.foo"), False)

    def test_spawn(self):
        dnc1 = DotNotationContainer()
        dnc1.set("k", "v")
        self.assertEqual(dnc1.__dict__, {"k": "v"})
        dnc2 = dnc1.spawn()
        self.assertEqual(dnc2.__dict__, {"k": "v"})
        self.assertIs(dnc1.__dict__, dnc2.__dict__)

        # nested
        dnc3 = DotNotationContainer()
        dnc3.set("k1.k2.k3", "v")
        self.assertEqual(dnc3.__dict__, {"k1": {"k2": {"k3": "v"}}})
        dnc4 = dnc3.spawn("k1.k2")
        self.assertEqual(dnc4.__dict__, {"k3": "v"})
        self.assertIs(dnc3.ref("k1.k2"), dnc4.__dict__)

    def test_clone(self):
        dnc1 = DotNotationContainer()
        dnc1.set("k", "v")
        self.assertEqual(dnc1.__dict__, {"k": "v"})
        dnc2 = dnc1.clone()
        self.assertEqual(dnc2.__dict__, {"k": "v"})
        self.assertIsNot(dnc1.__dict__, dnc2.__dict__)

        # nested
        dnc3 = DotNotationContainer()
        dnc3.set("k1.k2.k3", "v")
        self.assertEqual(dnc3.__dict__, {"k1": {"k2": {"k3": "v"}}})
        dnc4 = dnc3.clone("k1.k2")
        self.assertEqual(dnc4.__dict__, {"k3": "v"})
        self.assertIsNot(dnc3.ref("k1.k2"), dnc4.__dict__)

    def test_set(self):
        dnc1 = DotNotationContainer()
        self.assertEqual(dnc1.__dict__, {})
        dnc1.set("k", "v")
        self.assertEqual(dnc1.__dict__, {"k": "v"})

        # dot notation key
        dnc = DotNotationContainer()
        self.assertEqual(dnc.__dict__, {})
        dnc.set("k1.k2", "v")
        self.assertEqual(dnc.__dict__, {"k1": {"k2": "v"}})

        # create=false, keyerror
        dnc = DotNotationContainer()
        with self.assertRaises(KeyError):
            dnc.set("k", "v", create=False)

    def test_push(self):
        dnc1 = DotNotationContainer()
        self.assertEqual(dnc1.__dict__, {})
        dnc1.push("k", "v1")
        self.assertEqual(dnc1.__dict__, {"k": ["v1"]})
        dnc1.push("k", "v2")
        self.assertEqual(dnc1.__dict__, {"k": ["v1", "v2"]})

        # convert value
        dnc2 = DotNotationContainer()
        self.assertEqual(dnc2.__dict__, {})
        dnc2.set("k", "v1")
        self.assertEqual(dnc2.__dict__, {"k": "v1"})
        dnc2.push("k", "v2")
        self.assertEqual(dnc2.__dict__, {"k": ["v1", "v2"]})

        dnc3 = DotNotationContainer()
        self.assertEqual(dnc3.__dict__, {})
        dnc3.set("k", {"inner_k1": "v"})
        self.assertEqual(dnc3.__dict__, {"k": {"inner_k1": "v"}})

        dnc3.push("k", {"inner_k2": "v"})
        self.assertEqual(dnc3.__dict__, {
            "k": [
                {"inner_k1": "v"},
                {"inner_k2": "v"}
            ]
        })

        # dot notation key
        dnc4 = DotNotationContainer()
        self.assertEqual(dnc4.__dict__, {})
        dnc4.push("k1.k2", "v1")
        self.assertEqual(dnc4.__dict__, {"k1": {"k2": ["v1"]}})

        dnc4.push("k1.k2", "v2")

        self.assertEqual(dnc4.__dict__, {"k1": {"k2": ["v1", "v2"]}})

        # create=False, raise keyerror
        dnc5 = DotNotationContainer()
        with self.assertRaises(KeyError):
            dnc5.push("k", "v1", create=False)

        # raise typeerror
        dnc = DotNotationContainer()
        dnc.set("k", "v")
        self.assertEqual(dnc.__dict__, {"k": "v"})
        with self.assertRaises(TypeError):
            dnc.push("k", "v1", create=False)

    def test_pull(self):
        dnc1 = DotNotationContainer()
        self.assertEqual(dnc1.__dict__, {})
        dnc1.set("k", ["v1", "v2"])
        self.assertEqual(dnc1.__dict__, {"k": ["v1", "v2"]})
        dnc1.pull("k", "v2")
        self.assertEqual(dnc1.__dict__, {"k": ["v1"]})

        # raise valueerror
        dnc2 = DotNotationContainer()
        self.assertEqual(dnc2.__dict__, {})
        dnc2.set("k", ["v1"])
        self.assertEqual(dnc2.__dict__, {"k": ["v1"]})
        with self.assertRaises(ValueError):
            dnc2.pull("k", "v2")

        # raise typeerror
        dnc3 = DotNotationContainer()
        self.assertEqual(dnc3.__dict__, {})
        dnc3.set("k", "v")
        self.assertEqual(dnc3.__dict__, {"k": "v"})
        with self.assertRaises(TypeError):
            dnc3.pull("k", "v1")

        # dot notation
        dnc4 = DotNotationContainer()
        self.assertEqual(dnc4.__dict__, {})
        dnc4.set("k1", {"k2": ["v1", "v2"]})
        self.assertEqual(dnc4.__dict__, {"k1": {"k2": ["v1", "v2"]}})
        dnc4.pull("k1.k2", "v2")
        self.assertEqual(dnc4.__dict__, {"k1": {"k2": ["v1"]}})

        # dot notation raise keyerror
        dnc5 = DotNotationContainer()
        self.assertEqual(dnc5.__dict__, {})
        dnc5.set("k1", {"k2": ["v1", "v2"]})
        self.assertEqual(dnc5.__dict__, {"k1": {"k2": ["v1", "v2"]}})
        with self.assertRaises(KeyError):
            dnc5.pull("k1.k3", "v1")
        with self.assertRaises(KeyError):
            dnc5.pull("k1.k3.key7", "v1")

        # cleanup=True
        dnc = DotNotationContainer()
        self.assertEqual(dnc.__dict__, {})
        dnc.set("k", ["v"])
        self.assertEqual(dnc.__dict__, {
            "k": ["v"]
        })
        dnc.pull("k", "v", cleanup=True)
        self.assertEqual(dnc.__dict__, {})

    def test_unset(self):
        dnc1 = DotNotationContainer()
        self.assertEqual(dnc1.__dict__, {})
        dnc1.set("k", "v")
        self.assertEqual(dnc1.__dict__, {"k": "v"})
        dnc1.unset("k")
        self.assertEqual(dnc1.__dict__, {})

        # raise keyerror
        dnc2 = DotNotationContainer()
        self.assertEqual(dnc2.__dict__, {})
        dnc2.set("k", "v")
        self.assertEqual(dnc2.__dict__, {"k": "v"})
        with self.assertRaises(KeyError):
            dnc2.unset("k1")
        with self.assertRaises(KeyError):
            dnc2.unset("k.k2")

        # dot notation
        dnc3 = DotNotationContainer()
        self.assertEqual(dnc3.__dict__, {})
        dnc3.set("k1.k2", "v")
        self.assertEqual(dnc3.__dict__, {"k1": {"k2": "v"}})
        dnc3.unset("k1.k2")
        self.assertEqual(dnc3.__dict__, {"k1": {}})

        # cleanup=True
        dnc4 = DotNotationContainer()
        dnc4.set("k1.k2.k3", "v")
        dnc4.set("k1.k4", "v")
        self.assertEqual(dnc4.__dict__, {"k1": {"k2": {"k3": "v"}, "k4": "v"}})
        dnc4.unset("k1.k2.k3", cleanup=True)
        self.assertEqual(dnc4.__dict__, {"k1": {"k4": "v"}})

    def test_merge(self):
        dnc = DotNotationContainer()
        dnc.set("k1", "v")
        self.assertEqual(dnc.__dict__, {"k1": "v"})
        value1 = dnc.merge({"k2": "v"})
        self.assertEqual(value1, {"k1": "v", "k2": "v"})
        value2 = dnc.merge({"k1": "foo"})
        self.assertEqual(value2, {"k1": "foo", "k2": "v"})

    def test_update(self):
        dnc = DotNotationContainer()
        dnc.set("k1", "v")
        self.assertEqual(dnc.__dict__, {"k1": "v"})
        value1 = dnc.update({"k2": "v"})
        self.assertEqual(value1, {"k1": "v", "k2": "v"})
        self.assertEqual(dnc.__dict__, {"k1": "v", "k2": "v"})
        dnc.update({"k1": "foo"})
        self.assertEqual(dnc.__dict__, {"k1": "foo", "k2": "v"})

    def test_collapse(self):
        dnc = DotNotationContainer()
        dnc.set("k1.k2.k3", "v")
        dnc.set("k1.k3.k4", "v")
        dnc.set("k1.k2.k5", "v")
        self.assertEqual(dnc.__dict__, {
            "k1": {
                "k2": {"k3": "v", "k5": "v"},
                "k3": {"k4": "v"}
            }
        })

        self.assertEqual(dnc.collapse(), {
          "k1.k2.k5": "v",
          "k1.k3.k4": "v",
          "k1.k2.k3": "v"
        })

    def test_format_keyerror(self):
        dnc = DotNotationContainer()
        needle = "k"
        key = DotNotationString("k")
        self.assertEqual(dnc.format_keyerror(needle, key), "k")
        needle = "k2"
        key = "k1.k2.k3"
        self.assertEqual(
            dnc.format_keyerror(needle, key),
            "k2 in k1.k2.k3"
        )

    def test_format_typeerror(self):
        dnc = DotNotationContainer()
        type_ = "string"
        needle = "k"
        key = DotNotationString("k")
        self.assertEqual(
            dnc.format_typeerror(type_, needle, key),
            "Expected dict, found str for k")

        type_ = ["list"]
        needle = "k2"
        key = DotNotationString("k1.k2.k3")
        self.assertEqual(
            dnc.format_typeerror(type_, needle, key),
            "Expected dict, found list for k2 in k1.k2.k3"
        )

    def test_format_valueerror(self):
        dnc = DotNotationContainer()
        dns1 = DotNotationString("k")
        self.assertEqual(
            dnc.format_valueerror("k", dns1, "v"),
            "v not in list for k"
        )

        dns2 = DotNotationString("k1.k2.k3")
        self.assertEqual(
            dnc.format_valueerror("k2", dns2, "v"),
            "v not in list for k2 in k1.k2.k3"
        )

    def test_merge_containers(self):
        dnc = DotNotationContainer()

        data1 = {"k1": "v", "k2": {"k3": "v", "k4": "v"}}
        data2 = {"k2": {"k3": "foo", "k5": "v"}, "k3": "v"}

        self.assertEqual(dnc.merge_containers(data1, data2), {
            "k1": "v",
            "k2": {
                "k3": "v",
                "k4": "v", "k5": "v"
            },
            "k3": "v"
        })

    def test_expand_dot_notation(self):
        dnc = DotNotationContainer()
        d1 = {"k1.k2.k3": "v"}
        self.assertEqual(dnc.expand_dot_notation(d1), {
          "k1": {
            "k2": {"k3": "v"}
            }
        })

        d2 = {
          "k1.k2.k3": "v",
          "k1.k2.k4": "v",
          "k1.k2.k5": "v",
          "k1.k8.k9": "v"
        }
        self.assertEqual(dnc.expand_dot_notation(d2), {
          "k1": {
            "k2": {"k3": "v", "k4": "v", "k5": "v"},
            "k8": {"k9": "v"}
          }
        })

    def test_collapse_dot_notation(self):
        dnc = DotNotationContainer()
        data = {"k1": {"k2": {"k3": "v"}}}
        self.assertEqual(dnc.collapse_dot_notation(data), {"k1.k2.k3": "v"})
