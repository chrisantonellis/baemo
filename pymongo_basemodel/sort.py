
from collections import OrderedDict

from .dot_notation import OrderedDotNotationContainer
from .exceptions import SortMalformed


class Sort(OrderedDotNotationContainer):

    def __call__(self, data=None, expand=True):
        if data is not None:
            temp = OrderedDotNotationContainer(data=data, expand=expand)
            self.validate_sort(temp.ref())

        super().__call__(data, expand=expand)

    def set(self, key, value): 
        temp = OrderedDotNotationContainer(self.__dict__)
        temp.set(key, value)
        self.validate_sort(temp.__dict__)

        return super().set(key, value)

    def merge(self, sort):
        if type(sort) is not Sort:
            sort = Sort(sort)

        temp = OrderedDotNotationContainer(self.__dict__)
        temp.merge(sort.__dict__)
        self.validate_sort(temp.__dict__)

        return super().merge(sort)

    def flatten(self, remove=None):
        return self.flatten_sort(self, remove=remove)

    @classmethod
    def flatten_sort(cls, sort, remove=None):
        c = sort.collapse()
        if remove is not None:
            for sep_k in remove.collapse().keys():
                for col_k in c.keys():
                    if col_k.startswith(sep_k):
                        del c[col_k]
                        break
        return list(c.items())

    @classmethod
    def validate_sort(cls, data):
        if type(data) is not OrderedDict:
            data = OrderedDict(data)
        
        data = cls.collapse_dot_notation(data)
        for t in data.items():
            if t[1] not in [-1, 1] and type(t[1]) is not OrderedDict:
                raise SortMalformed(t[0], t[1])

        return True
