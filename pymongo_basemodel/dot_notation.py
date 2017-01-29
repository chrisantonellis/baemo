
import copy

__all__ = [
    "DotNotationString",
    "DotNotationContainer"
]


class DotNotationString(object):

    def __init__(self, string=None):
        self.raw = ""
        self.keys = [""]
        if string is not None:
            self.__call__(string)

    def __call__(self, string):
        self.raw = string
        self.keys = string.split(".")

    def __len__(self):
        return len(self.keys)

    def __repr__(self):
        return self.raw

    def __iter__(self):
        for key in self.keys:
            yield key

    def __getitem__(self, item):
        value = self.keys[item]

        if type(value) is list:
            value = ".".join(value)

        return value


class DotNotationContainer(object):

    def __init__(self, data=None, expand=True):
        if data:
            self.__call__(data, expand=expand)
        super().__init__()

    def __call__(self, data, expand=True):
        if expand:
            data = self.expand_dot_notation(data)
        self.__dict__ = data
        return self

    def __bool__(self):
        return bool(self.__dict__)

    def __eq__(self, value):
        return self.__dict__ == value

    def __repr__(self):
        return str(self.__dict__)

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
        return self.merge_dicts(data, self.__dict__)

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
    def merge_dicts(cls, dict_1, dict_2):
        for key, val in dict_1.items():
            if isinstance(dict_1[key], dict) and \
                    key in dict_2 and isinstance(dict_2[key], dict):
                dict_2[key] = cls.merge_dicts(dict_1[key], dict_2[key])
            else:
                dict_2[key] = copy.deepcopy(dict_1[key])
        return dict_2

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
                            ex[k] = cls.merge_dicts(ex[k], ex_key)
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
