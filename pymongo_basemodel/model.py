
import bson
import copy
import datetime

from .delimited import DelimitedStr
from .delimited import DelimitedDict

from .projection import Projection

from .collection import Collection

from .undefined import Undefined

from .exceptions import ModelNotFound
from .exceptions import ModelNotUpdated
from .exceptions import ModelNotDeleted
from .exceptions import ModelTargetNotSet
from .exceptions import DereferenceError


class Reference(dict):
    pass


class Model(object):
    mongo_collection = None
    id_type = bson.objectid.ObjectId
    id_attribute = "_id"

    def __init__(self, target=None):

        # meta
        self._projection
        self._operation
        self._result

        # attributes
        self.attributes = DelimitedDict()
        self.attributes_dereferenced = DelimitedDict()

        # state
        self.updates = DelimitedDict()
        self.original = DelimitedDict()
        self.target = DelimitedDict()

        # references
        self.references = DelimitedDict()

        # default attributes
        self.default_attributes = DelimitedDict()
        self.computed_attributes = DelimitedDict()

        # default projections
        self.default_find_projection = Projection()
        self.default_get_projection = Projection()

        # delete flag
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

    def __eq__(self, obj):
        return self.__class__ is obj.__class__ and self.attributes == obj.attributes

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def set_default_attributes(self):
        # default attributes get generated on get and save
        # they will not overwrite existing values
        for key, val in self.default_attributes.collapse().items():
            if not self.attributes.has(key):
                if callable(val):
                    self.set(key, val())
                else:
                    self.set(key, val)

    def set_computed_attributes(self, attributes):
        # computed attributes get generated on get and do not get saved
        # they will not overwrite existing values
        for key, val in self.computed_attributes.collapse().items():
            try:
                if not attributes.has(key):
                    if callable(val):
                        attributes.set(key, val())
                    else:
                        attributes.set(key, val)
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
        if self.default_find_projection and default:
            p.merge(self.default_find_projection)
        flattened_projection = p.flatten()
        if flattened_projection:
            self._projection = flattened_projection
            kwargs["projection"] = flattened_projection

        # find
        m = self.mongo_collection.find_one(**kwargs)
        if m is None:
            raise ModelNotFound(data=self.target.get())

        # post find hook
        self._post_find_hook(m)
        if callable(getattr(self, "post_find_hook", None)):
            self.post_find_hook()

        # dereference nested models
        if self.references and projection:
            self.dereference_models(projection=projection)

        return self

    def dereference_models(self, projection):

        for t in self.references.collapse().keys():

            # extract reference properties
            r_type = self.references[t]["type"]
            r_model = self.references[t]["model"]

            if "local_key" in self.references[t]:
                r_local_key = self.references[t]["local_key"]
            else:
                r_local_key = t

            if "foreign_key" in self.references[t]:
                r_foreign_key = self.references[t]["foreign_key"]
            else:
                if isinstance(r_model(), Model):
                    r_foreign_key = r_model.id_attribute
                else:
                    r_foreign_key = r_model.model.id_attribute

            # resolve this reference?
            if t in projection and \
                    (type(projection.get(t) is dict or
                     projection.get(t) == 2)):

                # setup kwargs
                kwargs = {}
                if type(projection.get(t)) is dict:
                    kwargs["projection"] = projection.get(t)

                # check t for dot notation syntax and if found
                # tunnel down through t and self.attributes

                # internal reference
                if t in self.attributes and self.attributes[t]:

                    # one to one : local, many_to_one : local
                    if r_type in ["one_to_one", "many_to_one"]:
                        try:
                            self.attributes[t] = r_model({
                                r_foreign_key: self.attributes[r_local_key]
                            }).find(**kwargs)

                        # dereference error
                        except:
                            error = DereferenceError(data={
                                "model": r_model.__name__,
                                "t": self.attributes[r_local_key]
                            })
                            self.attributes[t] = error

                    # one to many : local, many to many : local
                    elif r_type in ["one_to_many", "many_to_many"]:

                        collection = r_model().set_target(
                            self.attributes[r_local_key],
                            key=r_foreign_key
                        ).find(**kwargs)

                        # determine dereference errors
                        models_found = collection.get_ids()
                        for model_target in self.attributes[r_local_key]:
                            if model_target not in models_found:
                                error = DereferenceError(data={
                                    "model": r_model.__name__,
                                    "target": model_target
                                })
                                collection.add(error)

                        self.attributes[t] = collection

                # external reference
                elif self.has(r_local_key):

                    # one to one : foreign, many to one : foreign
                    if r_type in ["one_to_one", "many_to_one"]:

                        try:
                            self.attributes[t] = r_model({
                                r_foreign_key: self.get(r_local_key)
                            }).find(**kwargs)

                        # dereference error
                        except:
                            self.attributes[t] = None

                    # one to many : foreign
                    elif r_type in ["one_to_many", "many_to_many"]:

                        self.attributes[t] = r_model().set_target(
                            self.get(r_local_key),
                            key=r_foreign_key
                        ).find(**kwargs)

        return self

    # view attributes

    def ref(self, key=None, create=False):

        if type(key) is not DelimitedStr:
            key = DelimitedStr(key)

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

        if type(key) is not DelimitedStr:
            key = DelimitedStr(key)

        for i, needle in enumerate(key, 1):
            local_key = key[:i]

            if not self.attributes.has(local_key):
                return False

            elif i < len(key) and \
                    isinstance(self.attributes.ref(local_key),
                               (Model, Collection)):

                return self.attributes.ref(local_key).has(key=key[i:])

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
        attr = copy.deepcopy(self.attributes)
        self.set_computed_attributes(attr)
        haystack = attr

        # setup needle
        if type(key) is not DelimitedStr:
            key = DelimitedStr(key)

        for i, needle in enumerate(key, 1):
            if not haystack.has(needle):
                return Undefined()

            elif isinstance(haystack.ref(needle), (Model, Collection)):
                if projection and projection.has(needle):
                    projection = projection.clone(needle)
                return haystack.ref(needle).get(
                    key=key[i:],
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

                # no projection or include or missing from
                # exclusive projection
                if not projection or \
                        (not projection.has(local_key) and
                            projection.type == "exclusive") or \
                        (projection.has(local_key) and
                            projection.get(local_key) == 1):

                    data[k] = self.get(
                        key=local_key,
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
                        key=local_key,
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

    def unset(self, key, record=True, force=False, cleanup=False):

        try:

            if type(key) is not DelimitedStr:
                key = DelimitedStr(key)

            for i, needle in enumerate(key, 1):
                local_key = key[:i]

                if not self.attributes.has(local_key):
                    message = self.attributes.format_keyerror(needle, key)
                    raise KeyError(message)

                elif i < len(key) and \
                        isinstance(self.attributes.ref(local_key),
                                   (Model, Collection)):
                    return self.attributes.ref(local_key).unset(
                        key=key[i:],
                        record=record,
                        force=force
                    )

                elif i < len(key) and \
                        isinstance(self.attributes.ref(local_key),
                                   DereferenceError):

                    message = self.attributes.format_typeerror(
                        self.attributes.ref(local_key),
                        needle,
                        key
                    )
                    raise TypeError(message)

                elif i < len(key) and \
                        type(self.attributes.ref(local_key)) is not dict:

                    message = self.attributes.format_typeerror(
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
            if type(key) is not DelimitedStr:
                key = DelimitedStr(key)

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
        model.mongo_collection

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

    def cache_operation(self, type_, target=None, attributes=None, operators=None):
        self._operation = {
            "date": datetime.datetime.today(),
            "type": type_,
            "target": target,
            "attributes": attributes,
            "operators": operators
        }

    def cache_result(self, target=None, attributes=None):
        self._result = {
            "date": datetime.datetime.today(),
            "target": target,
            "attributes": attributes
        }

    def save(self, cascade=True, default=True):
        """ Saves model and nested model changes to the database

        Calls delete_one, update_one or insert_one for model.mongo_collection
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

            if callable(getattr(self, "pre_delete_hook", None)):
                self.pre_delete_hook()

            # run operation
            m = self.mongo_collection.find_one_and_delete(self.target.get())

            # cache operation
            self.cache_operation("delete", self.target.get())

            if m is None:
                raise ModelNotDeleted(data=self.target.get())

            # cache result
            self.cache_result()

            if cascade:
                self.reference_models(self.attributes)

            if callable(getattr(self, "post_delete_hook", None)):
                self.post_delete_hook()

        # update
        elif self.target and self.updates:

            if callable(getattr(self, "pre_update_hook", None)):
                self.pre_update_hook()

            # run operation
            updates = self.flatten_updates(cascade=cascade)
            m = self.mongo_collection.find_one_and_update(
                self.target.get(),
                updates
            )

            # cache operation
            self.cache_operation("update", self.target.get(), None, updates)

            if m is None:
                raise ModelNotUpdated(data=self.target.get())

            # cache result
            self.cache_result(self.target.get(), m)

            self._post_update_hook()
            if callable(getattr(self, "post_update_hook", None)):
                self.post_update_hook()

        # insert
        elif not self.target:

            self._pre_insert_hook(default=default)

            if callable(getattr(self, "pre_insert_hook", None)):
                self.pre_insert_hook()

            # cache operation
            self.cache_operation("insert", None, self.attributes.get(), None)

            m = self.mongo_collection.insert_one(
                self.reference_models(self.attributes, cascade)
            )

            # cache result
            self.cache_result(self.target.get(), self.attributes.get())
 
            self._post_insert_hook()
            if callable(getattr(self, "post_insert_hook", None)):
                self.post_insert_hook()

        # cascade save to nested models
        elif cascade:
            self.reference_models(self.attributes, cascade)

        return self

    def flatten_updates(self, cascade=True):
        flattened = {}
        for method, updates in self.reference_models(self.updates).items():
            flattened[method] = DelimitedDict(updates).collapse()
        return flattened

    def reference_models(self, data, cascade=True):
        referenced = type(data)()
        for k, v in data.items():

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

            # container
            elif isinstance(v, dict):
                referenced[k] = self.reference_models(v, cascade)

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
