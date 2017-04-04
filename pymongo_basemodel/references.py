
from .delimited import DelimitedDict

cache = {}

def get_reference(entity, name):
    global cache
    if entity not in cache:
        raise Exception("no references registered for entity '{}'".format(entity))
    if name not in cache["entity"]:
        raise Exception("reference '{}' not registered for entity '{}'".format(name, entity))

    return 

def set_reference(entity, name, reference):
    global cache
    cache[entity][name] = reference

class References(DelimitedDict):

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
