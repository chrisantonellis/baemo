
import bson
import copy

from .delimited import DelimitedStr
from .delimited import DelimitedDict
from .connection import Connections
from .entity import EntityMeta
from .entity import Entities
from .references import References
from .projection import Projection
from .collection import Collection
from .exceptions import ModelNotFound
from .exceptions import ModelNotUpdated
from .exceptions import ModelNotDeleted
from .exceptions import ModelTargetNotSet
from .exceptions import DereferenceError


class Model(object):
    """
    Model is an abstraction of a MongoDB document with methods for reading,
    manipulating and saving the data in a document.
    """

    # connection name
    # NOTE: connections are created and cached in the Connection module
    connection = None

    # collection name
    collection = None

    # id attribute type
    id_type = bson.objectid.ObjectId

    # id attribute key
    id_attribute = "_id"

    # reference definitions
    # NOTE: the type of this attribute is used during entity creation
    references = References()

    # find projection
    find_projection = Projection()

    # get projection
    get_projection = Projection()

    # default target
    default_target = DelimitedDict()

    # default attributes
    default_attributes = DelimitedDict()

    def __init__(self, target=None):
        """ Setup the model and prepare for use, create instance attributes and
        use defaults or arguments if set
        """

        # these values are cached after every operation
        self._projection = None
        self._operation = None
        self._result = None

        # target
        self.target = DelimitedDict(self.default_target.get())

        # set target if passed
        if target:
            self.set_target(target)

        # the original state of the document
        self.original = DelimitedDict()

        # the current state of the document
        self.attributes = DelimitedDict(self.default_attributes.get())

        # updates made to this document, in MongoDB update operator syntax
        self.updates = DelimitedDict()

        # delete flag
        self._delete = False

        # found as reference flag
        self._as_reference = False

        super().__init__()

    # magic methods

    def __copy__(self):
        new = type(self)()
        new.__dict__.update(copy.copy(self.__dict__))
        return new

    def __deepcopy__(self, memo):
        new = type(self)()
        new.__dict__.update(copy.deepcopy(self.__dict__))
        return new

    def __eq__(self, obj):
        return self.__class__ is obj.__class__ and self.attributes == obj.attributes  # noqa

    def __ne__(self, obj):
        return not self.__eq__(obj)

    # target

    def set_target(self, target):
        """ set target to argument.
        if argument is not a dict, create a dict using id_attribute as the key
        """

        if type(target) is dict:
            self.target(target)
        else:
            self.target({self.id_attribute: target})
        return self

    def get_target(self):
        """ return target if set, else return None
        """

        if self.target:
            return self.target.get()
        else:
            return None

    def get_id(self):
        """ return id_attribute portion of target if set, else return None
        because targets can contain more than just an id key and
        value, this method allows for extracing the id portion from
        complicated targets
        """

        if self.target.has(self.id_attribute):
            return self.target.get(self.id_attribute)
        else:
            return None

    # recall attributes

    def find(self, projection=None, default=True, _as_reference=False):
        """ find a document in the datbase and set the document in
        self.attributes.
        """

        # if finding as a reference, update state of entity
        if _as_reference:
            self._as_reference = _as_reference

        # check if target is set
        if not self.target:
            raise ModelTargetNotSet

        # pre find hook
        if callable(getattr(self, "pre_find_hook", None)):
            self.pre_find_hook()

        kwargs = {}

        # filter
        if self.target:
            kwargs["filter"] = self.target.get()

        # projection
        p = Projection()
        if projection is not None:
            p.merge(projection)
        if self.find_projection and default:
            p.merge(self.find_projection)
        flattened_projection = p.flatten()
        if flattened_projection:
            self._projection = flattened_projection
            kwargs["projection"] = flattened_projection

        # find
        connection = Connections.get(
            self.connection,
            self.collection
        )

        m = connection.find_one(**kwargs)

        if m is None:
            raise ModelNotFound(data=self.target.get())

        # post find hook
        self._post_find_hook(m)
        if callable(getattr(self, "post_find_hook", None)):
            self.post_find_hook()

        # dereference nested models
        if self.references and projection:
            self.dereference_entities(projection=projection)

        return self

    def dereference_entities(self, projection):

        for k, reference in self.references.collapse().items():
            entity = Entities.get(reference["entity"])
            type_ = reference["type"]

            if "foreign_key" in reference:
                foreign_key = reference["foreign_key"]
            else:
                foreign_key = entity["model"].id_attribute


            if k in projection and \
            (type(projection.get(k) is dict or projection.get(k) == 2)):

                # setup kwargs
                kwargs = {}

                kwargs["_as_reference"] = True

                if type(projection.get(k)) is dict:
                    kwargs["projection"] = projection.get(k)

                # local reference
                if k in self.attributes and self.attributes[k]:

                    # one
                    if type_ == "local_one":
                        try:
                            self.attributes[k] = entity["model"]({
                                foreign_key: self.attributes[k]
                            }).find(**kwargs)

                        # dereference error
                        except:
                            error = DereferenceError(data={
                                "model": entity["model"].__name__,
                                "t": self.attributes[k]
                            })
                            self.attributes[k] = error

                    # many
                    elif type_ == "local_many":

                        collection = entity["collection"]().set_target(
                            self.attributes[k],
                            key=foreign_key
                        ).find(**kwargs)

                        # determine dereference errors
                        models_found = collection.get_ids()
                        for model_target in self.attributes[k]:
                            if model_target not in models_found:
                                error = DereferenceError(data={
                                    "model": entity["collection"].__name__,
                                    "target": model_target
                                })
                                collection.add(error)

                        self.attributes[k] = collection

                # foreign reference
                else:
                    source = entity["model"].id_attribute

                    # one
                    if type_ == "foreign_one":
                        try:
                            self.attributes[k] = entity["model"]({
                                foreign_key: self.get(source)
                            }).find(**kwargs)

                        # dereference error
                        except:
                            self.attributes[k] = None

                    # many
                    elif type_ == "foreign_many":
                        collection = entity["collection"]().set_target(
                            self.get(source),
                            key=foreign_key
                        ).find(**kwargs)

                        self.attributes[k] = collection

        return self

    # view attributes

    def ref(self, key=None, create=False):
        if type(key) is not DelimitedStr:
            key = DelimitedStr(key)

        local_key = key
        for i, needle in enumerate(key, 1):
            local_key = key[:i]

            if needle:
                if i < len(key) \
                        and self.attributes.has(local_key) \
                        and isinstance(self.attributes.ref(local_key), EntityMeta): # noqa
                    return self.attributes.ref(local_key).ref(
                        key[i:],
                        create=create
                    )

        return self.attributes.ref(key, create=create)

    def has(self, key):

        if type(key) is not DelimitedStr:
            key = DelimitedStr(key)

        for i, needle in enumerate(key, 1):
            local_key = key[:i]

            if not self.attributes.has(local_key):
                return False

            elif i < len(key) and isinstance(self.attributes.ref(local_key), EntityMeta): # noqa

                return self.attributes.ref(local_key).has(key=key[i:])

            elif i < len(key) and type(self.attributes.ref(local_key)) is not dict: # noqa
                return False

        return True

    def get(self, *args, projection=None, default=True, setup=False):

        args = list(args)
        if len(args) == 0:
            key = None
        else:
            key = args[0]

        if len(args) < 2:
            use_default_value = False
        else:
            use_default_value = True
            default_value = args[1]

        # setup projection
        if not setup:

            if projection and type(projection) is not Projection:
                projection = Projection(projection)

                if self.get_projection and default:
                    _projection = copy.deepcopy(self.get_projection)
                    _projection.update(projection)
                    projection = _projection

            elif not projection and self.get_projection and default:
                projection = self.get_projection

        # setup haystack
        attr = copy.deepcopy(self.attributes)
        haystack = attr

        # setup needle
        if type(key) is not DelimitedStr:
            key = DelimitedStr(key)

        for i, needle in enumerate(key, 1):
            if not haystack.has(needle) and use_default_value:
                return default_value

            elif isinstance(haystack.ref(needle), EntityMeta):
                if projection and projection.has(needle):
                    projection = projection.clone(needle)

                args[0] = key[i:]

                return haystack.ref(needle).get(
                    *args,
                    projection=projection,
                    setup=True
                )

            elif isinstance(haystack.ref(needle), BaseException):
                return haystack.ref(needle).get()

            # return haystack as dot notation container
            elif isinstance(haystack.ref(needle), dict):
                haystack = haystack.clone(needle)

            # return value
            else:
                haystack = haystack.ref(needle)

        if type(haystack) in [dict, DelimitedDict]:
            data = {}
            for k, v in haystack.items():
                local_key = ".".join(key.keys + [k]) if key else k

                if args:
                    args[0] = local_key
                else:
                    args = [local_key]

                # no projection or include or missing from
                # exclusive projection
                if not projection or \
                        (not projection.has(local_key) and projection.validate() == "exclusive") or \
                        (projection.has(local_key) and projection.get(local_key) == 1):

                    data[k] = self.get(
                        *args,
                        setup=True
                    )

                # exclude
                elif projection.has(local_key) and \
                        projection.get(local_key) == 0:
                    continue

                # include with projection
                elif projection.has(local_key) and \
                        type(projection.get(local_key)) is dict:
                    data[k] = self.get(
                        *args,
                        projection=projection,
                        setup=True
                    )

            return data

        else:
            return copy.deepcopy(haystack)

    # update attributes

    def generate_id(self):
        return self.id_type()

    def set(self, key, value=None, create=True, record=True):

        if type(key) is dict:
            for k, v in key.items():
                self.set(k, v, create, record)
            return self

        if type(key) is not DelimitedStr:
            key = DelimitedStr(key)

        for i, needle in enumerate(key, 1):
            local_key = key[:i]

            if not self.attributes.has(local_key):
                if not create:
                    raise KeyError(
                        self.attributes._format_keyerror(needle, key)
                    )

            elif i < len(key) and \
                    isinstance(self.attributes.ref(local_key), EntityMeta):

                return self.attributes.ref(local_key).set(
                    key=key[i:],
                    value=value,
                    create=create,
                    record=record
                )

            elif i < len(key) and \
                    type(self.attributes.ref(local_key)) is not dict:

                if not create:
                    message = self.attributes._format_typeerror(
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

    def unset(self, key, record=True, force=False, cleanup=False):

        try:

            if type(key) is not DelimitedStr:
                key = DelimitedStr(key)

            for i, needle in enumerate(key, 1):
                local_key = key[:i]

                if not self.attributes.has(local_key):
                    message = self.attributes._format_keyerror(needle, key)
                    raise KeyError(message)

                elif i < len(key) and \
                        isinstance(self.attributes.ref(local_key), EntityMeta):
                    return self.attributes.ref(local_key).unset(
                        key=key[i:],
                        record=record,
                        force=force
                    )

                elif i < len(key) and \
                        isinstance(self.attributes.ref(local_key),
                                   DereferenceError):

                    message = self.attributes._format_typeerror(
                        self.attributes.ref(local_key),
                        needle,
                        key
                    )
                    raise TypeError(message)

                elif i < len(key) and \
                        type(self.attributes.ref(local_key)) is not dict:

                    message = self.attributes._format_typeerror(
                        self.attributes.ref(local_key),
                        needle,
                        key
                    )
                    raise TypeError(message)

            self.attributes.unset(key, cleanup=cleanup)

        except:
            if not self.original or force:
                pass
            else:
                raise

        if record:
            if not self.original or self.original.has(key):
                self.record_update("$unset", copy.copy(key), "")

        return self

    def unset_many(self, keys, record=True, force=False, cleanup=False):
        for key in keys:
            self.unset(key, record=record, force=force, cleanup=cleanup)
        return self

    def push(self, key, value, create=True, record=True):

        if type(key) is not DelimitedStr:
            key = DelimitedStr(key)

        for i, needle in enumerate(key, 1):
            local_key = key[:i]

            if not self.attributes.has(local_key):
                if not create:
                    message = self.attributes._format_keyerror(needle, key)
                    raise KeyError(message)

            elif i < len(key) and \
                    isinstance(self.attributes.ref(local_key), EntityMeta):
                return self.attributes.ref(local_key).push(
                    key=key[i:],
                    value=value,
                    create=create,
                    record=record
                )

            elif i < len(key) and \
                    type(self.attributes.ref(local_key)) is not dict:
                if not create:
                    message = self.attributes._format_typeerror(
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
            if type(key) is not DelimitedStr:
                key = DelimitedStr(key)

            for i, needle in enumerate(key, 1):
                local_key = key[:i]

                if not self.attributes.has(local_key):
                    message = self.attributes._format_keyerror(needle, key)
                    raise KeyError(message)

                elif i < len(key) and \
                        isinstance(self.attributes.ref(local_key), EntityMeta):
                    return self.attributes.ref(local_key).pull(
                        key=key[i:],
                        value=value,
                        record=record,
                        force=force,
                        cleanup=cleanup
                    )

                elif i < len(key) and \
                        type(self.attributes.ref(local_key)) is not dict:
                    message = self.attributes._format_typeerror(
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
        if cascade:
            for v in self.attributes.collapse().values():
                if isinstance(v, EntityMeta):
                    v.delete(cascade=cascade)
        self._delete = True
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
                self.updates.set(
                    oper_key,
                    type("NestedDict", (dict,), {})(value)
                )
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

            elif isinstance(self.updates.ref(oper_key), dict) and \
                    iterator in self.updates.ref(oper_key):
                existing_values = self.updates.get(
                    "{}.{}".format(oper_key, iterator)
                )

            else:
                existing_values = [self.updates.get(oper_key)]

            # append new values
            if isinstance(value, dict):
                value = type("NestedDict", (dict,), {})(value)
            existing_values.append(value)

            # record change
            if len(existing_values) == 1:
                self.updates.set(oper_key, existing_values[0])
            else:
                self.updates.set(
                    oper_key,
                    type("NestedDict", (dict,), {})({
                        iterator: existing_values
                    })
                )

            # cleanup opposite operator
            if self.updates.has(_key):
                # opposite reference
                _ref = self.updates.ref(_key)

                # opposite is a string
                if type(_ref) is str and _ref == value:
                    self.updates.unset(_key, cleanup=True)

                # opposite is list
                elif isinstance(_ref, dict):
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

    def cache_operation(self, type_, target=None, operators=None):
        self._operation = {
            "type": type_,
            "target": target,
            "operators": operators
        }

    def cache_result(self, target=None, attributes=None):
        self._result = {
            "target": target,
            "attributes": attributes
        }

    def save(self, cascade=True, default=True):

        connection = Connections.get(
            self.connection,
            self.collection
        )

        # delete
        if self._delete:

            if not self.target:
                raise ModelTargetNotSet

            if callable(getattr(self, "pre_delete_hook", None)):
                self.pre_delete_hook()

            # run operation
            m = connection.find_one_and_delete(self.target.get())

            # cache operation
            self.cache_operation("delete", self.target.get())

            if m is None:
                raise ModelNotDeleted(data=self.target.get())

            # cache result
            self.cache_result()

            if cascade:
                self.reference_entities(self.attributes)

            if callable(getattr(self, "post_delete_hook", None)):
                self.post_delete_hook()

        # update
        elif self.target and self.updates:

            if callable(getattr(self, "pre_update_hook", None)):
                self.pre_update_hook()

            # run operation
            updates = self.flatten_updates(cascade=cascade)

            m = connection.find_one_and_update(
                self.target.get(),
                updates
            )

            # cache operation
            self.cache_operation("update", self.target.get(), updates)

            if m is None:
                raise ModelNotUpdated(data=self.target.get())

            # cache result
            self.cache_result(self.target.get(), m)

            self._post_update_hook()
            if callable(getattr(self, "post_update_hook", None)):
                self.post_update_hook()

        # insert
        elif not self.target:

            # if not

            self._pre_insert_hook(default=default)

            if callable(getattr(self, "pre_insert_hook", None)):
                self.pre_insert_hook()

            # cache operation
            self.cache_operation("insert", None, {"$set": self.attributes.get()})

            m = connection.insert_one(
                self.reference_entities(self.attributes, cascade)
            )

            # cache result
            self.cache_result(self.target.get(), self.attributes.get())

            self._post_insert_hook()
            if callable(getattr(self, "post_insert_hook", None)):
                self.post_insert_hook()

        # cascade save to nested models
        elif cascade:
            self.reference_entities(self.attributes, cascade)

        return self

    def flatten_updates(self, cascade=True):
        flattened = {}
        for method, updates in self.reference_entities(self.updates).items():
            flattened[method] = DelimitedDict(updates).collapse()
        return flattened

    def reference_entities(self, data, cascade=True):

        referenced = DelimitedDict()
        references = self.references.collapse()

        # iterate over collapsed data
        for k, v in data.collapse().items():

            # value in data is dereferenced entity
            if k in references and isinstance(v, EntityMeta):

                if cascade:
                    v.save(cascade=cascade)

                reference = references[k]
                entity = Entities.get(reference["entity"])

                if "foreign_key" in reference:
                    foreign_key = reference["foreign_key"]
                else:
                    foreign_key = entity["model"].id_attribute

                if reference["type"] == "local_one":
                    referenced[k] = v.get(foreign_key)

                elif reference["type"] == "local_many":
                    referenced[k] = v.get(foreign_key)

            # pass thru
            else:
                referenced[k] = v

        return referenced

    # hooks

    def _pre_insert_hook(self, default=True):
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
