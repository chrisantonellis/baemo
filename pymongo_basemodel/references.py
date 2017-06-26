
from .delimited import DelimitedDict
from .exceptions import ReferencesMalformed


class Reference(dict):
    pass


class References(DelimitedDict):
    """ not meant to be changed after the fact so missing update methods """

    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)
        self.wrap()
        self.validate()

    def wrap(self):
        self.__dict__ = self._wrap(self.__dict__)

    def validate(self):
        return self._validate(self.__dict__)

    """ wrap actual references as Reference class, anything else should be
    a DelimitedDict """
    @classmethod
    def _wrap(cls, data):
        for k, v in data.items():
            if isinstance(v, (cls.container, cls.__class__)):
                if all(k in v for k in ["type", "entity"]):
                    data[k] = Reference(v)
                else:
                    data[k] = cls._wrap(v)

        return data

    @classmethod
    def _validate(cls, data):
        for k, v in cls._collapse_delimited_notation(data).items():
            if not isinstance(v, Reference):
                raise ReferencesMalformed(k, v)
