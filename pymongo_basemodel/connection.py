
from .exceptions import ConnectionNotSet


class Connections(object):

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
