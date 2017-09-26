
"""
baemo.entity
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

    def __new__(cls, name, model_options=None, collection_options=None):
        from .model import Model
        from .collection import Collection

        entity_definition = {}

        entity_config = [{
            "type": "model",
            "bases": [Model, EntityMeta],
            "options": model_options
        }, {
            "type": "collection",
            "bases": [Collection, EntityMeta],
            "options": collection_options
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
                dict()
            )

            # for each base class in reverse order, cache and merge dict
            # type attributes NOTE: attribute type will be what it was
            # when first encountered while scanning base classes, this is
            # important because attributes set in model/collection options
            # as dicts at entity creation time must become the type
            # appropriate for the attribute to function correctly
            # Sort for sorts, References for references etc.
            bases_attribute_cache = {}
            for base in reversed(member_config["bases"]):

                # for each attribute in base class
                for key in dir(base):
                    attr = getattr(base, key)

                    # determine correct type by checking type on base model
                    if isinstance(attr, (dict, OrderedDict, DelimitedDict)):

                        if key not in bases_attribute_cache:
                            bases_attribute_cache[key] = attr.__class__()

                        bases_attribute_cache[key] = DelimitedDict._merge(
                            attr,
                            bases_attribute_cache[key]
                        )

            # add merged base attribute to options
            if bases_attribute_cache:

                if member_config["options"] is None:
                    member_config["options"] = {}

                for key, value in bases_attribute_cache.items():

                    # overwrite
                    if key not in member_config["options"]:
                        member_config["options"][key] = value


                    # merge
                    # if key not in member_config["options"]:
                    #     member_config["options"][key] = value.__class__()
                    #
                    # # overwrite values inherited with values in options
                    # member_config["options"][key] = DelimitedDict._merge(
                    #     value,
                    #     member_config["options"][key]
                    # )

                    # cast back to correct type
                    # member_config["options"][key] = value.__class__(member_config["options"][key])

            # # if there are no options, continue
            # if member_config["options"] is None:
            #     continue

            # add options attributes to entity member class
            for key, value in member_config["options"].items():

                # check against type of attribute in Model or Collection base
                # for attributes passed only as options and
                if hasattr(member_config["bases"][-2], key):
                    attr = getattr(member_config["bases"][-2], key)

                    if isinstance(attr, (dict, OrderedDict, DelimitedDict)):
                        if not isinstance(value, attr.__class__):
                            value = attr.__class__(value)

                # set attribute on entity member class
                setattr(entity_definition[member_config["type"]], key, value)

        # connect model and collection via entity definition
        entity_definition["model"].__entity__ = entity_definition
        entity_definition["collection"].__entity__ = entity_definition

        # set entity member in Entities cache
        Entities.set(name, entity_definition)

        return entity_definition["model"], entity_definition["collection"]
