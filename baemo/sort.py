
from collections import OrderedDict

from .delimited import DelimitedOrderedDict
from .exceptions import SortMalformed


class SortOperator(OrderedDict):
    pass


class Sort(DelimitedOrderedDict):

    def __call__(self, data=None, expand=True):
        if type(data) is list:
            data = OrderedDict(data)
        elif type(data) is tuple:
            data = OrderedDict([data])

        super().__call__(data=data, expand=expand)
        self.wrap()
        self.validate()

    def set(self, key, value):
        super().set(key, value)
        self.validate()

    def merge(self, data):
        if type(data) is tuple:
            data = OrderedDict([data])
        elif type(data) is list:
            data = OrderedDict(data)

        return super().merge(data)

    def update(self, data):
        if type(data) is tuple:
            data = OrderedDict([data])
        elif type(data) is list:
            data = OrderedDict(data)

        super().update(data)
        self.validate()

    def wrap(self):
        self.__dict__ = self._wrap(self.__dict__)

    def flatten(self, remove=None):
        return self._flatten(self, remove=remove)

    def validate(self):
        return self._validate(self.__dict__)

    @classmethod
    def _wrap(cls, data):
        for k, v in data.items():

            if isinstance(v, (cls.container, Sort)):
                # if set(v.keys()) & set(["$meta", "$natural"]):
                if k in ["$meta", "$natural"]:
                    data[k] = SortOperator(v)
                else:
                    data[k] = cls._wrap(v)

        return data

    @classmethod
    def _flatten(cls, sort, remove=None):
        """ requires sort or something that can be collapsed """

        c = sort.collapse()
        if remove is not None:
            for sep_k in remove.collapse().keys():
                for col_k in c.keys():
                    if col_k.startswith(sep_k):
                        del c[col_k]
                        break
        return list(c.items())

    @classmethod
    def _validate(cls, data):
        data = cls._collapse_delimited_notation(data)
        for t in data.items():
            if t[1] not in [-1, 1] and type(t[1]) not in [OrderedDict, SortOperator]:
                raise SortMalformed(t[0], t[1])
        return True
