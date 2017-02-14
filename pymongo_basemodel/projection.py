
import copy

from .dot_notation import DotNotationContainer
from .exceptions import ProjectionMalformed
from .exceptions import ProjectionTypeMismatch


class Projection(DotNotationContainer):

    def __init__(self, data=None, expand=True):
        super().__init__()
        self.__call__(data=data, expand=expand)

    def __call__(self, data=None, expand=True):
        if data is None:
            self.__dict__ = {}    
        else:
            if expand:
                data = self.expand_dot_notation(data)
            self.validate_projection(data)
            self.__dict__ = data

    @property
    def type(self):
        return self.validate_projection(self.__dict__)

    def set(self, key, value):
        data = DotNotationContainer()
        data.set(key, value)
        p = self.merge_projections(self.__dict__, data.__dict__)
        self.validate_projection(p)
        super().set(key, value)
        return True

    def merge(self, projection):
        if type(projection) is not Projection:
            projection = Projection(data=projection)

        if self.type and projection.type and self.type != projection.type:
            raise ProjectionTypeMismatch

        return self.merge_projections(projection.__dict__, self.__dict__)

    def flatten(self):
        return self.flatten_projection(self.__dict__)

    @classmethod
    def validate_projection(cls, p, parent_type=None):

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
                    child_type = cls.validate_projection(value, parent_type)
                except ProjectionMalformed as e:
                    raise ProjectionMalformed(
                        "{}.{}".format(k, e.key), e.value
                    )

                if child_type and local_type and child_type != local_type:
                    raise ProjectionTypeMismatch

                if child_type and not local_type:
                    local_type = child_type

        return local_type

    @classmethod
    def flatten_projection(cls, projection):

        # 0 = exclude
        # 1 = include
        # 2 = resolve relationship
        # Projection = resolve relationship and pass projection forward
        projection_type = Projection.validate_projection(projection)
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

        return flattened

    @classmethod
    def merge_projections(cls, p1, p2):
        for key, val in p1.items():
            if val == -1:
                del p2[key]
            elif isinstance(p1[key], dict) and \
                    key in p2 and isinstance(p2[key], dict):
                p2[key] = cls.merge_projections(p1[key], p2[key])
            else:
                p2[key] = p1[key]
        return p2
