
import unittest

from collections import OrderedDict

from pymongo_basemodel.sort import Sort
from pymongo_basemodel.dot_notation import DotNotationContainer
from pymongo_basemodel.model import Relationship
from pymongo_basemodel.exceptions import SortMalformed


class TestSort(unittest.TestCase):

    def test_call(self):
        s = Sort()
        s(OrderedDict([("k", 1)]))
        self.assertEqual(s.__dict__, OrderedDict([("k", 1)]))

        # raise exception ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        with self.assertRaises(SortMalformed):
            s = Sort()
            s(OrderedDict([("foo", "bar")]))

    def test_set(self):
        s = Sort()
        s.set("k", 1)
        self.assertEqual(s.__dict__, OrderedDict([("k", 1)]))

        # dot notation ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        s()
        s.set("k1.k2.k3", 1)
        self.assertEqual(s.__dict__, OrderedDict([
            ("k1", OrderedDict([
                ("k2", OrderedDict([
                    ("k3", 1)
                ])
            )])
        )]))


        # raise exception ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        with self.assertRaises(SortMalformed):
            s.set("foo", "bar")

        with self.assertRaises(SortMalformed):
            s.set("k1", 1)
            s.set("k1.k2", 1)
            s.set("k1.k2.k3", "bar")

    def test_merge(self):
        s1 = Sort(OrderedDict([("k1", 1)]))
        s2 = Sort(OrderedDict([("k2", 1)]))
        s1.merge(s2)
        self.assertEqual(s1.__dict__, OrderedDict([("k1", 1), ("k2", 1)]))

        s1.merge(OrderedDict([("k3", 1)]))
        self.assertEqual(s1.__dict__, OrderedDict([
            ("k1", 1),
            ("k2", 1),
            ("k3", 1)
        ]))

    def test_flatten(self):
        s = Sort()
        s.set("k1.k2.k3", 1)
        s.set("k1.k4.k5", 1)
        self.assertEqual(s.flatten(), [
            ("k1.k2.k3", 1),
            ("k1.k4.k5", 1)
        ])

        r = DotNotationContainer({
            "k1": {
                "k2": Relationship({"foo": "bar"})
            }
        })
        self.assertEqual(s.flatten(remove=r), [
            ("k1.k4.k5", 1)
        ])

    def test_validate_sort(self):
        s = Sort()
        # self.assertEqual(s.validate_sort([("k", 1)]), True)

        # raise exception ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # with self.assertRaises(SortMalformed):
        #     s.validate_sort([("foo", "bar")])

        with self.assertRaises(SortMalformed):
            s.validate_sort([("k1", 1), ("k2", OrderedDict([("foo", "bar")]))])
