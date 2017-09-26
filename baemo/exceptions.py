
# base

class BasemodelException(Exception):
    message = "baemo error"
    args = []
    data = None

    def __init__(self, *args, message=None, data=None):
        if len(args) > 0:
            self.args = args

        if message:
            self.message = message
        self.message = self.message.format(*self.args)

        if data:
            self.data = data

        super().__init__(self.message)

    def get(self):
        data = {"message": self.message}
        if self.data is not None:
            data["data"] = self.data  # yo dawg
        return data


# connection


class ConnectionNotSet(BasemodelException):
    message = "Connection '{}' not set"


# entity


class EntityNotSet(BasemodelException):
    message = "Entity '{}' not set"


# model


class ModelNotFound(BasemodelException):
    message = "Model not found"


class ModelNotUpdated(BasemodelException):
    message = "Model not updated"


class ModelNotDeleted(BasemodelException):
    message = "Model not deleted"


class ModelTargetNotSet(BasemodelException):
    message = "Model target not set"


# collection


class CollectionModelClassMismatch(BasemodelException):
    message = "Collection model class mismatch"


class CollectionModelNotPresent(BasemodelException):
    message = "Collection model not present"


# references


class DereferenceError(BasemodelException):
    message = "Dereference error"


class ReferencesMalformed(BasemodelException):
    message = "Reference malformed for key '{}'"


# projection


class ProjectionTypeMismatch(BasemodelException):
    message = "Projection type mismatch, cannot merge include and exclude projections"


class ProjectionMalformed(BasemodelException):
    message = "Projection malformed, invalid value '{}' for key '{}'"


# sort


class SortMalformed(BasemodelException):
    message = "Sort malformed, invalid value '{}' for key '{}'"
