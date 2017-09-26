
"""
baemo.connection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module defines the Connections interface that allows for caching of
MongoDB database connections and retrieval of connections by name.
"""

from .exceptions import ConnectionNotSet


class Connections(object):
    """ An interface that allows for caching of MongoDB database
    connections and retrieval of connections by name. The first connection set
    will become the default connection and can be retrieved by calling
    `Connections.get()` without a `name` argument. The default connection can be
    changed by calling `Connections.set()` with the keyword argument `default`
    set to True.
    """

    cache = {}
    default = None

    @classmethod
    def set(cls, name, connection, default=False):
        Connections.cache[name] = connection
        if not Connections.default or default:
            Connections.default = connection

    @classmethod
    def get(cls, name=None, collection=None):
        if name is None:
            if Connections.default is None:
                raise ConnectionNotSet("Default")
            else:
                connection = Connections.default

        else:
            if name not in Connections.cache:
                raise ConnectionNotSet(name)
            else:
                connection = Connections.cache[name]

        if collection is not None:
            connection = connection[collection]

        return connection
