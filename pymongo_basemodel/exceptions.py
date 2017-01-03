
__doc__ = ""
__all__ = [
  "BaseException",
  "ModelNotCreated",
  "ModelNotFound",
  "ModelNotUpdated",
  "ModelNotDeleted",
  "ModelTargetNotSet",
  "ModelNotChanged",
  "CollectionModelClassMismatch",
  "CollectionModelNotPresent",
  "RelationshipResolutionError",
  "PymongoCollectionNotSet",
  "ProjectionMalformed",
  "ProjectionTypeMismatch"
]

# base exception

class BaseException(Exception):
  message = "pymongo_basemodel error"
  data = None

  def __init__(self, message = None, data = None):
    if message:
      self.message = message
    if data:
      self.data = data
      
    super().__init__(self.message)

  def get(self):
    data = {
      "message": self.message
    }

    if self.data:
      data["data"] = self.data # yo dawg

    return data

# model

class ModelNotCreated(BaseException):
  message = "Model not created"

class ModelNotFound(BaseException):
  message = "Model not found"

class ModelNotUpdated(BaseException):
  message = "Model not updated"

class ModelNotDeleted(BaseException):
  message = "Model not deleted"

class ModelTargetNotSet(BaseException):
  message = "Model target not set"

class ModelNotChanged(BaseException):
  message = "Model not changed"

# collection

class CollectionModelClassMismatch(BaseException):
  message = "Collection model class mismatch"

class CollectionModelNotPresent(BaseException):
  message = "Collection model not present"

# relationship

class RelationshipResolutionError(BaseException):
  message = "Relationship resolution error"

class PymongoCollectionNotSet(BaseException):
  message = "Pymongo collection not set on model"

# projection

class ProjectionMalformed(BaseException):
  message = "Projection malformed, invalid value '%s' for key '%s'"
  
  def __init__(self, key, value, **kwargs):
    self.key = key
    self.value = value
    self.message = self.message % (value, key)
    super().__init__(**kwargs)

class ProjectionTypeMismatch(BaseException):
  message = "Projection type mismatch, cannot mix include and exclude projections"
