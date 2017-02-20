
import pymongo
import copy

from .delimited import DelimitedDict

from .projection import Projection

from .sort import Sort

from .exceptions import ModelTargetNotSet
from .exceptions import DereferenceError
from .exceptions import CollectionModelClassMismatch
from .exceptions import CollectionModelNotPresent


class Collection(object):
    model = None

    def __init__(self, target=None):

        # collection
        self.collection = []

        # state
        self.target = DelimitedDict()

        # default sort
        self.default_sort = Sort()

        # default limit
        self.default_limit = None

        # default projections
        self.default_find_projection = Projection()
        self.default_get_projection = Projection()

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

    def __setitem__(self, index, item):
        if not isinstance(item, self.model):
            raise CollectionModelClassMismatch
        self.collection[index] = item
        return True

    def __getitem__(self, index):
        return self.collection[index]

    def __delitem__(self, index):
        del self.collection[index]
        return True

    def __reversed__(self):
        return reversed(self.collection)

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
             default_model_projection=False, sort=None, default_sort=True,
             limit=None, skip=None):

        if callable(getattr(self, "pre_find_hook", None)):
            self.pre_find_hook()

        find_kwargs = {}

        # filter
        if self.target:
            find_kwargs["filter"] = self.target.get()

        # projection
        p = Projection()
        if projection is not None:
            p.merge(projection)
        if self.default_find_projection and default_projection:
            p.merge(self.default_find_projection)
        if default_model_projection:
            model_default = self.model().default_find_projection.get()
            if model_default:
                p.merge(model_default)
        flattened_projection = p.flatten()
        if flattened_projection:
            find_kwargs["projection"] = flattened_projection

        # sort
        s = Sort()
        if sort is not None:
            s.merge(sort)
        if self.default_sort and default_sort:
            s.merge(self.default_sort)
        flattened_sort = s.flatten(remove=self.model().references)
        if flattened_sort:
            find_kwargs["sort"] = flattened_sort

        # skip
        if skip is not None:
            find_kwargs["skip"] = skip

        # limit
        l = None
        if limit:
            l = limit
        elif self.default_limit:
            l = self.default_limit
        if l is not None:
            find_kwargs["limit"] = l

        # find
        collection = self.model.mongo_collection.find(**find_kwargs)

        for m in collection:
            model = self.model()
            if callable(getattr(model, "pre_find_hook", None)):
                model.pre_find_hook()
            model._post_find_hook(m)
            if callable(getattr(model, "post_find_hook", None)):
                model.post_find_hook()
            if model.references and projection:
                model.dereference_models(projection=projection)
            self.collection.append(model)

        if callable(getattr(self, "post_find_hook", None)):
            self.post_find_hook()

        return self

    # view attributes

    def ref(self, **kwargs):
        return [m.ref(**kwargs) for m in self]

    def has(self, key):
        return [m.has(key=key) for m in self]

    # key, projection, default, model_default

    def get(self, key=None, projection=None, default=True,
            model_default=False):
        p = Projection()
        if default and self.default_get_projection:
            p.merge(self.default_get_projection)
        if projection:
            if type(projection) is not Projection:
                projection = Projection(projection)
            p.merge(projection)

        elif not projection and self.default_get_projection and default:
            projection = self.default_get_projection

        data = []
        for m in self:
            data.append(m.get(key=key, projection=p, default=model_default))
        return data

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

        if callable(getattr(self, "pre_modify_hook", None)):
            self.pre_modify_hook()

        requests = []

        for m in self:

            # delete
            if m._delete:
                if not m.target:
                    raise ModelTargetNotSet

                if callable(getattr(m, "pre_delete_hook", None)):
                    m.pre_delete_hook()

                requests.append(pymongo.DeleteOne(m.target.get()))

                if cascade:
                    m.reference_models(m.attributes, cascade)

            # update
            elif m.target and m.updates:

                if callable(getattr(m, "pre_update_hook", None)):
                    m.pre_update_hook()

                requests.append(pymongo.UpdateOne(
                                    m.target.get(),
                                    m.flatten_updates(cascade=cascade))
                                )

            # insert
            elif not m.target:
                m._pre_insert_hook()
                if callable(getattr(m, "pre_insert_hook", None)):
                    m.pre_insert_hook()

                requests.append(pymongo.InsertOne(
                                    m.reference_models(
                                        m.attributes,
                                        cascade=cascade
                                    )
                                ))

            elif cascade:
                m.reference_models(
                    m.attributes,
                    cascade=cascade
                )

        # execute requests with bulk write
        if requests:
            self.model.mongo_collection.bulk_write(requests)

        for m in self:

            # delete
            if m._delete and m.target:
                if callable(getattr(m, "post_delete_hook", None)):
                    m.post_delete_hook()

            # update
            elif m.target:
                m._post_update_hook()
                if callable(getattr(m, "post_update_hook", None)):
                    m.post_update_hook()

            # insert
            else:
                m._post_insert_hook()
                if callable(getattr(m, "post_insert_hook", None)):
                    m.post_insert_hook()

        if callable(getattr(self, "post_modify_hook", None)):
            self.post_modify_hook()

        return self

    # update collection members

    def add(self, m):
        if type(m) not in [self.model, DereferenceError]:
            raise CollectionModelClassMismatch
        else:
            self.collection.append(m)

    def remove(self, m):
        if m not in self:
            raise CollectionModelNotPresent
        else:
            self.collection.remove(m)
