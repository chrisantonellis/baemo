
from .delimited import DelimitedDict

class Reference(dict):
    pass


class References(DelimitedDict):

    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)
        self.__dict__ = self._wrap(self.__dict__)

    def _wrap(self, data):
        for k, v in data.items():
            if isinstance(v, (self.container, self.__class__)):

                if all(k in v for k in ["type", "entity"]):
                    data[k] = Reference(v)
                else:
                    data[k] = self._wrap(v)

        return data
