
import sys; sys.path.append("../") # noqa

import unittest


from pymongo_basemodel.model import Model
from pymongo_basemodel.collection import Collection
from pymongo_basemodel.entity import Entities, Entity
from pymongo_basemodel.projection import Projection
from pymongo_basemodel.exceptions import EntityNotSet


class TestEntity(unittest.TestCase):

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
            "default_get_projection": {
                "k": 1
            }
        }, {
            "default_get_projection": {
                "k": 1
            }
        })

        self.assertEqual(m.default_get_projection.get(), {"k": 1})
        self.assertEqual(c.default_get_projection.get(), {"k": 1})
        self.assertEqual(type(m.default_get_projection), Projection)
        self.assertEqual(type(c.default_get_projection), Projection)


class TestEntities(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        Entities.cache = {}

    def test_set__entity_param(self):
        m, c = Entity("m")
        self.assertEqual(Entities.cache, {
            "m": {
                "model": m,
                "collection": c
            }
        })

    def test_get__string_param(self):
        m, c = Entity("m")
        self.assertEqual(Entities.get("m"), {
            "model": m,
            "collection": c
        })

    def test_get__string_param__raises_EntityNotSet(self):
        with self.assertRaises(EntityNotSet):
            Entities.get("foo")


if __name__ == "__main__":
    unittest.main()
