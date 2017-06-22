
"""
pymongo_basemodel.entity
~~~~~~~~~~~~~~~~~~~~~~~~
This module defines the Entity and Entities interfaces. Entities is a cache of
Entity groups that allows for retrieval by name. Entity is a metaclass that
creates Model and Collection classes.
"""

from collections import OrderedDict

from .delimited import DelimitedDict
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

        entity_config = [{
            "type": "model",
            "bases": [Model, EntityMeta],
            "options": m_options
        }, {
            "type": "collection",
            "bases": [Collection, EntityMeta],
            "options": c_options
        }]

        entity = {}
        for member_config in entity_config:

            if member_config["options"] is not None:

                # base classes
                if "bases" in member_config["options"]:
                    bases = member_config["options"]["bases"]
                    del member_config["options"]["bases"]

                    if type(bases) is not list:
                        bases = [bases]

                    member_config["bases"] = bases + member_config["bases"]

            # create entity member class
            entity[member_config["type"]] = type(
                name + member_config["type"].title(), # <name>Model etc
                tuple(member_config["bases"]),
                {"__entity__": entity}
            )

            # cache base class attribtues in order of inheritance
            bases_attribute_cache = {}
            for base in reversed(member_config["bases"]):
                for key in dir(base):

                    if isinstance(getattr(base, key), dict):

                        if key not in bases_attribute_cache:
                            bases_attribute_cache[key] = {}

                        bases_attribute_cache[key] = DelimitedDict._merge(
                            getattr(base, key),
                            bases_attribute_cache[key]
                        )

                    elif isinstance(getattr(base, key), OrderedDict):

                        if key not in bases_attribute_cache:
                            bases_attribute_cache[key] = OrderedDict()

                        bases_attribute_cache[key] = DelimitedDict._merge(
                            getattr(base, key),
                            bases_attribute_cache[key]
                        )

            # add merged base attributes to options
            for key, value in bases_attribute_cache.items():
                if key not in member_config["options"]:
                    member_config["options"][key] = value

            if member_config["options"] is None:
                continue

            # add options attributes to entity member class
            for key, value in member_config["options"].items():

                # convert to correct type if necessary
                if isinstance(value, (dict, OrderedDict)):
                    temp_instance = entity[member_config["type"]]()
                    if hasattr(temp_instance, key):
                        value = getattr(temp_instance, key).__class__(value)

                setattr(entity[member_config["type"]], key, value)

        Entities.set(name, entity)

        return entity["model"], entity["collection"]
