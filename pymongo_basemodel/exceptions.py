
# base


class BaseException(Exception):
    message = "pymongo_basemodel error"
    data = None

    def __init__(self, message=None, data=None):
        if message:
            self.message = message
        if data:
            self.data = data
        super().__init__(self.message)

    def get(self):
        data = {}
        data["message"] = self.message

        if self.data is not None:
            data["data"] = self.data  # yo dawg
        return data


# connection 


class ConnectionNotSet(BaseException):
    message = "Connection '{}' not set"

    def __init__(self, connection, **kwargs):
        self.connection = connection
        self.message = self.message.format(connection)
        super().__init__(**kwargs)


# entity


class EntityNotSet(BaseException):
    message = "Entity '{}' not set"

    def __init__(self, name, **kwargs):
        self.name = name
        self.message = self.message.format(name)
        super().__init__(**kwargs)


# model


class ModelNotFound(BaseException):
    message = "Model not found"


class ModelNotUpdated(BaseException):
    message = "Model not updated"


class ModelNotDeleted(BaseException):
    message = "Model not deleted"


class ModelTargetNotSet(BaseException):
    message = "Model target not set"


# collection


class CollectionModelClassMismatch(BaseException):
    message = "Collection model class mismatch"


class CollectionModelNotPresent(BaseException):
    message = "Collection model not present"


# references


class DereferenceError(BaseException):
    message = "Dereference error"


# projection


class ProjectionTypeMismatch(BaseException):
    message = ("Projection type mismatch, cannot merge include and exclude "
               "projections")


class ProjectionMalformed(BaseException):
    message = "Projection malformed, invalid value '{}' for key '{}'"

    def __init__(self, key, value, **kwargs):
        self.key = key
        self.value = value
        self.message = self.message.format(value, key)
        super().__init__(**kwargs)


# sort


class SortMalformed(BaseException):
    message = "Sort malformed, invalid value '{}' for key '{}'"

    def __init__(self, key, value, **kwargs):
        self.key = key
        self.value = value
        self.message = self.message.format(value, key)
        super().__init__(**kwargs)
