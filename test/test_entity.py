
import sys; sys.path.append("../")

import unittest


from pymongo_basemodel.model import Model
from pymongo_basemodel.collection import Collection
from pymongo_basemodel.entity import Entities, Entity
from pymongo_basemodel.projection import Projection
from pymongo_basemodel.exceptions import EntityNotSet


class TestEntity(unittest.TestCase):

    # __new__

    def test___new___no_params(self):
        m, c = Entity("m")
        self.assertTrue(issubclass(m, Model))
        self.assertTrue(issubclass(c, Collection))

    def test___new___dict_params(self):
        m, c = Entity("m", {
            "foo": "bar"
        }, {
            "foo": "bar"
        })

        self.assertEqual(m.foo, "bar")
        self.assertEqual(c.foo, "bar")

    def test___new___dict_params_with_methods(self):
        class mAbstract(object):
            def test_method(self):
                pass

        class cAbstract(object):
            def test_method(self):
                pass

        m, c = Entity("m", {
            "methods": mAbstract
        }, {
            "methods": cAbstract
        })

        self.assertTrue(hasattr(m, "test_method"))
        self.assertTrue(hasattr(c, "test_method"))

    def test___new___dict_params_overwrite_existing_types(self):
        m, c = Entity("m", {
            "get_projection": {
                "k": 1
            }
        }, {
            "get_projection": {
                "k": 1
            }
        })

        self.assertEqual(m.get_projection.get(), {"k": 1})
        self.assertEqual(c.get_projection.get(), {"k": 1})
        self.assertEqual(type(m.get_projection), Projection)
        self.assertEqual(type(c.get_projection), Projection)


class TestEntities(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        Entities.cache = {}

    # __set__

    def test_set__entity_param(self):
        m, c = Entity("m")
        self.assertEqual(Entities.cache, {
            "m": {
                "model": m,
                "collection": c
            }
        })

    # __get__

    def test_get__string_param(self):
        m, c = Entity("m")
        self.assertEqual(Entities.get("m"), {
            "model": m,
            "collection": c
        })

    def test_get__string_param__raises_EntityNotSet(self):
        with self.assertRaises(EntityNotSet):
            Entities.get("foo")

    # __unnecessary__

    def test_something(self):
        self.assertTrue("something" == "something")

    def test_whatever(self):
        self.assertTrue("whatever" == "whatever")

    def test_math_is_hard(self):
        with self.assertRaises(ZeroDivisionError):
            0/0


if __name__ == "__main__":
    unittest.main()