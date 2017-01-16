
import bson
import copy
import pymongo

from .exceptions import ModelNotFound
from .exceptions import ModelNotUpdated
from .exceptions import ModelNotDeleted
from .exceptions import ModelTargetNotSet
from .exceptions import CollectionModelClassMismatch
from .exceptions import CollectionModelNotPresent
from .exceptions import RelationshipResolutionError
from .exceptions import ProjectionMalformed
from .exceptions import ProjectionTypeMismatch


__name__ = "core"
__all__ = [
    "Model",
    "Collection"
]


class NestedDict(dict):
    """ NestedDict is a dict wrapper used to identify dicts set in nested data
    """


class Undefined(object):
    def __str__(self):
        return "undefined"

    def __bool__(self):
        return False


class DotNotationString(object):

    def __init__(self, string=None):
        self.raw = ""
        self.keys = [""]
        if string is not None:
            self.__call__(string)

    def __call__(self, string):
        self.raw = string
        self.keys = string.split(".")

    def __len__(self):
        return len(self.keys)

    def __repr__(self):
        return self.raw

    def __iter__(self):
        for key in self.keys:
            yield key

    def __getitem__(self, item):
        value = self.keys[item]

        if type(value) is list:
            value = ".".join(value)

        return value


class DotNotationContainer(object):

    def __init__(self, data=None, expand=True):
        if data:
            self.__call__(data, expand=expand)
        super().__init__()

    def __call__(self, data, expand=True):
        if expand:
            data = self.expand_dot_notation(data)
        self.__dict__ = data
        return self

    def __bool__(self):
        return bool(self.__dict__)

    def __eq__(self, value):
        return self.__dict__ == value

    def __repr__(self):
        return str(self.__dict__)

    def __iter__(self):
        for key, val in self.__dict__.items():
            yield (key, val)

    def __contains__(self, key):
        return self.has(key)

    def __getitem__(self, item):
        item = self.ref(item)
        if type(item) is dict:
            return self.__class__(item, expand=False)
        else:
            return item

    def __setitem__(self, key, value):
        self.set(key, value)
        return True

    def __copy__(self):
        new = type(self)()
        new.__dict__.update(self.__dict__)
        return new

    def __deepcopy__(self, memo):
        new = type(self)()
        new.__dict__.update(copy.deepcopy(self.__dict__))
        return new

    def items(self):
        for key, val in self.__dict__.items():
            yield (key, val)

    def keys(self):
        for key in self.__dict__.keys():
            yield key

    def values(self):
        for value in self.__dict__.values():
            yield value

    def clear(self):
        self.__dict__.clear()

    def ref(self, key=None, create=False):

        haystack = self.__dict__

        if type(key) is not DotNotationString:
            key = DotNotationString(key)

        for i, needle in enumerate(key, 1):

            if needle:

                if needle not in haystack:
                    if create:
                        haystack[needle] = {}

                    else:
                        message = self.format_keyerror(needle, key)
                        raise KeyError(message)

                if i < len(key) and type(haystack[needle]) is not dict:
                    if create:
                        haystack[needle] = {}

                    else:
                        message = self.format_typeerror(needle, key,
                                                        haystack[needle])
                        raise TypeError(message)

                if create and type(haystack[needle]) is not dict:
                    haystack[needle] = {}

                haystack = haystack[needle]

        return haystack

    def get(self, key=None):
        return copy.deepcopy(self.ref(key))

    def has(self, key=None):
        try:
            self.ref(key)
            return True
        except:
            return False

    def spawn(self, key=None):
        return self.__class__(self.ref(key), expand=False)

    def clone(self, key=None):
        return self.__class__(self.get(key), expand=False)

    def set(self, key, value, create=True):

        if type(key) is not DotNotationString:
            key = DotNotationString(key)

        haystack = self.ref(key[:-1], create)
        needle = key[-1]

        if needle not in haystack:
            if create:
                pass
            else:
                raise KeyError(self.format_keyerror(needle, key))

        haystack[needle] = value
        return True

    def push(self, key, value, create=True):

        if type(key) is not DotNotationString:
            key = DotNotationString(key)

        haystack = self.ref(key[:-1], create)
        needle = key[-1]

        if needle not in haystack:
            if create:
                haystack[needle] = []
            else:
                raise KeyError(self.format_keyerror(needle, key))

        if type(haystack[needle]) is not list:
            if create:
                haystack[needle] = [haystack[needle]]
            else:
                message = self.format_typeerror(haystack[needle], needle, key)
                raise TypeError(message)

        haystack[needle].append(value)
        return True

    def pull(self, key, value, cleanup=False):

        if type(key) is not DotNotationString:
            key = DotNotationString(key)

        haystack = self.ref(key[:-1])
        needle = key[-1]

        if needle not in haystack:
            message = self.format_keyerror(needle, key)
            raise KeyError(message)

        elif type(haystack[needle]) is not list:
            message = self.format_typeerror(haystack[needle], needle, key)
            raise TypeError(message)

        elif value not in haystack[needle]:
            message = self.format_valueerror(value, needle, key)
            raise ValueError(message)

        haystack[needle].remove(value)

        if cleanup:
            if haystack[needle] == []:
                del haystack[needle]

        return True

    def unset(self, key, cleanup=False):

        if type(key) is not DotNotationString:
            key = DotNotationString(key)

        haystack = self.ref(key[:-1])
        needle = key[-1]

        if needle not in haystack:
            raise KeyError(self.format_keyerror(needle, key))

        del haystack[needle]

        if cleanup:
            for i, needle in enumerate(key, 1):
                if i < len(key):
                    cleanup_key = key[:(len(key) - i)]
                    if self.has(cleanup_key) and self.get(cleanup_key) == {}:
                        self.unset(cleanup_key)
                    else:
                        break

        return True

    def merge(self, data):
        data = self.expand_dot_notation(data)
        return self.merge_dicts(data, self.__dict__)

    def update(self, data):
        self.__dict__ = self.merge(data)
        return self.__dict__

    def collapse(self):
        return self.collapse_dot_notation(self.__dict__)

    @classmethod
    def format_keyerror(cls, needle, key):
        return "{} in {}".format(needle, key) if len(key) > 1 else needle

    @classmethod
    def format_typeerror(cls, type_, needle, key):
        message = "Expected dict, found {} for {}"
        keyerror = cls.format_keyerror(needle, key)
        return message.format(type(type_).__name__, keyerror)

    @classmethod
    def format_valueerror(cls, needle, key, value):
        message = "{} not in list for {}"
        keyerror = cls.format_keyerror(needle, key)
        return message.format(value, keyerror)

    @classmethod
    def merge_dicts(cls, dict_1, dict_2):
        for key, val in dict_1.items():
            if isinstance(dict_1[key], dict) and \
                    key in dict_2 and isinstance(dict_2[key], dict):
                dict_2[key] = cls.merge_dicts(dict_1[key], dict_2[key])
            else:
                dict_2[key] = copy.deepcopy(dict_1[key])
        return dict_2

    @classmethod
    def expand_dot_notation(cls, data):
        ex = {}
        for key, val in data.items():

            if type(val) is dict:
                ex_val = cls.expand_dot_notation(val)
            else:
                ex_val = val

            if "." in key:
                key = DotNotationString(key)
                ex_key = {}
                for i, k in enumerate(reversed(key.keys)):
                    if i == 0:
                        ex_key = {k: ex_val}
                    elif i == (len(key) - 1):
                        if k not in ex:
                            ex[k] = ex_key
                        else:
                            ex[k] = cls.merge_dicts(ex[k], ex_key)
                    else:
                        ex_key = {k: copy.copy(ex_key)}
            else:
                ex[key] = ex_val

        return ex

    @classmethod
    def collapse_dot_notation(cls, data, parent_key=None):
        items = []
        for key, val in data.items():
            new_key = "{}.{}".format(parent_key, key) if parent_key else key
            if type(val) is dict:
                items.extend(cls.collapse_dot_notation(val, new_key).items())
            else:
                items.append((new_key, val))
        return dict(items)


class Projection(DotNotationContainer):

    def __init__(self, data=None, expand=True):
        if data:
            self.__call__(data, expand)
        super().__init__()

    def __call__(self, data, expand=True):
        if expand:
            data = self.expand_dot_notation(data)
        self.get_projection_type(data)
        self.__dict__ = data

    def get(self, key=None):
        try:
            return super().get(key)
        except:
            return Undefined()

    def set(self, key, value):
        try:
            cache = copy.deepcopy(self.__dict__)
            super().set(key, value)
            self.get_type()
            return True
        except:
            self(cache)
            raise

    def merge(self, projection):
        if type(projection) is not Projection:
            projection = Projection(data=projection)

        self_type = self.get_type()
        projection_type = projection.get_type()

        if self_type and projection_type and self_type != projection_type:
            raise ProjectionTypeMismatch

        return self.merge_projections(projection.__dict__, self.__dict__)

    def update(self, projection):
        self.__dict__ = self.merge(projection)
        return self.__dict__

    def get_type(self):
        return self.get_projection_type(self.__dict__)

    def flatten(self):
        return self.flatten_projection(self.__dict__)

    @classmethod
    def get_projection_type(cls, p, parent_type=None):

        # check for invalid values
        for k, v in p.items():
            if v not in [-1, 0, 1, 2] and type(v) not in [dict, Projection]:
                raise ProjectionMalformed(k, v)

        # checking for -1, 1, 2, dict, Projection
        if any(v == 1 for v in p.values()) and \
                all(v in [-1, 1, 2] or
                    type(v) in [dict, Projection] for v in p.values()):
            local_type = "inclusive"

        # checking for -1, 0, 2, dict, Projection
        elif any(v == 0 for v in p.values()) and \
                all(v in [-1, 0, 2] or
                    type(v) in [dict, Projection] for v in p.values()):
            local_type = "exclusive"

        # checking for -1, 2, dict, Projection
        elif all(v in [-1, 2] or
                 type(v) in [dict, Projection] for v in p.values()):
            local_type = None

        # values are valid but types are mixed
        else:
            raise ProjectionTypeMismatch

        # check type recursively
        for value in p.values():
            if type(value) is dict:

                child_type = cls.get_projection_type(value, parent_type)

                if child_type and local_type and child_type != local_type:
                    raise ProjectionTypeMismatch

                if child_type and not local_type:
                    local_type = child_type

        return local_type

    @classmethod
    def flatten_projection(cls, projection):

        # 0 = exclude
        # 1 = include
        # 2 = resolve relationship
        # Projection = resolve relationship and pass projection forward
        projection_type = Projection.get_projection_type(projection)
        projection = copy.copy(projection)
        flattened = copy.copy(projection)

        # inclusive
        # 2 ----------> 1
        # Projection -> 1
        if projection_type == "inclusive":
            for key, val in projection.items():
                if val == 2 or type(val) in [dict, Projection]:
                    flattened[key] = 1

        # exclusive, None
        # 2 ----------> [ remove ]
        # Projection -> [ remove ]
        elif projection_type in ["exclusive", None]:
            for key, val in projection.items():
                if val == 2 or type(val) in [dict, Projection]:
                    del flattened[key]

        return flattened

    @classmethod
    def merge_projections(cls, p1, p2):
        for key, val in p1.items():
            if val == -1:
                del p2[key]
            elif isinstance(p1[key], dict) and \
                    key in p2 and isinstance(p2[key], dict):
                p2[key] = cls.merge_projections(p1[key], p2[key])
            else:
                p2[key] = p1[key]
        return p2


class Model(object):
    id_attribute = "_id"
    pymongo_collection = None

    def __init__(self, target=None, default=True):
        self.attributes = DotNotationContainer()
        self.updates = DotNotationContainer()
        self.original = DotNotationContainer()
        self.target = DotNotationContainer()
        self.relationships = DotNotationContainer()
        self.default_attributes = DotNotationContainer()
        self.computed_attributes = DotNotationContainer()
        self.default_find_projection = Projection()
        self.default_get_projection = Projection()
        self._delete = False

        if target:
            self.set_target(target)

        super().__init__()

    def __copy__(self):
        new = type(self)()
        new.__dict__.update(self.__dict__)
        return new

    def __deepcopy__(self, memo):
        new = type(self)()
        new.__dict__.update(copy.deepcopy(self.__dict__))
        return new

    def set_default_attributes(self):
        # default attributes get generated on get and save
        # they will not overwrite existing values
        for key, val in self.default_attributes.collapse().items():
            if not self.attributes.has(key):
                if callable(val):
                    self.set(key, val())
                else:
                    self.set(key, val)

    def set_computed_attributes(self):
        # computed attributes get generated on get and do not get saved
        # they will not overwrite existing values
        for key, val in self.computed_attributes.collapse().items():
            try:
                if not self.attributes.has(key):
                    if callable(val):
                        self.set(key, val())
                    else:
                        self.set(key, val)
            except:
                pass

    # target

    def set_target(self, target):
        if type(target) is dict:
            self.target(target)
        else:
            self.target({self.id_attribute: target})
        return self

    def get_target(self):
        if self.target:
            return self.target.get()
        else:
            return None

    def get_id(self):
        if self.target.has(self.id_attribute):
            return self.target.get(self.id_attribute)
        else:
            return None

    # recall attributes

    def find(self, projection=None, default=True):

        # check if target is set
        if not self.target:
            raise ModelTargetNotSet

        # pre find hook
        if "pre_find_hook" in dir(self):
            self.pre_find_hook()

        # setup projection
        if projection and type(projection) is not Projection:
            projection = Projection(projection)

            if self.default_find_projection and default:
                projection.merge(self.default_find_projection)

        elif not projection and self.default_find_projection and default:
            projection = self.default_find_projection

        if projection:
            flattened_projection = projection.flatten()

        # find
        if not projection or not flattened_projection:
            m = self.pymongo_collection.find_one(
                filter=self.target.get()
            )
        else:
            m = self.pymongo_collection.find_one(
                filter=self.target.get(),
                projection=flattened_projection
            )

        if m is None:
            raise ModelNotFound(data=self.target.get())

        # post find hook
        self._post_find_hook(m)

        if "post_find_hook" in dir(self):
            self.post_find_hook()

        # dereference nested models
        if self.relationships and projection:
            self.dereference_nested_models(projection=projection)

        return self

    def dereference_nested_models(self, projection):

        for r_target in self.relationships.keys():

            # extract relationship properties
            r_type = self.relationships[r_target]["type"]
            r_model = self.relationships[r_target]["model"]

            if "local_key" in self.relationships[r_target]:
                r_local_key = self.relationships[r_target]["local_key"]
            else:
                r_local_key = r_target

            if "foreign_key" in self.relationships[r_target]:
                r_foreign_key = self.relationships[r_target]["foreign_key"]
            else:
                if isinstance(r_model(), Model):
                    r_foreign_key = r_model.id_attribute
                else:
                    r_foreign_key = r_model.model.id_attribute

            # resolve this relationship?
            if r_target in projection and \
                    (type(projection.get(r_target) is dict or
                     projection.get(r_target) == 2)):

                # check r_target for dot notation syntax and if found
                # tunnel down through r_target and self.attributes

                # internal relationship
                if r_target in self.attributes and self.attributes[r_target]:

                    # one to one : local, many_to_one : local
                    if r_type in ["one_to_one", "many_to_one"]:

                        try:

                            # projection
                            if type(projection.get(r_target)) is dict:
                                self.attributes[r_target] = r_model({
                                    r_foreign_key: self.attributes[r_local_key]
                                }).find(projection=projection.get(r_target))

                            # no projection
                            else:
                                self.attributes[r_target] = r_model({
                                    r_foreign_key: self.attributes[r_local_key]
                                }).find()

                        # relationship resolution error
                        except:
                            error = RelationshipResolutionError(data={
                                "model": r_model.__name__,
                                "target": self.attributes[r_local_key]
                            })
                            self.attributes[r_target] = error

                    # one to many : local, many to many : local
                    elif r_type in ["one_to_many", "many_to_many"]:

                        # projection
                        if type(projection.get(r_target)) is dict:

                            collection = r_model().set_target(
                                self.attributes[r_local_key],
                                key=r_foreign_key
                            ).find(projection=projection.get(r_target))

                        # no projection
                        else:

                            collection = r_model().set_target(
                                self.attributes[r_local_key],
                                key=r_foreign_key
                            ).find()

                        # determine relationship resolution errors
                        targets_found = collection.get_ids()
                        for target in self.attributes[r_local_key]:
                            if target not in targets_found:
                                error = RelationshipResolutionError(data={
                                    "model": r_model.__name__,
                                    "target": target
                                })
                                collection.add(error)

                        self.attributes[r_target] = collection

                # external relationship
                else:

                    # one to one : foreign, many to one : foreign
                    if r_type in ["one_to_one", "many_to_one"]:
                        try:

                            # projection
                            if type(projection.get(r_target)) is dict:
                                self.attributes[r_target] = r_model({
                                    r_foreign_key: self.get(r_local_key)
                                }).find(projection=projection.get(r_target))

                            # no projection
                            else:
                                self.attributes[r_target] = r_model({
                                    r_foreign_key: self.get(r_local_key)
                                }).find()

                        # relationship resolution error
                        except:
                            self.attributes[r_target] = None

                    # one to many : foreign
                    elif r_type in ["one_to_many", "many_to_many"]:

                        # projection
                        if type(projection.get(r_target)) is dict:
                            self.attributes[r_target] = r_model().set_target(
                                self.get(r_local_key),
                                key=r_foreign_key
                            ).find(projection=projection.get(r_target))

                        # no projection
                        else:
                            self.attributes[r_target] = r_model().set_target(
                                self.get(r_local_key),
                                key=r_foreign_key
                            ).find()

        return self

    # view attributes

    def ref(self, key=None, create=False):

        if type(key) is not DotNotationString:
            key = DotNotationString(key)

        local_key = key
        for i, needle in enumerate(key, 1):
            local_key = key[:i]

            if needle:

                if not self.attributes.has(local_key):
                    if not create:
                        return Undefined()

                elif i < len(key) and \
                        isinstance(self.attributes.ref(local_key),
                                   (Model, Collection)):
                    return self.attributes.ref(local_key).ref(
                        key=key[i:],
                        create=create
                    )

                elif i < len(key) and \
                        type(self.attributes.ref(local_key)) is not dict:
                    if not create:
                        return Undefined()

        return self.attributes.ref(local_key, create=create)

    def has(self, key):

        if type(key) is not DotNotationString:
            key = DotNotationString(key)

        for i, needle in enumerate(key, 1):
            local_key = key[:i]

            if not self.attributes.has(local_key):
                return False

            elif i < len(key) and \
                    isinstance(self.attributes.ref(local_key),
                               (Model, Collection)):

                return self.attributes.ref(local_key).has(
                    key=key[i:]
                )

            elif i < len(key) and \
                    type(self.attributes.ref(local_key)) is not dict:
                return False

        return True

    def get(self, key=None, projection=None, default=True, setup=False):

        # setup projection
        if not setup:

            if projection and type(projection) is not Projection:
                projection = Projection(projection)

                if self.default_get_projection and default:
                    _projection = copy.deepcopy(self.default_get_projection)
                    _projection.update(projection)
                    projection = _projection

            elif not projection and self.default_get_projection and default:
                projection = self.default_get_projection

        # setup haystack
        clone = copy.deepcopy(self)
        clone.set_computed_attributes()
        haystack = clone.attributes

        # setup needle

        if type(key) is not DotNotationString:
            key = DotNotationString(key)

        for i, needle in enumerate(key, 1):
            local_key = key[:i]

            if needle:

                if not haystack.has(local_key):
                    return Undefined()

                elif isinstance(haystack.ref(local_key), (Model, Collection)):

                    if projection and projection.has(local_key):
                        projection = projection.spawn(local_key)

                    return haystack.ref(local_key).get(
                        key=key[i:],
                        projection=projection,
                        setup=True
                    )

                elif isinstance(haystack.ref(local_key), BaseException):
                    return haystack.ref(local_key).get()

            # apply projection
            if i == len(key):

                haystack = haystack.ref(local_key)

                # apply projection to dict
                if type(haystack) is dict:
                    data = {}
                    for k, v in haystack.items():
                        local_key = ".".join(key.keys + [k]) if needle else k

                        # no projection or include or missing from
                        # exclusive projection
                        if not projection or \
                                projection.get_type() == "exclusive" and not \
                                projection.has(local_key) or \
                                projection.get(local_key) == 1:

                            data[k] = self.get(
                                key=local_key,
                                setup=True
                            )

                        # exclude
                        elif projection.get(local_key) == 0:
                            continue

                        # include with projection
                        elif type(projection.get(local_key)) is dict:
                            data[k] = self.get(
                                key=local_key,
                                projection=projection,
                                setup=True
                            )

                    return data

                else:
                    return copy.deepcopy(haystack)

    # update attributes

    def generate_id(self):
        return bson.objectid.ObjectId()

    def set(self, key, value=None, create=True, record=True):

        if type(key) is dict:
            for k, v in key.items():
                self.set(k, v, create, record)
            return self

        if type(key) is not DotNotationString:
            key = DotNotationString(key)

        for i, needle in enumerate(key, 1):
            local_key = key[:i]

            if not self.attributes.has(local_key):
                if not create:
                    raise KeyError(
                        self.attributes.format_keyerror(needle, key)
                    )

            elif i < len(key) and \
                    isinstance(self.attributes.ref(local_key),
                               (Model, Collection)):

                return self.attributes.ref(local_key).set(
                    key=key[i:],
                    value=value,
                    create=create,
                    record=record
                )

            elif i < len(key) and \
                    type(self.attributes.ref(local_key)) is not dict:

                if not create:
                    message = self.attributes.format_typeerror(
                        self.attributes.ref(local_key),
                        needle,
                        key
                    )
                    raise TypeError(message)

        self.attributes.set(key, value, create=create)

        if record:
            if not self.original or not \
                    self.original.has(key) or \
                    self.original.ref(key) != value:

                self.record_update(
                    "$set",
                    copy.copy(key),
                    copy.deepcopy(value)
                )

            elif self.updates.has("$set.{}".format(key)):
                self.updates.unset("$set.{}".format(key), cleanup=True)

        return self

    def unset(self, key, record=True, force=False):

        try:

            # setup haystack
            haystack = self.attributes

            # setup needle
            if type(key) is not DotNotationString:
                key = DotNotationString(key)

            for i, needle in enumerate(key, 1):
                local_key = key[:i]

                if not haystack.has(local_key):
                    message = haystack.format_keyerror(needle, key)
                    raise KeyError(message)

                elif i < len(key) and \
                        isinstance(haystack.ref(local_key),
                                   (Model, Collection)):
                    return haystack.ref(local_key).unset(
                        key=key[i:],
                        record=record,
                        force=force
                    )

                elif i < len(key) and \
                        isinstance(haystack.ref(local_key),
                                   RelationshipResolutionError):

                    message = haystack.format_typeerror(
                        haystack.ref(local_key),
                        needle,
                        key
                    )
                    raise TypeError(message)

                elif i < len(key) and \
                        type(haystack.ref(local_key)) is not dict:

                    message = haystack.format_typeerror(
                        haystack.ref(local_key),
                        needle,
                        key
                    )
                    raise TypeError(message)

            haystack.unset(key)

        except:
            if not self.original or force:
                pass
            else:
                raise

        if record:
            if not self.original or self.original.has(key):
                self.record_update("$unset", copy.copy(key), "")

        return self

    def unset_many(self, keys, record=True, force=False):
        for key in keys:
            self.unset(key, record=record, force=force)
        return self

    def push(self, key, value, create=True, record=True):

        if type(key) is not DotNotationString:
            key = DotNotationString(key)

        for i, needle in enumerate(key, 1):
            local_key = key[:i]

            if not self.attributes.has(local_key):
                if not create:
                    message = self.attributes.format_keyerror(needle, key)
                    raise KeyError(message)

            elif i < len(key) and \
                    isinstance(self.attributes.ref(local_key),
                               (Model, Collection)):
                return self.attributes.ref(local_key).push(
                    key=key[i:],
                    value=value,
                    create=create,
                    record=record
                )

            elif i < len(key) and \
                    type(self.attributes.ref(local_key)) is not dict:
                if not create:
                    message = self.attributes.format_typeerror(
                        self.attributes.ref(local_key),
                        needle,
                        key
                    )
                    raise TypeError(message)

        self.attributes.push(key, value, create=create)

        if record:
            self.record_update("$push", copy.copy(key), copy.deepcopy(value))

        return self

    def push_many(self, key, values, record=True):
        for value in values:
            self.push(key, value, record=record)
        return self

    def pull(self, key, value, record=True, force=False, cleanup=False):

        try:
            if type(key) is not DotNotationString:
                key = DotNotationString(key)

            for i, needle in enumerate(key, 1):
                local_key = key[:i]

                if not self.attributes.has(local_key):
                    message = self.attributes.format_keyerror(needle, key)
                    raise KeyError(message)

                elif i < len(key) and \
                        isinstance(self.attributes.ref(local_key),
                                   (Model, Collection)):
                    return self.attributes.ref(local_key).pull(
                        key=key[i:],
                        value=value,
                        record=record,
                        force=force,
                        cleanup=cleanup
                    )

                elif i < len(key) and \
                        type(self.attributes.ref(local_key)) is not dict:
                    message = self.attributes.format_typeerror(
                        self.attributes.ref(local_key),
                        needle,
                        key
                    )
                    raise TypeError(message)

            self.attributes.pull(key, value, cleanup=cleanup)

        except:
            if not self.original or force:
                pass
            else:
                raise

        if record:
            if not self.original or \
                    self.original.has(key) and value in self.original.get(key):
                self.record_update(
                    "$pull",
                    copy.copy(key),
                    copy.deepcopy(value)
                )

        return self

    def pull_many(self, key, values, record=True, force=False):
        for value in values:
            self.pull(key, value, record=record, force=force)
        return self

    def delete(self, cascade=False):
        """ Sets the delete flag on a model to True

        When model.save() is called, if model._delete is true model.target will
        be used to find and delete a document in the collection
        model.pymongo_collection

        Args:
            cascade (boolean, optional): Defaults to True. If True,
            model._delete will also be set to True for all nested models

        Returns:
            self

        """
        self._delete = True
        if cascade:
            for v in self.attributes.collapse().values():
                if isinstance(v, (Model, Collection)):
                    v.delete()
        return self

    def reset(self):
        self.attributes.clear()
        self.target.clear()
        self.original.clear()
        self.updates.clear()
        self._delete = False
        return self

    # record updates in mongodb operator syntax

    def record_update(self, o, key, value):

        if not self.updates.has(o):
            self.updates.set(o, {})

        # operator key
        oper_key = "{}.{}".format(o, key)

        if o == "$set":
            if type(value) is dict:
                self.updates.set(oper_key, NestedDict(value))
            else:
                self.updates.set(oper_key, value)

        elif o == "$unset":
            self.updates.set(oper_key, "")

        elif o in ["$push", "$pull"]:

            if o == "$pull":
                iterator = "$in"
                # opposite iterator key
                _key = "{}.{}".format("$push", key)
                # opposite iterator
                _iterator = "$each"

            else:
                iterator = "$each"
                # opposite key
                _key = "{}.{}".format("$pull", key)
                # opposite_iterator
                _iterator = "$in"

            # handle existing values
            if not self.updates.has(oper_key):
                existing_values = []
            elif type(self.updates.ref(oper_key)) is dict and \
                    iterator in self.updates.ref(oper_key):
                existing_values = self.updates.get(
                    "{}.{}".format(oper_key, iterator)
                )
            else:
                existing_values = [self.updates.get(oper_key)]

            # append new values
            existing_values.append(value)

            # record change
            if len(existing_values) == 1:
                self.updates.set(oper_key, existing_values[0])
            else:
                self.updates.set(oper_key, {iterator: existing_values})

            # cleanup opposite operator
            if self.updates.has(_key):
                # opposite reference
                _ref = self.updates.ref(_key)

                # opposite is a string
                if type(_ref) is str and _ref == value:
                    self.updates.unset(_key, cleanup=True)

                # opposite is list
                elif type(_ref) is dict:
                    # opposite values
                    _values = self.updates.get(
                        "{}.{}".format(_key, _iterator)
                    )

                    # new is string
                    if value in _values:
                        _values.remove(value)

                        # set value using iterator correctly
                        if len(_values) > 1:
                            self.updates.set(
                                "{}.{}".format(_key, _iterator),
                                _values
                            )
                        elif len(_values) == 1:
                            self.updates.set(_key, _values[0])

    # persist updates

    def save(self, cascade=True, default=True):
        """ Saves model and nested model changes to the database

        Calls delete_one, update_one or insert_one for model.pymongo_collection
        based on model state attributes. Depending on the method called,
        certain protected and extendable hooks are also called.
        State required to delete a model:
            model._delete is true. This applies regardless of the value of
                other model state attributes.
        State required to update a model:
            model.target is set
            model._changed is set
        State required to insert a model:
            model.target is not set
            model._changed is set
        If keyword argument cascade is True (this is the default value) save is
        also called on nested models, even if the parent model is unchanged. If
        hooks are set they will be called with their respective operation.
        Hooks checked for are:
            model.pre_delete_hook
            model.pre_update_hook
            model.pre_insert_hook
            model.post_delete_hook
            model.post_update_hook
            model.post_insert_hook
        Some save functionality is hidden in protected hooks. These hooks are:
            model._pre_insert_hook
            model._post_insert_hook
            model._post_find_hook
            model._post_update_hook

        Args:
            cascade (boolean, optional): Defaults to True. If True, save is
            also called on nested models, even if the parent model is unchanged

        Returns:
            self
        """

        # delete
        if self._delete:

            if not self.target:
                raise ModelTargetNotSet

            if "pre_delete_hook" in dir(self):
                self.pre_delete_hook()

            m = self.pymongo_collection.delete_one(self.target.get())
            if not m.deleted_count:
                raise ModelNotDeleted(data=self.target.get())

            if cascade:
                self.reference_nested_models()

            if "post_delete_hook" in dir(self):
                self.post_delete_hook()

        # update
        elif self.target and self.updates:

            if "pre_update_hook" in dir(self):
                self.pre_update_hook()

            m = self.pymongo_collection.update_one(
                self.target.get(),
                self.flatten_updates(cascade=cascade)
            )

            if not m.modified_count:
                raise ModelNotUpdated(data=self.target.get())

            self._post_update_hook()
            if "post_update_hook" in dir(self):
                self.post_update_hook()

        # insert
        elif not self.target:

            self._pre_insert_hook(default=default)

            if "pre_insert_hook" in dir(self):
                self.pre_insert_hook()

            m = self.pymongo_collection.insert_one(
                self.reference_nested_models(cascade=cascade)
            )

            self._post_insert_hook()
            if "post_insert_hook" in dir(self):
                self.post_insert_hook()

        # cascade save to nested models
        elif cascade:
            self.reference_nested_models(cascade=cascade)

        return self

    def flatten_updates(self, cascade=True):
        flattened = {}
        for method, data in self.updates.items():
            ref = self.reference_nested_models(data, cascade)
            flattened[method] = self.collapse_dot_notation(ref)
        return flattened

    def collapse_dot_notation(self, data, parent_key=None):
        items = []
        for key, val in data.items():
            new_key = "%s.%s" % (parent_key, key) if parent_key else key
            if type(val) is dict and not \
                    set(val.keys()) & set(["$in", "$each"]):
                collapsed = self.collapse_dot_notation(val, new_key)
                items.extend(collapsed.items())
            else:
                items.append((new_key, val))
        return dict(items)

    def reference_nested_models(self, haystack=None, cascade=True):

        if haystack is None:
            haystack = self.attributes

        referenced = {}
        for k, v in haystack.items():

            # model
            if isinstance(v, Model):
                if cascade:
                    v.save(cascade=cascade)
                referenced[k] = v.get_id()

            # collection
            elif isinstance(v, Collection):
                if cascade:
                    v.save(cascade=cascade)
                referenced[k] = v.get_ids()

            # dict
            elif type(v) is dict:
                referenced[k] = self.reference_nested_models(v, cascade)

            # everything else
            else:
                referenced[k] = v

        return referenced

    # hooks

    def _pre_insert_hook(self, default=True):
        if default:
            self.set_default_attributes()

        if self.id_attribute not in self.attributes:
            self.set(self.id_attribute, self.generate_id())

    def _post_insert_hook(self):
        if self.has(self.id_attribute):
            self.set_target(self.attributes.get(self.id_attribute))
        self.original(copy.deepcopy(self.attributes))
        self.updates.clear()

    def _post_find_hook(self, data):
        if self.id_attribute in data:
            self.set_target(data[self.id_attribute])
        self.attributes(data)
        self.original(copy.deepcopy(data))

    def _post_update_hook(self):
        self.original(copy.deepcopy(self.attributes))
        self.updates.clear()


class Collection(object):

    model = Model

    def __init__(self, target=None):
        self.target = DotNotationContainer()
        self.collection = []
        self.default_sort = None
        self.default_find_projection = DotNotationContainer()
        self.default_get_projection = DotNotationContainer()

        if target:
            self.set_target(target)

    def __copy__(self):
        new = type(self)()
        new.__dict__.update(self.__dict__)
        return new

    def __deepcopy__(self, memo):
        new = type(self)()
        new.__dict__.update(copy.deepcopy(self.__dict__))
        return new

    def __len__(self):
        return len(self.collection)

    def __iter__(self):
        for m in self.collection:
            yield m

    # target

    def set_target(self, value, key=None):
        if key is None:
            key = self.model.id_attribute

        if type(value) is dict:
            self.target(value)

        else:
            if type(value) is not list:
                value = [value]
            self.target({key: {"$in": value}})

        return self

    def get_target(self):
        if self.target:
            return self.target.get()
        else:
            return None

    def get_targets(self):
        return [m.get_target() for m in self]

    def get_ids(self):
        return [m.get_id() for m in self]

    # recall attributes

    def find(self, projection=None, default_projection=True,
             default_model_projection=False):

        if "pre_find_hook" in dir(self):
            self.pre_find_hook()

        # setup projection
        p = Projection()

        if projection:
            p.merge(projection)

        if self.default_find_projection and default_projection:
            p.merge(self.default_find_projection)

        if default_model_projection:
            model_default = self.model().default_find_projection.get()
            if model_default:
                p.merge(model_default)

        if p:
            flattened_projection = p.flatten()

        # find
        if not p or not flattened_projection:
            if self.target:
                collection = self.model.pymongo_collection.find(
                    filter=self.target.get()
                )
            else:
                collection = self.model.pymongo_collection.find()
        else:
            if self.target:
                collection = self.model.pymongo_collection.find(
                    filter=self.target.get(),
                    projection=flattened_projection
                )
            else:
                collection = self.model.pymongo_collection.find(
                    projection=flattened_projection
                )

        for m in collection:

            model = self.model()

            if "pre_find_hook" in dir(model):
                model.pre_find_hook()

            model._post_find_hook(m)

            if "post_find_hook" in dir(model):
                model.post_find_hook()

            # resolve relationships
            if model.relationships and projection:
                model.dereference_nested_models(projection=projection)

            self.collection.append(model)

        if "post_find_hook" in dir(self):
            self.post_find_hook()

        return self

    # view attributes

    def ref(self, *args, **kwargs):
        return [m.ref(*args, **kwargs) for m in self]

    def has(self, *args, **kwargs):
        return [m.has(*args, **kwargs) for m in self]

    def get(self, *args, **kwargs):
        return [m.get(*args, **kwargs) for m in self]

    # update attributes

    def set(self, *args, **kwargs):
        for m in self:
            m.set(*args, **kwargs)
        return self

    def unset(self, *args, **kwargs):
        for m in self:
            m.unset(*args, **kwargs)
        return self

    def unset_many(self, *args, **kwargs):
        for m in self:
            m.unset_many(*args, **kwargs)
        return self

    def push(self, *args, **kwargs):
        for m in self:
            m.push(*args, **kwargs)
        return self

    def push_many(self, *args, **kwargs):
        for m in self:
            m.push_many(*args, **kwargs)
        return self

    def pull(self, *args, **kwargs):
        for m in self:
            m.pull(*args, **kwargs)
        return self

    def pull_many(self, *args, **kwargs):
        for m in self:
            m.pull_many(*args, **kwargs)
        return self

    def delete(self, **kwargs):
        for m in self:
            m.delete(**kwargs)
        return self

    def reset(self):
        self.target.clear()
        self.collection = []
        return self

    # persist updates

    def save(self, cascade=True):

        if "pre_modify_hook" in dir(self):
            self.pre_modify_hook()

        requests = []

        for m in self:

            # delete
            if m._delete:
                if not m.target:
                    raise ModelTargetNotSet

                if "pre_delete_hook" in dir(m):
                    m.pre_delete_hook()

                requests.append(pymongo.DeleteOne(m.target.get()))

                if cascade:
                    m.reference_nested_models(cascade=cascade)

            # update
            elif m.target and m.updates:

                if "pre_update_hook" in dir(m):
                    m.pre_update_hook()

                requests.append(pymongo.UpdateOne(
                                    m.target.get(),
                                    m.flatten_updates(cascade=cascade))
                                )

            # insert
            elif not m.target:
                m._pre_insert_hook()
                if "pre_insert_hook" in dir(m):
                    m.pre_insert_hook()

                requests.append(pymongo.InsertOne(
                                    m.reference_nested_models(cascade=cascade))
                                )

            elif cascade:
                m.reference_nested_models(cascade=cascade)

        # execute requests with bulk write
        if requests:
            self.model.pymongo_collection.bulk_write(requests)

        for m in self:

            # delete
            if m._delete and m.target:
                if "post_delete_hook" in dir(m):
                    m.post_delete_hook()

            # update
            elif m.target:
                m._post_update_hook()
                if "post_update_hook" in dir(m):
                    m.post_update_hook()

            # insert
            else:
                m._post_insert_hook()
                if "post_insert_hook" in dir(m):
                    m.post_insert_hook()

        if "post_modify_hook" in dir(self):
            self.post_modify_hook()

        return self

    # update collection members

    def add(self, *args):
        if type(args[0]) not in [self.model, RelationshipResolutionError]:
            raise CollectionModelClassMismatch
        else:
            self.collection.append(args[0])

    def remove(self, *args):
        if args[0] not in self:
            raise CollectionModelNotPresent
        else:
            self.collection.remove(args[0])
