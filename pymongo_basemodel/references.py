
from .delimited import DelimitedDict


class References(DelimitedDict):

    # TODO: get reference model, always return base model if model or collection

    def collapse_delimited_notation(cls, data, parent_key=None):
        items = []
        for key, val in data.items():
            new_key = "{}.{}".format(parent_key, key) if parent_key else key
            if type(val) is cls.container \
            and all(k in val for k in ["type", "model"]):
                items.append((new_key, val))
            else:
                items.extend(
                    cls.collapse_delimited_notation(val, new_key).items()
                )

        return cls.container(items)
