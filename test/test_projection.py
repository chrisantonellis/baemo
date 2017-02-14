
import unittest

from pymongo_basemodel.projection import Projection

from pymongo_basemodel.exceptions import ProjectionMalformed
from pymongo_basemodel.exceptions import ProjectionTypeMismatch


class TestProjection(unittest.TestCase):

    def test_init(self):
        p = Projection({"k": 0})
        self.assertEqual(p.__dict__, {"k": 0})

        # raise exception
        with self.assertRaises(ProjectionMalformed):
            Projection({"k": "foo"})

        with self.assertRaises(ProjectionTypeMismatch):
            Projection({"k": 0, "k2": 1})

    def test_call(self):
        p1 = Projection()
        p1({"k": 0})
        self.assertEqual(p1.__dict__, {"k": 0})

        # raise exception
        p2 = Projection()
        with self.assertRaises(ProjectionMalformed):
            p2({"k": "foo"})

        with self.assertRaises(ProjectionTypeMismatch):
            p2({"k1": 0, "k2": 1})

    def test_set(self):
        p1 = Projection()
        p1.set("k1", 1)
        self.assertEqual(p1.__dict__, {"k1": 1})

        p1.set("k2", 1)
        self.assertEqual(p1.__dict__, {"k1": 1, "k2": 1})

        # dot notation
        p1.set("k3.k4.k5", 1)
        self.assertEqual(p1.__dict__, {
            "k1": 1,
            "k2": 1,
            "k3": {"k4": {"k5": 1}}
        })

        # raise exception
        p2 = Projection()
        p2.set("k1", 1)
        self.assertEqual(p2.__dict__, {"k1": 1})
        with self.assertRaises(ProjectionMalformed):
            p2.set("k2", "something")

        self.assertEqual(p2.__dict__, {"k1": 1})
        with self.assertRaises(ProjectionTypeMismatch):
            p2.set("k2", 0)

        self.assertEqual(p2.__dict__, {"k1": 1})

    def test_merge(self):
        p1 = Projection({"k1": 1})
        v = p1.merge({"k2": 1})
        self.assertEqual(v, {"k1": 1, "k2": 1})

        # raise exception
        p2 = Projection({"k1": 1})
        d1 = {"k2": "foo"}
        with self.assertRaises(ProjectionMalformed):
            p2.merge(d1)

        d2 = {"k2": 0}
        with self.assertRaises(ProjectionTypeMismatch):
            p2.merge(d2)

    def test_flatten(self):
        p = Projection({"k1": 1, "k2": 2, "k3": {"k4": 1, "k5": 2}})
        self.assertEqual(p.flatten(), {"k1": 1, "k2": 1, "k3": 1})

    def test_flatten_projection(self):
        p = Projection()
        d1 = {"k1": 1, "k2": 2, "k3": {"k4": 1, "k5": 2}}
        self.assertEqual(p.flatten_projection(d1), {"k1": 1, "k2": 1, "k3": 1})

        d2 = {"k1": 0, "k2": {"k3": 0}, "k4": 2}
        self.assertEqual(p.flatten_projection(d2), {"k1": 0})

        # raise exception
        with self.assertRaises(ProjectionMalformed):
            p.flatten_projection({"k": "foo"})

        with self.assertRaises(ProjectionTypeMismatch):
            p.flatten_projection({"k1": 1, "k2": 0})

    def test_validate_projection(self):
        p = Projection()
        d1 = {"k": 1}
        self.assertEqual(p.validate_projection(d1), "inclusive")

        d2 = {"k1": 1, "k2": {"k3": 1, "k4": 2}, "k6": -1}
        self.assertEqual(p.validate_projection(d2), "inclusive")

        d3 = {"k": 0}
        self.assertEqual(p.validate_projection(d3), "exclusive")

        d4 = {"k1": 0, "k2": {"k3": 0, "k4": 2}, "k6": -1}
        self.assertEqual(p.validate_projection(d4), "exclusive")

        d5 = {"k": 2}
        self.assertEqual(p.validate_projection(d5), None)

        d6 = {"k1": 2, "k2": {"k3": 2}, "k6": -1}
        self.assertEqual(p.validate_projection(d6), None)

        d7 = {"foo": "bar"}

        with self.assertRaises(ProjectionMalformed):
            p.validate_projection(d7)

        d8 = {"k1": {"k2": {"k3": "bar"}}}
        with self.assertRaises(ProjectionMalformed):
            p.validate_projection(d8)

        # raise exception
        p = Projection()
        d1 = {"k": "foo"}
        with self.assertRaises(ProjectionMalformed):
            p.validate_projection(d1)

        d2 = {"k1": 1, "k2": 0}
        with self.assertRaises(ProjectionTypeMismatch):
            p.validate_projection(d2)

        d3 = {"k1": 1, "k2": {"k3": 2, "k4": {"k5": 0}}}
        with self.assertRaises(ProjectionTypeMismatch):
            p.validate_projection(d3)

    def test_type(self):
        p = Projection({"k": 1})
        self.assertEqual(p.type, "inclusive")

        p({"k": 0})
        self.assertEqual(p.type, "exclusive")

        p({"k": 2})
        self.assertEqual(p.type, None)

    def test_merge_projections(self):
        p = Projection()
        d1 = {"k1": 1, "k2": {"k3": 1}}
        d2 = {"k2": {"k4": 1}}
        self.assertEqual(p.merge_projections(d1, d2), {
          "k1": 1,
          "k2": {"k3": 1, "k4": 1}
        })

        # remove key with -1
        d3 = {"k1": 1, "k2": {"k3": 1}, "k5": -1}
        d4 = {"k2": {"k4": 1}, "k5": 1}
        self.assertEqual(p.merge_projections(d3, d4), {
          "k1": 1,
          "k2": {"k3": 1, "k4": 1}
        })
