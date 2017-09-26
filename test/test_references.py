
import sys; sys.path.append("../")

import unittest

from collections import OrderedDict
from baemo.references import Reference
from baemo.references import References
from baemo.exceptions import ReferencesMalformed


class TestReferences(unittest.TestCase):

    # __init__

    def test___init___no_params(self):
        r = References()
        self.assertEqual(r.__dict__, {})
        self.assertEqual(type(r), References)

    def test___init___dict_param(self):
        r = References({
            "k": {
                "type": "one_to_one",
                "entity": "user"
            }
        })

        self.assertEqual(r.__dict__, {
            "k": Reference({
                "type": "one_to_one",
                "entity": "user"
            })
        })

    # __call__

    def test___call___no_params(self):
        r = References({
            "k": {
                "type": "one_to_one",
                "entity": "user"
            }
        })

        r()
        self.assertEqual(r.__dict__, {})

    def test___call___dict_param(self):
        r = References()
        r({
            "k": {
                "type": "one_to_one",
                "entity": "user"
            }
        })

        self.assertEqual(r.__dict__, {
            "k": Reference({
                "type": "one_to_one",
                "entity": "user"
            })
        })

    # _wrap

    def test__wrap__dict_param(self):
        r = {
            "k": {
                "type": "one_to_one",
                "entity": "user"
            }
        }

        self.assertEqual(References._wrap(r), {
            "k": Reference({
                "type": "one_to_one",
                "entity": "user"
            })
        })

    def test__wrap__nested_dict_param(self):
        r = {
            "k1": {
                "k2": {
                    "k3": {
                        "type": "one_to_one",
                        "entity": "user"
                    }
                }
            }
        }

        self.assertEqual(References._wrap(r), {
            "k1": {
                "k2": {
                    "k3": Reference({
                        "type": "one_to_one",
                        "entity": "user"
                    })
                }
            }
        })

    # wrap

    def test_wrap(self):
        r = References()
        r.__dict__ = {
            "k": {
                "type": "one_to_one",
                "entity": "user"
            }
        }

        r.wrap()
        self.assertEqual(r.__dict__, {
            "k": Reference({
                "type": "one_to_one",
                "entity": "user"
            })
        })

    # _validate

    def test__validate__dict_param(self):
        r = {
            "k": Reference({
                "type": "one_to_one",
                "entity": "user"
            }
        )}

        try:
            References._validate(r)
        except ReferencesMalformed:
            self.fail("exception raised")

    def test__validate__dict_param__raises_ReferencesMalformed(self):
        with self.assertRaises(ReferencesMalformed):
            References._validate({"foo": "bar"})

    # validate

    def test_validate__dict_param(self):
        r = References()
        r.__dict__ = {
            "k": Reference({
                "type": "one_to_one",
                "entity": "user"
            }
        )}
            
        try:
            r.validate()
        except ReferencesMalformed:
            self.fail("exception raised")

    def test_validate__dict_param__raises_ReferencesMalformed(self):
        r = References()
        r.__dict__ = {"foo": "bar"}
        with self.assertRaises(ReferencesMalformed):
            r.validate()


if __name__ == "__main__":
    unittest.main()
