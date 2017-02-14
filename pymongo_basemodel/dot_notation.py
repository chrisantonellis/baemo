
import copy

from collections import OrderedDict


# class DelimiterNotationString(object):
#     pass

# class DelimiterNotationContainer(object):
#     pass

# class OrderedDelimiterNotationContainer(object):
#     pass


class DotNotationString(object):
    delimiter = "."

    def __init__(self, string=None, delimiter=None):
        self.keys = []
        if delimiter is not None:
            self.delimiter = delimiter
        if string is not None:
            self.__call__(string)

    def __call__(self, string=None):
        if not string:
            self.keys = []
        else:
            self.keys = string.split(self.delimiter)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.keys == other.keys
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash((self.delimiter, str(self.keys)))

    def __len__(self):
        return len(self.keys)

    def __bool__(self):
        return bool(len(self.keys))

    def __repr__(self):
        return self.delimiter.join(self.keys)

    def __iter__(self):
        for key in self.keys:
            yield key

    def __reversed__(self):
        return reversed(self.keys)

    def __contains__(self, value):
        return value in self.keys

    def __getitem__(self, index):
        value = self.keys[index]
        if type(value) is list:
            value = self.delimiter.join(value)
        return value

    def __setitem__(self, index, value):
        self.keys[index] = value
        return self

    def __delitem__(self, index):
        del self.keys[index]
        return self


class DotNotationContainer(object):

    def __init__(self, data=None, expand=True):
        super().__init__()
        self.__call__(data=data, expand=expand)

    def __call__(self, data=None, expand=True):
        if data is None:
            self.__dict__ = {}

        elif type(data) is dict:
            if expand:
                data = self.expand_dot_notation(data)
            self.__dict__ = data

        elif type(data) is self.__class__:
            self.__dict__ = data.__dict__

        else:
            raise TypeError

        return self

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(str(self.__dict__))

    def __bool__(self):
        return bool(self.__dict__)

    def __iter__(self):
        for key, val in self.__dict__.items():
            yield (key, val)

    def __contains__(self, key):
        return self.has(key)

    def __getitem__(self, item):
        item = self.ref(item)
        if type(item) is dict:
            return self.__class__(item, expand=False)
        else:
            return item

    def __setitem__(self, key, value):
        self.set(key, value)
        return True

    def __copy__(self):
        new = type(self)()
        new.__dict__.update(self.__dict__)
        return new

    def __deepcopy__(self, memo):
        new = type(self)()
        new.__dict__.update(copy.deepcopy(self.__dict__))
        return new

    def items(self):
        for key, val in self.__dict__.items():
            yield (key, val)

    def keys(self):
        for key in self.__dict__.keys():
            yield key

    def values(self):
        for value in self.__dict__.values():
            yield value

    def clear(self):
        self.__dict__.clear()

    def ref(self, key=None, create=False):

        haystack = self.__dict__

        if type(key) is not DotNotationString:
            key = DotNotationString(key)

        for i, needle in enumerate(key, 1):

            if needle:

                if needle not in haystack:
                    if create:
                        haystack[needle] = {}

                    else:
                        message = self.format_keyerror(needle, key)
                        raise KeyError(message)

                if i < len(key) and type(haystack[needle]) is not dict:
                    if create:
                        haystack[needle] = {}

                    else:
                        message = self.format_typeerror(needle, key,
                                                        haystack[needle])
                        raise TypeError(message)

                if create and type(haystack[needle]) is not dict:
                    haystack[needle] = {}

                haystack = haystack[needle]

        return haystack

    def get(self, key=None):
        return copy.deepcopy(self.ref(key))

    def has(self, key=None):
        try:
            self.ref(key)
            return True
        except:
            return False

    def spawn(self, key=None):
        return self.__class__(self.ref(key), expand=False)

    def clone(self, key=None):
        return self.__class__(self.get(key), expand=False)

    def set(self, key, value, create=True):

        if type(key) is not DotNotationString:
            key = DotNotationString(key)

        haystack = self.ref(key[:-1], create)
        needle = key[-1]

        if needle not in haystack:
            if create:
                pass
            else:
                raise KeyError(self.format_keyerror(needle, key))

        haystack[needle] = value
        return True

    def push(self, key, value, create=True):

        if type(key) is not DotNotationString:
            key = DotNotationString(key)

        haystack = self.ref(key[:-1], create)
        needle = key[-1]

        if needle not in haystack:
            if create:
                haystack[needle] = []
            else:
                raise KeyError(self.format_keyerror(needle, key))

        if type(haystack[needle]) is not list:
            if create:
                haystack[needle] = [haystack[needle]]
            else:
                message = self.format_typeerror(haystack[needle], needle, key)
                raise TypeError(message)

        haystack[needle].append(value)
        return True

    def pull(self, key, value, cleanup=False):

        if type(key) is not DotNotationString:
            key = DotNotationString(key)

        haystack = self.ref(key[:-1])
        needle = key[-1]

        if needle not in haystack:
            message = self.format_keyerror(needle, key)
            raise KeyError(message)

        elif type(haystack[needle]) is not list:
            message = self.format_typeerror(haystack[needle], needle, key)
            raise TypeError(message)

        elif value not in haystack[needle]:
            message = self.format_valueerror(value, needle, key)
            raise ValueError(message)

        haystack[needle].remove(value)

        if cleanup:
            if haystack[needle] == []:
                del haystack[needle]

        return True

    def unset(self, key, cleanup=False):

        if type(key) is not DotNotationString:
            key = DotNotationString(key)

        haystack = self.ref(key[:-1])
        needle = key[-1]

        if needle not in haystack:
            raise KeyError(self.format_keyerror(needle, key))

        del haystack[needle]

        if cleanup:
            for i, needle in enumerate(key, 1):
                if i < len(key):
                    cleanup_key = key[:(len(key) - i)]
                    if self.has(cleanup_key) and self.get(cleanup_key) == {}:
                        self.unset(cleanup_key)
                    else:
                        break

        return True

    def merge(self, data):
        data = self.expand_dot_notation(data)
        return self.merge_containers(data, self.__dict__)

    def update(self, data):
        self.__dict__ = self.merge(data)
        return self.__dict__

    def collapse(self):
        return self.collapse_dot_notation(self.__dict__)

    @classmethod
    def format_keyerror(cls, needle, key):
        return "{} in {}".format(needle, key) if len(key) > 1 else needle

    @classmethod
    def format_typeerror(cls, type_, needle, key):
        message = "Expected dict, found {} for {}"
        keyerror = cls.format_keyerror(needle, key)
        return message.format(type(type_).__name__, keyerror)

    @classmethod
    def format_valueerror(cls, needle, key, value):
        message = "{} not in list for {}"
        keyerror = cls.format_keyerror(needle, key)
        return message.format(value, keyerror)

    @classmethod
    def merge_containers(cls, c1, c2):
        for k in c1.keys():
            if isinstance(c1[k], dict) and k in c2 and isinstance(c2[k], dict):
                c2[k] = cls.merge_containers(c1[k], c2[k])
            else:
                c2[k] = copy.deepcopy(c1[k])
        return c2

    @classmethod
    def expand_dot_notation(cls, data):
        ex = {}
        for key, val in data.items():

            if type(val) is dict:
                ex_val = cls.expand_dot_notation(val)
            else:
                ex_val = val

            if "." in key:
                key = DotNotationString(key)
                ex_key = {}
                for i, k in enumerate(reversed(key.keys)):
                    if i == 0:
                        ex_key = {k: ex_val}
                    elif i == (len(key) - 1):
                        if k not in ex:
                            ex[k] = ex_key
                        else:
                            ex[k] = cls.merge_containers(ex[k], ex_key)
                    else:
                        ex_key = {k: copy.copy(ex_key)}
            else:
                ex[key] = ex_val

        return ex

    @classmethod
    def collapse_dot_notation(cls, data, parent_key=None):
        items = []
        for key, val in data.items():
            new_key = "{}.{}".format(parent_key, key) if parent_key else key
            if type(val) is dict:
                items.extend(cls.collapse_dot_notation(val, new_key).items())
            else:
                items.append((new_key, val))
        return dict(items)


class OrderedDotNotationContainer(DotNotationContainer):
    """ override methods that specity dict and replace with OrderedDict """

    def __init__(self, data=None, expand=True):
        super().__init__()
        self.__call__(data=data, expand=expand)

    def __call__(self, data=None, expand=True):
        if data is None:
            self.__dict__ = OrderedDict()
            return

        elif type(data) not in [tuple, list, OrderedDict]:
            raise TypeError("Tuple, list of tuples or OrderedDict required, got {}".format(data))

        if type(data) is tuple:
            data = OrderedDict([data])

        elif type(data) is list and all(type(v) is tuple for v in data):
            data = OrderedDict(data)

        if expand:
            data = self.expand_dot_notation(data)

        self.__dict__ = data

    def __getitem__(self, item):
        item = self.ref(item)
        if type(item) is OrderedDict:
            return self.__class__(item, expand=False)
        else:
            return item

    def ref(self, key=None, create=False):

        haystack = self.__dict__

        if type(key) is not DotNotationString:
            key = DotNotationString(key)

        for i, needle in enumerate(key, 1):

            if needle:

                if needle not in haystack:
                    if create:
                        haystack[needle] = OrderedDict()

                    else:
                        message = self.format_keyerror(needle, key)
                        raise KeyError(message)

                if i < len(key) and type(haystack[needle]) is not OrderedDict:
                    if create:
                        haystack[needle] = OrderedDict()

                    else:
                        message = self.format_typeerror(type(haystack[needle]),
                                                        needle, key)
                        raise TypeError(message)

                if create and type(haystack[needle]) is not OrderedDict:
                    haystack[needle] = OrderedDict()

                haystack = haystack[needle]

        return haystack

    def merge(self, data):
        data = self.expand_dot_notation(data)
        return self.merge_containers(data, self.__dict__)

    @classmethod
    def merge_containers(cls, c1, c2):
        for k in c1.keys():
            if isinstance(c1[k], OrderedDict) and \
                    k in c2 and isinstance(c2[k], OrderedDict):
                c2[k] = cls.merge_containers(c1[k], c2[k])
            else:
                c2[k] = copy.deepcopy(c1[k])
        return c2

    @classmethod
    def collapse_dot_notation(cls, data, parent_k=None):
        items = []
        for k, v in data.items():
            _k = "{}.{}".format(parent_k, k) if parent_k else k
            if type(v) is OrderedDict:
                items.extend(cls.collapse_dot_notation(v, _k).items())
            else:
                items.append((_k, v))
        return OrderedDict(items)

    @classmethod
    def expand_dot_notation(cls, data):
        ex = OrderedDict()
        for t in data.items():
            if type(t[1]) is OrderedDict:
                ex_val = cls.expand_dot_notation(t[1])
            else:
                ex_val = t[1]

            if "." in t[0]:
                dns = DotNotationString(t[0])
                ex_key = OrderedDict()
                for i, k in enumerate(reversed(dns), 1):
                    if i == 1:
                        ex_key = OrderedDict([(k, ex_val)])
                    elif i == len(dns):
                        if k not in ex:
                            ex[k] = ex_key
                        else:
                            ex[k] = cls.merge_containers(ex[k], ex_key)
                    else:
                        ex_key = OrderedDict([(k, copy.copy(ex_key))])
            else:
                ex[t[0]] = ex_val

        return ex
