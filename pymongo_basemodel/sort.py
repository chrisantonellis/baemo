
from collections import OrderedDict

from .dot_notation import OrderedDotNotationContainer
from .exceptions import SortMalformed


class Sort(OrderedDotNotationContainer):

    def __call__(self, data=None, expand=True):
        if data is not None:
            if type(data) is tuple:
                data = OrderedDict([(data)])
            elif type(data) is list and all(type(v) is tuple for v in data):
                data = OrderedDict(data)

            temp = OrderedDotNotationContainer(data=data, expand=expand)
            self.validate_sort(temp.ref())

        super().__call__(data=data, expand=expand)

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

    # def collapse(self):
    #     return self.collapse_dot_notation(self.__dict__)

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
            if t[1] not in [-1, 1] and type(t[1]) not in[dict, OrderedDict]:
                raise SortMalformed(t[0], t[1])

        return True

    @classmethod
    def collapse_dot_notation(cls, data, parent_key=None):
        items = []
        for key, val in data.items():
            new_key = "%s.%s" % (parent_key, key) if parent_key else key
            if type(val) is OrderedDict and not \
                    set(val.keys()) & set(["$meta", "$natural"]):
                collapsed = cls.collapse_dot_notation(val, new_key)
                items.extend(collapsed.items())
            else:
                items.append((new_key, val))
        return dict(items)
