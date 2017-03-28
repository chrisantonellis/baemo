

class Undefined(object):
    """ unique type used to represent non presence of attribute because all
    existing types (including None) are valid return values """

    def __str__(self):
        return "undefined"

    def __bool__(self):
        return False
