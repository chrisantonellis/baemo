
import sys; sys.path.append("../")

import unittest

from collections import OrderedDict

from baemo.delimited import DelimitedDict
from baemo.sort import Sort
from baemo.sort import SortOperator
from baemo.references import References
from baemo.exceptions import SortMalformed


class TestSort(unittest.TestCase):

    # __init__

    def test___init___no_params(self):
        s = Sort()
        self.assertEqual(s.__dict__, OrderedDict())
        self.assertEqual(type(s), Sort)

    def test___init___OrderedDict_param(self):
        s = Sort(OrderedDict([("k", 1)]))
        self.assertEqual(s.__dict__, OrderedDict([("k", 1)]))

    def test___init___OrderedDict_param__raises_SortMalformed(self):
        with self.assertRaises(SortMalformed):
            s = Sort(OrderedDict([("k", "foo")]))

    # __call__

    def test___call___no_params(self):
        s = Sort(OrderedDict([("k", 1)]))
        self.assertEqual(s.__dict__, OrderedDict([("k", 1)]))
        s()
        self.assertEqual(s.__dict__, OrderedDict())

    def test___call___OrderedDict_param(self):
        s = Sort()
        s(OrderedDict([("k", 1)]))
        self.assertEqual(s.__dict__, OrderedDict([("k", 1)]))

    def test___call___OrdereDict_param__raises_SortMalformed(self):
        s = Sort()
        with self.assertRaises(SortMalformed):
            s(OrderedDict([("k", "foo")]))

    # set

    def test_set__string_and_int_params(self):
        s = Sort()
        s.set("k", 1)
        self.assertEqual(s.__dict__, OrderedDict([("k", 1)]))

    def test_set__string_and_string_params__raises_SortMalformed(self):
        s = Sort()
        with self.assertRaises(SortMalformed):
            s.set("k", "foo")

    def test_set__delimited_string_and_int_params(self):
        s = Sort()
        s.set("k1.k2.k3", 1)
        self.assertEqual(s.__dict__, OrderedDict([(
            "k1", OrderedDict([(
                "k2", OrderedDict([(
                    "k3", 1
                )])
            )])
        )]))

    def test_set__delimited_string_and_int_params(self):
        s = Sort()
        with self.assertRaises(SortMalformed):
            s.set("k1.k2.k3", "foo")

    # merge

    def test_merge__tuple_param(self):
        s = Sort(("k1", 1))
        v = s.merge(("k2", 1))
        self.assertEqual(v, OrderedDict([
            ("k1", 1),
            ("k2", 1)
        ]))

    def test_merge__list_param(self):
        s = Sort(("k1", 1))
        v = s.merge([("k2", 1)])
        self.assertEqual(v, OrderedDict([
            ("k1", 1),
            ("k2", 1)
        ]))

    # update

    def test_update__tuple_param(self):
        s = Sort(("k1", 1))
        s.update(("k2", 1))
        self.assertEqual(s.__dict__, OrderedDict([
            ("k1", 1),
            ("k2", 1)
        ]))

    def test_update__list_param(self):
        s = Sort(("k1", 1))
        s.update([("k2", 1)])
        self.assertEqual(s.__dict__, OrderedDict([
            ("k1", 1),
            ("k2", 1)
        ]))

    # _wrap

    def test__wrap__natural_key(self):
        s = OrderedDict([("$natural", OrderedDict([("foo", 1)]))])
        self.assertEqual(
            Sort._wrap(s),
            OrderedDict([("$natural", SortOperator([("foo", 1)]))])
        )

    def test__wrap__meta_key(self):
        s = OrderedDict([("$meta", OrderedDict([("foo", 1)]))])
        self.assertEqual(
            Sort._wrap(s),
            OrderedDict([("$meta", SortOperator([("foo", 1)]))])
        )

    # wrap

    def test_wrap__natural_key(self):
        s = Sort()
        s.__dict__ = OrderedDict([("$natural", OrderedDict([("foo", 1)]))])
        s.wrap()
        self.assertEqual(
            s.__dict__,
            OrderedDict([("$natural", SortOperator([("foo", 1)]))])
        )

    def test_wrap__meta_key(self):
        s = Sort()
        s.__dict__ = OrderedDict([("$meta", OrderedDict([("foo", 1)]))])
        s.wrap()
        self.assertEqual(
            s.__dict__,
            OrderedDict([("$meta", SortOperator([("foo", 1)]))])
        )

    # _flatten

    def test__flatten(self):
        s = Sort([("k1", 1), ("k2", 1)])
        self.assertEqual(Sort._flatten(s), [("k1", 1), ("k2", 1)])

    def test__flatten__remove_reference_sorts(self):
        s = Sort([("k1.k2.k3", 1), ("k4", 1)])
        r = DelimitedDict({"k1.k2": 1, "foo": "bar"})
        self.assertEqual(Sort._flatten(s, remove=r), [
            ("k4", 1)
        ])

    # flatten

    def test_flatten(self):
        s = Sort([("k1", 1), ("k2", 1)])
        self.assertEqual(s.flatten(), [("k1", 1), ("k2", 1)])

    def test_flatten__remove_reference_sorts(self):
        s = Sort([("k1.k2.k3", 1), ("k4", 1)])
        r = DelimitedDict({"k1.k2": 1, "foo": "bar"})
        self.assertEqual(s.flatten(remove=r), [
            ("k4", 1)
        ])

    # _validate

    def test__validate__incorrect_value__raises_SortMalformed(self):
        s = OrderedDict([("k1", 1), ("k2", "foo")])
        with self.assertRaises(SortMalformed):
            Sort._validate(s)

    def test__validate__incorrect_type__raises_SortMalformed(self):
        s = OrderedDict([("k1", 1), ("k2", ["foo", "bar", "baz"])])
        with self.assertRaises(SortMalformed):
            Sort._validate(s)

    # validate

    def test_validate__incorrect_value__raises_SortMalformed(self):
        s = Sort()
        s.__dict__ = OrderedDict([("k1", 1), ("k2", "foo")])
        with self.assertRaises(SortMalformed):
            s.validate()

    def test_validate__incorrect_type__raises_SortMalformed(self):
        s = Sort()
        s.__dict__ = OrderedDict([("k1", 1), ("k2", ["foo", "bar", "baz"])])
        with self.assertRaises(SortMalformed):
            s.validate()


if __name__ == "__main__":
    unittest.main()
