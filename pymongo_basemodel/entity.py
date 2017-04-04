
from .delimited import DelimitedDict

from .model import Model
from .collection import Collection

cache = {}


def get_entity(name, type_):
    global cache

    if name not in cache:
        raise Exception("entity not registered: {}".format(name))
    else:
        return cache[name][type_]


class EntityMeta(object):
    pass


class Entity(object):

    def __new__(self, name, m_options=None, c_options=None):
        global cache

        class NewModel(Model, EntityMeta):
            pass

        class NewCollection(Collection, EntityMeta):
            pass

        NewModel.collection = NewCollection
        NewCollection.model = NewModel

        entities = [{
            "class": NewModel,
            "options": m_options
        }, {
            "class": NewCollection,
            "options": c_options
        }]

        for entity in entities:
            if entity["options"] is None:
                continue

            for k, v in entity["options"].items():
                default_key = "_{}".format(k)
                if not hasattr(entity["class"], default_key):
                    raise Exception("invalid option '{}' for entity '{}'".format(default_key, name))

                existing = getattr(entity["class"], default_key)
                if isinstance(existing, DelimitedDict):
                    v = existing.__class__(v)

                setattr(entity["class"], default_key, v)

        cache[name] = {
            "model": NewModel,
            "collection": NewCollection
        }

        return NewModel, NewCollection
