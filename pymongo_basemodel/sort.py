
import copy

from .dot_notation import DotNotationContainer
from .exceptions import SortMalformed


class Sort(DotNotationContainer):

  def __init__(self, data=None, expand=True):
    if data:
      self.__call__(data, expand)
    super().__init__()

  def __call__(self, data={}, expand=True):
    if expand:
      data = self.expand_dot_notation(data)
    self.validate_sort(data)
    self.__dict__ = data

  def set(self, key, value):
    try:
      cache = copy.deepcopy(self.__dict__)
      super().set(key, value)
      self.validate()
      return self
    except:
      self(cache)
      raise

  def merge(self, sort):
    if type(sort) is not Sort:
      sort = Sort(sort)

    return super().merge(sort)

  def validate(self):
    self.validate_sort(self.__dict__)
    return self

  @classmethod
  def validate_sort(cls, data):
    for k,v in data.items():

      if v not in [-1, 1] and type(v) is not dict:
        raise SortMalformed(k, v)

      if type(v) is dict:
        try:
          cls.validate_sort(v)
        except SortMalformed as e:
          raise SortMalformed("{}.{}".format(k, e.key), e.value)

    return True
