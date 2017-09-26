
import copy

from .delimited import DelimitedDict
from .exceptions import ProjectionMalformed
from .exceptions import ProjectionTypeMismatch


class Projection(DelimitedDict):

    def __call__(self, data=None, expand=True):
        super().__call__(data=data, expand=expand)
        self.validate()

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.validate()

    def set(self, key, value):
        super().set(key, value)
        self.validate()
        return self

    def validate(self):
        return self._validate(self)

    def flatten(self):
        return self._flatten(self)

    def merge(self, data):
        if type(data) is not Projection:
            data = Projection(data)

        self_type = self.validate()
        projection_type = data.validate()
        if self_type and projection_type and self_type != projection_type:
            raise ProjectionTypeMismatch

        return self._merge(data, self)

    def update(self, data):
        self.__dict__ = self.merge(data).__dict__

    @classmethod
    def _validate(cls, p, parent_type=None):

        # check for invalid values
        for k, v in p.items():
            if v not in [-1, 0, 1, 2] and type(v) not in [dict, Projection]:
                raise ProjectionMalformed(k, v)

        # checking for -1, 1, 2, dict, Projection
        if any(v == 1 for v in p.values()) and \
                all(v in [-1, 1, 2] or
                    type(v) in [dict, Projection] for v in p.values()):
            local_type = "inclusive"

        # checking for -1, 0, 2, dict, Projection
        elif any(v == 0 for v in p.values()) and \
                all(v in [-1, 0, 2] or
                    type(v) in [dict, Projection] for v in p.values()):
            local_type = "exclusive"

        # checking for -1, 2, dict, Projection
        elif all(v in [-1, 2] or
                 type(v) in [dict, Projection] for v in p.values()):
            local_type = None

        # values are valid but types are mixed
        else:
            raise ProjectionTypeMismatch

        # check type recursively
        for value in p.values():
            if type(value) is dict:

                try:
                    child_type = cls._validate(value, parent_type)
                except ProjectionMalformed as e:
                    raise ProjectionMalformed(
                        "{}.{}".format(k, e.args[0]), e.args[1]
                    )

                if child_type and local_type and child_type != local_type:
                    raise ProjectionTypeMismatch

                if child_type and not local_type:
                    local_type = child_type

        return local_type

    @classmethod
    def _flatten(cls, projection):

        # 0 = exclude
        # 1 = include
        # 2 = resolve reference
        # Projection = resolve reference and pass projection forward
        projection_type = projection.validate()
        projection = copy.copy(projection)
        flattened = copy.copy(projection)

        # inclusive
        # 2 ----------> 1
        # Projection -> 1
        if projection_type == "inclusive":
            for key, val in projection.items():
                if val == 2 or type(val) in [dict, Projection]:
                    flattened[key] = 1

        # exclusive, None
        # 2 ----------> [ remove ]
        # Projection -> [ remove ]
        elif projection_type in ["exclusive", None]:
            for key, val in projection.items():
                if val == 2 or type(val) in [dict, Projection]:
                    del flattened[key]

        return flattened.get()

    @classmethod
    def _merge(cls, projection1, projection2):
        """ merge two projections, delete key if -1 found, returned merged projection
        without altering self
        """

        for key, val in projection1.items():
            if val == -1:
                del projection2[key]

            elif isinstance(projection1[key], dict) and key in projection2 and isinstance(projection2[key], dict):
                projection2[key] = cls._merge(projection1[key], projection2[key])

            else:
                projection2[key] = projection1[key]

        return projection2
