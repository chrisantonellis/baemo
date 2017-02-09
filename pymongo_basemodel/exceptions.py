
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


class ModelNotFound(BaseException):
    message = "Model not found"


class ModelNotUpdated(BaseException):
    message = "Model not updated"


class ModelNotDeleted(BaseException):
    message = "Model not deleted"


class ModelTargetNotSet(BaseException):
    message = "Model target not set"


class CollectionModelClassMismatch(BaseException):
    message = "Collection model class mismatch"


class CollectionModelNotPresent(BaseException):
    message = "Collection model not present"


class RelationshipResolutionError(BaseException):
    message = "Relationship resolution error"


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


class SortMalformed(BaseException):
    message = "Sort malformed, invalid value '{}' for key '{}'"

    def __init__(self, key, value, **kwargs):
        self.key = key
        self.value = value
        self.message = self.message.format(value, key)
        super().__init__(**kwargs)
