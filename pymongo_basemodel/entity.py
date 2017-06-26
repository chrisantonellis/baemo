
"""
pymongo_basemodel.entity
~~~~~~~~~~~~~~~~~~~~~~~~
This module defines the Entity and Entities interfaces. Entities is a cache of
Entity groups that allows for retrieval by name. Entity is a metaclass that
creates Model and Collection classes.
"""

from collections import OrderedDict

from .delimited import DelimitedDict
from .projection import Projection
from .references import References
from .sort import Sort
from .exceptions import EntityNotSet


class EntityMeta(object):
    pass


class Entities(object):

    cache = {}

    @classmethod
    def set(cls, name, entity):
        Entities.cache[name] = entity

    @classmethod
    def get(cls, name):
        if name not in Entities.cache:
            raise EntityNotSet(name)
        else:
            return Entities.cache[name]


class Entity(type):

    def __new__(cls, name, m_options=None, c_options=None):
        from .model import Model
        from .collection import Collection

        entity_definition = {}

        entity_config = [{
            "type": "model",
            "bases": [Model, EntityMeta],
            "options": m_options
        }, {
            "type": "collection",
            "bases": [Collection, EntityMeta],
            "options": c_options
        }]

        for member_config in entity_config:

            # pre handle configuration options
            if member_config["options"] is not None:

                # base classes
                if "bases" in member_config["options"]:
                    bases = member_config["options"]["bases"]
                    del member_config["options"]["bases"]
                    if type(bases) is not list:
                        bases = [bases]
                    member_config["bases"] = bases + member_config["bases"]

            # create entity member class
            entity_definition[member_config["type"]] = type(
                "{}{}".format(name, member_config["type"].title()),
                tuple(member_config["bases"]),
                {"__entity__": entity_definition}
            )

            # merge base class attributes in order of inheritance
            bases_attribute_cache = {}
            for base in reversed(member_config["bases"]):
                for key in dir(base):

                    # capture mergable types dict and OrderedDict
                    if isinstance(getattr(base, key), (dict, OrderedDict)):

                        if key not in bases_attribute_cache:
                            bases_attribute_cache[key] = {}

                        bases_attribute_cache[key] = DelimitedDict._merge(
                            getattr(base, key),
                            bases_attribute_cache[key]
                        )

            # add merged base attributes to options
            for key, value in bases_attribute_cache.items():
                if key not in member_config["options"]:
                    member_config["options"][key] = value

            # if there are no options, continue
            if member_config["options"] is None:
                continue

            # add options attributes to entity member class
            for key, value in member_config["options"].items():

                # cast to correct type based on type in base entity member class
                if member_config["type"] == "model":
                    if hasattr(Model, key):
                        if isinstance(getattr(Model, key), (DelimitedDict, Projection, References)):
                            value = getattr(Model, key).__class__(value)

                elif member_config["type"] == "collection":
                    if hasattr(Collection, key):
                        if isinstance(getattr(Collection, key), (DelimitedDict, Projection, Sort)):
                            value = getattr(Collection, key).__class__(value)

                # set attribute on entity member class
                setattr(entity_definition[member_config["type"]], key, value)

        # set entity member in Entities cache
        Entities.set(name, entity_definition)

        return entity_definition["model"], entity_definition["collection"]
