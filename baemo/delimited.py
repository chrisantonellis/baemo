
"""
baemo.delimited
~~~~~~~~~~~~~~~~~~~~~~~~~~~
This module defines types that allow for accessing and modifying nested data
using delimited notation.
"""

import copy

from collections import MutableMapping
from collections import OrderedDict


class DelimitedStr(object):
    """ Emulates a string and handles delimited strings. Allows for accessing
    and modifying parts of the string by index or slice.
    """

    delimiter = "."

    def __init__(self, string=None, delimiter=None):
        self.keys = []
        if delimiter is not None:
            self.delimiter = delimiter
        if string is not None:
            self.__call__(string)

    def __call__(self, string=None):
        if string is None:
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

    def __str__(self):
        return self.delimiter.join(self.keys)

    def __iter__(self):
        for k in self.keys:
            yield k

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

    def __delitem__(self, index):
        del self.keys[index]


class DelimitedDict(MutableMapping):
    """ Emulates a dict and handles data with keys that are delimited strings.
    Allows for accessing and modifying nested data by delimited string.
    """

    container = dict

    def __init__(self, data=None, expand=True):
        super().__init__()
        self.__call__(data=data, expand=expand)

    def __call__(self, data=None, expand=True):
        if data is None:
            self.__dict__ = self.container()

        elif isinstance(data, self.__class__):
            self.__dict__ = data.__dict__

        elif isinstance(data, self.container):
            if expand:
                data = self._expand_delimited_notation(data)
            self.__dict__ = data

        else:
            raise TypeError(self._format_typeerror(
                data,
                "data",
                self.__class__.__name__
            ))

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

    def __str__(self):
        return str(self.__dict__)

    def __iter__(self):
        for key in self.__dict__.keys():
            yield key

    def __contains__(self, key):
        return self.has(key)

    def __getitem__(self, item):
        return self.ref(item)

    def __setitem__(self, key, value):
        self.set(key, value)
        return True

    def __delitem__(self, key):
        self.unset(key)
        return True

    def __len__(self):
        return len(self.__dict__)

    def __copy__(self):
        new = self.__class__()
        new.__dict__.update(self.__dict__)
        return new

    def __deepcopy__(self, memo):
        new = self.__class__()
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

    def ref(self, *args, create=False):

        if len(args) == 0:
            key = None
        else:
            key = args[0]

        if len(args) < 2:
            use_default_value = False
        else:
            use_default_value = True
            default_value = args[1]

        haystack = self.__dict__

        if type(key) is not DelimitedStr:
            key = DelimitedStr(key)

        for i, needle in enumerate(key, 1):

            if needle:

                if needle not in haystack:
                    if create:
                        haystack[needle] = self.container()

                    else:
                        if use_default_value:
                            return default_value
                        else:
                            message = self._format_keyerror(needle, key)
                            raise KeyError(message)

                if i < len(key) and \
                        not isinstance(haystack[needle], self.container):
                    if create:
                        haystack[needle] = self.container()

                    else:
                        if use_default_value:
                            return default_value
                        else:
                            message = self._format_typeerror(needle, key, haystack[needle])
                            raise TypeError(message)

                if create and not isinstance(haystack[needle], self.container):
                    haystack[needle] = self.container()

                haystack = haystack[needle]

        return haystack

    def get(self, *args):
        return copy.deepcopy(self.ref(*args))

    def has(self, key=None):
        """ Returns True if object has key, else False
        Returun False if no key specified and object.__dict__ is empty """
        try:
            r = self.ref(key)
            return False if key is None and not r else True
        except:
            return False

    def spawn(self, *args, **kwargs):
        """ create another instance whos __dict__ is a reference to this
        instances __dict__, doppelganger instance """
        return self.__class__(self.ref(*args, **kwargs), expand=False)

    def clone(self, key=None):
        """ create another instance whos __dict__ is a copy of this
        instances __dict__ """
        return self.__class__(self.get(key), expand=False)

    def set(self, key, value, create=True):

        if type(key) is not DelimitedStr:
            key = DelimitedStr(key)

        haystack = self.ref(key[:-1], create=create)
        needle = key[-1]

        if needle not in haystack:
            if create:
                pass
            else:
                raise KeyError(self._format_keyerror(needle, key))

        haystack[needle] = value
        return True

    def push(self, key, value, create=True):

        if type(key) is not DelimitedStr:
            key = DelimitedStr(key)

        haystack = self.ref(key[:-1], create=create)
        needle = key[-1]

        if needle not in haystack:
            if create:
                haystack[needle] = []
            else:
                raise KeyError(self._format_keyerror(needle, key))

        if type(haystack[needle]) is not list:
            if create:
                haystack[needle] = [haystack[needle]]
            else:
                message = self._format_typeerror(haystack[needle], needle, key)
                raise TypeError(message)

        haystack[needle].append(value)
        return True

    def pull(self, key, value, cleanup=False):

        if type(key) is not DelimitedStr:
            key = DelimitedStr(key)

        haystack = self.ref(key[:-1])
        needle = key[-1]

        if needle not in haystack:
            message = self._format_keyerror(needle, key)
            raise KeyError(message)

        elif type(haystack[needle]) is not list:
            message = self._format_typeerror(haystack[needle], needle, key)
            raise TypeError(message)

        elif value not in haystack[needle]:
            message = self._format_valueerror(value, needle, key)
            raise ValueError(message)

        haystack[needle].remove(value)

        if cleanup:
            if haystack[needle] == []:
                del haystack[needle]

        return True

    def unset(self, key, cleanup=False):

        if type(key) is not DelimitedStr:
            key = DelimitedStr(key)

        haystack = self.ref(key[:-1])
        needle = key[-1]

        if needle not in haystack:
            raise KeyError(self._format_keyerror(needle, key))

        del haystack[needle]

        if cleanup:
            for i, needle in enumerate(key, 1):
                if i < len(key):
                    cleanup_key = key[:(len(key) - i)]
                    if self.has(cleanup_key) and self.get(cleanup_key) == self.container():
                        self.unset(cleanup_key)

        return True

    def merge(self, data):
        """ merges self.__dict__ with data and returns data """

        if isinstance(data, self.__class__):
            data = data.__dict__

        elif isinstance(data, self.container):
            data = self._expand_delimited_notation(data)

        return self._merge(data, copy.deepcopy(self.__dict__))

    def update(self, data):
        self.__dict__ = self.merge(data)
        return self.__dict__

    def collapse(self):
        return self._collapse_delimited_notation(self.__dict__)

    @classmethod
    def _format_keyerror(cls, needle, key):
        return "{} in {}".format(needle, key) if len(key) > 1 else needle

    @classmethod
    def _format_typeerror(cls, type_, needle, key):
        message = "Expected {}, found {} for {}"
        keyerror = cls._format_keyerror(needle, key)
        return message.format(
            cls.container.__name__,
            type(type_).__name__,
            keyerror
        )

    @classmethod
    def _format_valueerror(cls, needle, key, value):
        message = "{} not in list for {}"
        keyerror = cls._format_keyerror(needle, key)
        return message.format(value, keyerror)

    @classmethod
    def _merge(cls, d1, d2):
        """ d1 overwrites values in d2 """

        for k in d1.keys():
            if isinstance(d1[k], cls.container) and \
                    k in d2 and isinstance(d2[k], cls.container):
                d2[k] = cls._merge(d1[k], d2[k])
            else:
                d2[k] = d1[k]
        return d2

    @classmethod
    def _expand_delimited_notation(cls, data):
        ex = cls.container()
        for key, val in data.items():

            if type(val) is cls.container:
                ex_val = cls._expand_delimited_notation(val)
            else:
                ex_val = val

            if "." in key:
                key = DelimitedStr(key)
                ex_key = cls.container()
                for i, k in enumerate(reversed(key), 1):
                    if i == 1:
                        ex_key[k] = ex_val
                    elif i == len(key):
                        if k not in ex:
                            ex[k] = ex_key
                        else:
                            ex[k] = cls._merge(ex[k], ex_key)
                    else:
                        ex_temp = cls.container()
                        ex_temp[k] = copy.copy(ex_key)
                        ex_key = ex_temp
            else:
                ex[key] = ex_val

        return ex

    @classmethod
    def _collapse_delimited_notation(cls, data, parent_key=None):
        items = []
        for key, val in data.items():
            new_key = "{}.{}".format(parent_key, key) if parent_key else key
            if type(val) is cls.container:

                if len(val):
                    items.extend(
                        cls._collapse_delimited_notation(val, new_key).items()
                    )

                # empty container
                else:
                    items.append((new_key, val))

            else:
                items.append((new_key, val))

        return data.__class__(items)


class DelimitedOrderedDict(DelimitedDict):
    """ Emulates an ordereddict and handles data with keys that are delimited
    strings. Allows for accessing and modifying nested data by delimited
    string.
    """

    container = OrderedDict
