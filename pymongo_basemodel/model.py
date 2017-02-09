
import bson
import copy

from .dot_notation import DotNotationString
from .dot_notation import DotNotationContainer

from .projection import Projection

from .collection import Collection

from .exceptions import ModelNotFound
from .exceptions import ModelNotUpdated
from .exceptions import ModelNotDeleted
from .exceptions import ModelTargetNotSet
from .exceptions import RelationshipResolutionError


class NestedDict(dict):
    """ represents dict set in nested data that potentially overwrites other
    nested data on assignment. Disallows collapsing contained data to dot
    notation syntax by not presenting itself as type dict to avoid losing
    intention of overwriting when saving to the db """


class Undefined(object):
    # model.get() return value soft error

    def __str__(self):
        return "undefined"

    def __bool__(self):
        return False


class Model(object):
    id_attribute = "_id"
    pymongo_collection = None

    def __init__(self, target=None):

        # attributes
        self.attributes = DotNotationContainer()

        # state
        self.updates = DotNotationContainer()
        self.original = DotNotationContainer()
        self.target = DotNotationContainer()

        # relationships
        self.relationships = DotNotationContainer()

        # default attributes
        self.default_attributes = DotNotationContainer()
        self.computed_attributes = DotNotationContainer()

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
        if callable(getattr(self, "post_find_hook", None)):
            self.post_find_hook()

        # dereference nested models
        if self.relationships and projection:
            self.dereference_nested_models(projection=projection)

        return self

    def dereference_nested_models(self, projection):

        for target in self.relationships.keys():

            # adjust target for dot notation relationships
            while not hasattr(self.relationships[target], "type"):
                target_keys = [k for k in self.relationships[target].keys()]
                target = "{}.{}".format(target, target_keys[0])

            # extract relationship properties
            r_type = self.relationships[target]["type"]
            r_model = self.relationships[target]["model"]

            if "local_key" in self.relationships[target]:
                r_local_key = self.relationships[target]["local_key"]
            else:
                r_local_key = target

            if "foreign_key" in self.relationships[target]:
                r_foreign_key = self.relationships[target]["foreign_key"]
            else:
                if isinstance(r_model(), Model):
                    r_foreign_key = r_model.id_attribute
                else:
                    r_foreign_key = r_model.model.id_attribute

            # resolve this relationship?
            if target in projection and \
                    (type(projection.get(target) is dict or
                     projection.get(target) == 2)):

                # check target for dot notation syntax and if found
                # tunnel down through target and self.attributes

                # internal relationship
                if target in self.attributes and self.attributes[target]:

                    # one to one : local, many_to_one : local
                    if r_type in ["one_to_one", "many_to_one"]:

                        try:

                            # projection
                            if type(projection.get(target)) is dict:
                                self.attributes[target] = r_model({
                                    r_foreign_key: self.attributes[r_local_key]
                                }).find(projection=projection.get(target))

                            # no projection
                            else:
                                self.attributes[target] = r_model({
                                    r_foreign_key: self.attributes[r_local_key]
                                }).find()

                        # relationship resolution error
                        except:
                            error = RelationshipResolutionError(data={
                                "model": r_model.__name__,
                                "target": self.attributes[r_local_key]
                            })
                            self.attributes[target] = error

                    # one to many : local, many to many : local
                    elif r_type in ["one_to_many", "many_to_many"]:

                        # projection
                        if type(projection.get(target)) is dict:

                            collection = r_model().set_target(
                                self.attributes[r_local_key],
                                key=r_foreign_key
                            ).find(projection=projection.get(target))

                        # no projection
                        else:

                            collection = r_model().set_target(
                                self.attributes[r_local_key],
                                key=r_foreign_key
                            ).find()

                        # determine relationship resolution errors
                        models_found = collection.get_ids()
                        for model_target in self.attributes[r_local_key]:
                            if model_target not in models_found:
                                error = RelationshipResolutionError(data={
                                    "model": r_model.__name__,
                                    "target": model_target
                                })
                                collection.add(error)

                        self.attributes[target] = collection

                # external relationship
                elif self.has(r_local_key):

                    # one to one : foreign, many to one : foreign
                    if r_type in ["one_to_one", "many_to_one"]:
                        try:

                            # projection
                            if type(projection.get(target)) is dict:
                                self.attributes[target] = r_model({
                                    r_foreign_key: self.get(r_local_key)
                                }).find(projection=projection.get(target))

                            # no projection
                            else:
                                self.attributes[target] = r_model({
                                    r_foreign_key: self.get(r_local_key)
                                }).find()

                        # relationship resolution error
                        except:
                            self.attributes[target] = None

                    # one to many : foreign
                    elif r_type in ["one_to_many", "many_to_many"]:

                        # projection
                        if type(projection.get(target)) is dict:
                            self.attributes[target] = r_model().set_target(
                                self.get(r_local_key),
                                key=r_foreign_key
                            ).find(projection=projection.get(target))

                        # no projection
                        else:
                            self.attributes[target] = r_model().set_target(
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
        if type(key) is not DotNotationString:
            key = DotNotationString(key)

        for i, needle in enumerate(key, 1):
            if not haystack.has(needle):
                return Undefined()

            elif isinstance(haystack.ref(needle), (Model, Collection)):
                if projection and projection.has(needle):
                    projection = projection.spawn(needle)
                return haystack.ref(needle).get(
                    key=key[i:],
                    projection=projection,
                    setup=True
                )

            elif isinstance(haystack.ref(needle), BaseException):
                return haystack.ref(needle).get()

            # return haystack as dot notation container
            elif isinstance(haystack.ref(needle), dict):
                haystack = haystack.spawn(needle)

            # return value
            else:
                haystack = haystack.ref(needle)

        if type(haystack) in [dict, DotNotationContainer]:
            data = {}
            for k, v in haystack.items():
                local_key = ".".join(key.keys + [k]) if key else k

                # no projection or include or missing from
                # exclusive projection
                if not projection or \
                        (not projection.has(local_key) and
                            projection.get_type() == "exclusive") or \
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

            if callable(getattr(self, "pre_delete_hook", None)):
                self.pre_delete_hook()

            m = self.pymongo_collection.delete_one(self.target.get())
            if not m.deleted_count:
                raise ModelNotDeleted(data=self.target.get())

            if cascade:
                self.reference_nested_models()

            if callable(getattr(self, "post_delete_hook", None)):
                self.post_delete_hook()

        # update
        elif self.target and self.updates:

            if callable(getattr(self, "pre_update_hook", None)):
                self.pre_update_hook()

            m = self.pymongo_collection.update_one(
                self.target.get(),
                self.flatten_updates(cascade=cascade)
            )

            if not m.modified_count:
                raise ModelNotUpdated(data=self.target.get())

            self._post_update_hook()
            if callable(getattr(self, "post_update_hook", None)):
                self.post_update_hook()

        # insert
        elif not self.target:

            self._pre_insert_hook(default=default)

            if callable(getattr(self, "pre_insert_hook", None)):
                self.pre_insert_hook()

            m = self.pymongo_collection.insert_one(
                self.reference_nested_models(cascade=cascade)
            )

            self._post_insert_hook()
            if callable(getattr(self, "post_insert_hook", None)):
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
