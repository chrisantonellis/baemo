
import unittest

from pymongo_basemodel.sort import Sort

from pymongo_basemodel.exceptions import SortMalformed


class TestSort(unittest.TestCase):

    def test_init(self):
        s = Sort({"k": 1})
        self.assertEqual(s.__dict__, {"k": 1})

        # raise exception ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        with self.assertRaises(SortMalformed):
            s = Sort({"foo": "bar"})

    def test_call(self):
        s = Sort()
        s({"k": 1})
        self.assertEqual(s.__dict__, {"k": 1})

        # raise exception ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        with self.assertRaises(SortMalformed):
            s = Sort()
            s({"foo": "bar"})

    def test_set(self):
        s = Sort()
        s.set("k", 1)
        self.assertEqual(s.__dict__, {"k": 1})

        # dot notation ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        s()
        s.set("k1.k2.k3", 1)
        self.assertEqual(s.__dict__, {"k1": {"k2": {"k3": 1}}})

        # raise exception ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        with self.assertRaises(SortMalformed):
            s.set("foo", "bar")

        with self.assertRaises(SortMalformed):
            s.set("k1", 1)
            s.set("k1.k2", 1)
            s.set("k1.k2.k3", "bar")

    def test_merge(self):
        s1 = Sort({"k1": 1})
        s2 = Sort({"k2": 1})
        s2.merge(s1)
        self.assertEqual(s2.__dict__, {"k1": 1, "k2": 1})

        s2.merge({"k3": 1})
        self.assertEqual(s2.__dict__, {"k1": 1, "k2": 1, "k3": 1})

    def test_validate(self):
        s = Sort()
        s.__dict__ = {"k": 1}
        s.validate()

        s()
        s.__dict__ = {"foo": "bar"}
        with self.assertRaises(SortMalformed):
            s.validate()

    def test_validate_sort(self):
        s = Sort()
        self.assertEqual(s.validate_sort({"k": 1}), True)
        with self.assertRaises(SortMalformed):
            s.validate_sort({"foo": "bar"})