
import sys; sys.path.append("../")

import unittest

from baemo.projection import Projection
from baemo.exceptions import ProjectionMalformed
from baemo.exceptions import ProjectionTypeMismatch


class TestProjection(unittest.TestCase):

    # __init__

    def test_init__no_params(self):
        p = Projection()
        self.assertEqual(p.__dict__, {})
        self.assertEqual(type(p), Projection)

    def test_init__dict_param(self):
        p = Projection({"k": 0})
        self.assertEqual(p.__dict__, {"k": 0})

    # __call__

    def test_call__dict_param(self):
        p = Projection()
        p({"k": 0})
        self.assertEqual(p.__dict__, {"k": 0})

    # set

    def test_set__non_delimited_key_param(self):
        p = Projection()
        p.set("k1", 1)
        self.assertEqual(p.__dict__, {"k1": 1})

        p.set("k2", 1)
        self.assertEqual(p.__dict__, {"k1": 1, "k2": 1})

    def test_set__delimited_key_param(self):
        p = Projection()
        p.set("k1.k2.k3", 1)
        self.assertEqual(p.__dict__, {
            "k1": {
                "k2": {
                    "k3": 1
                }
            }
        })

    # _merge

    def test__merge__simple_projection_params(self):
        p1 = Projection({"k1": 1})
        p2 = Projection({"k2": 1})
        self.assertEqual(Projection._merge(p1, p2), Projection({
            "k1": 1,
            "k2": 1
        }))

    def test__merge__advanced_projection_params(self):
        p1 = Projection({"k1": 1, "k2": 2, "k3": {"k4": 1}})
        p2 = Projection({"k5": 1, "k6": 2, "k3": {"k8": 1}})
        self.assertEqual(Projection._merge(p1, p2), Projection({
            "k1": 1,
            "k2": 2,
            "k3": {
                "k4": 1,
                "k8": 1
            },
            "k5": 1,
            "k6": 2
        }))

    def test__merge__projection_param__delete_key(self):
        p1 = Projection({"k2": -1})
        p2 = Projection({"k1": 1, "k2": 2, "k3": 1})
        self.assertEqual(Projection._merge(p1, p2), Projection({
            "k1": 1,
            "k3": 1
        }))

    # merge

    def test_merge__dict_param(self):
        p = Projection({"k1": 1})
        d = {"k2": 1}
        self.assertEqual(p.merge(d), Projection({
            "k1": 1,
            "k2": 1
        }))

    def test_merge__projection_param(self):
        p1 = Projection({"k1": 1})
        p2 = Projection({"k2": 1})
        self.assertEqual(p1.merge(p2), Projection({
            "k1": 1,
            "k2": 1
        }))

    def test_merge__projection_param__raises_ProjectionTypeMismatch(self):
        p1 = Projection({"k1": 1})
        p2 = Projection({"k2": 0})
        with self.assertRaises(ProjectionTypeMismatch):
            p1.merge(p2)

    # update

    def test_update(self):
        p1 = Projection({"k1": 1})
        p2 = Projection({"k2": 1})
        p1.update(p2)
        self.assertEqual(p1.__dict__, {
            "k1": 1,
            "k2": 1
        })

    # _flatten

    def test__flatten__projection_param__returns_dict(self):
        p = Projection({"k1": 1, "k2": 2, "k3": {"k4": 1, "k5": 2}})
        flattened = Projection._flatten(p)
        self.assertEqual(flattened, {"k1": 1, "k2": 1, "k3": 1})
        self.assertEqual(type(flattened), dict)

    # flatten

    def test_flatten__inclusive_projection(self):
        p = Projection({
            "k1": 1,
            "k2": 2,
            "k3": {
                "k4": 1,
                "k5": 2
            }
        })
        self.assertEqual(p.flatten(), {"k1": 1, "k2": 1, "k3": 1})

    def test_flatten__exclusive_projection(self):
        p = Projection({
            "k1": 0,
            "k2": 2,
            "k3": {
                "k4": 0,
                "k5": 2
            }
        })
        self.assertEqual(p.flatten(), {"k1": 0})

    def test_flatten__none_projection(self):
        p = Projection({
            "k1": 2,
            "k2": {
                "k3": 2
            }
        })

        self.assertEqual(p.flatten(), {})

    # _validate

    def test__validate__projection_param__return_value_discarded(self):
        try:
            Projection._validate(Projection({"k": 1}))
        except (ProjectionMalformed, ProjectionTypeMismatch):
            self.fail("exception raised")

    def test__validate__basic_inclusive_projection_param__returns_type(self):
        d = {"k": 1}
        self.assertEqual(Projection._validate(Projection(d)), "inclusive")

    def test__validate__advanced_inclusive_projection_param__returns_type(self):
        d = {
            "k1": 1,
            "k2": -1,
            "k3": 2,
            "k4": {
                "k5": 1,
                "k6": 2
            }
        }

        self.assertEqual(Projection._validate(Projection(d)), "inclusive")

    def test__validate__basic_exclusive_projection_param__returns_type(self):
        d = {"k": 0}
        self.assertEqual(Projection._validate(Projection(d)), "exclusive")

    def test__validate__advanced_exclusive_projection_param__returns_type(self):
        d = {
            "k1": 0,
            "k2": -1,
            "k3": 2,
            "k4": {
                "k5": 0,
                "k6": 2
            }
        }

        self.assertEqual(Projection._validate(Projection(d)), "exclusive")

    def test__validate__basic_none_projection_param__returns_type(self):
        d = {"k": 2}
        self.assertEqual(Projection._validate(Projection(d)), None)

    def test__validate__advanced_none_projection_param__returns_type(self):
        d = {
            "k1": 2,
            "k2": -1,
            "k3": 2,
            "k4": {
                "k5": -1,
                "k6": 2
            }
        }

        self.assertEqual(Projection._validate(Projection(d)), None)

    def test__validate__simple_projection_param__raises_ProjectionMalformed(self):
        with self.assertRaises(ProjectionMalformed):
            Projection({"k": "foo"})

    def test__validate__advanced_projection_param__raises_ProjectionMalformed(self):
        with self.assertRaises(ProjectionMalformed):
            Projection({
                "k1": 1,
                "k2": 2,
                "k3": {
                    "k4": "foo"
                }
            })

    def test__validate__simple_projection_param__raises_ProjectionTypeMismatch(self):
        with self.assertRaises(ProjectionTypeMismatch):
            Projection({
                "k": 0,
                "k2": 1
            })

    def test__validate__advanced_projection_param__raises_ProjectionTypeMismatch(self):
        with self.assertRaises(ProjectionTypeMismatch):
            Projection({
                "k1": 1,
                "k2": 2,
                "k3": {
                    "k4": 0
                }
            })

    # validate

    def test_validate__discard_return_value(self):
        try:
            Projection({"k": 0})
        except (ProjectionMalformed, ProjectionTypeMismatch):
            self.fail("exception raised")




if __name__ == "__main__":
    unittest.main()
