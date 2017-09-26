
import sys; sys.path.append("../")

import unittest


from baemo.model import Model
from baemo.collection import Collection
from baemo.entity import Entities, Entity
from baemo.projection import Projection
from baemo.exceptions import EntityNotSet


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
            "bases": mAbstract
        }, {
            "bases": cAbstract
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


if __name__ == "__main__":
    unittest.main()
