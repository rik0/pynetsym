
def gather_from_ancestors(child_obj, attr_name, acc_type=set):
    """
    Accumulate all the options sets defined over the class hierarchy.

    @param child_obj: an object instance or a class from which to start
        gathering. If is an instance, its type is obtained.
    @param attr_name: the name of the attribute to accumulate.
    @type attr_name: str
    @param acc_type: a factory of the type of objects were to accumulate stuff.
        Examples are sets or lists (depending on the intended semantics).
    """
    child_type = child_obj if isinstance(child_obj, type) else type(child_obj)

    reverted_mro = reversed(child_type.__mro__)

    values = acc_type()
    try:
        acc_method = values.update
    except AttributeError:
        acc_method = values.extend
    for parent in reverted_mro:
        new_value = parent.__dict__.get(attr_name, acc_type())
        if isinstance(new_value, property):
            new_value = new_value.fget(child_obj)
        acc_method(new_value)
    return values


class classproperty(property):
    """
    Introduces a class property. Works like property, but on the class.

    @warning: the setter and deleter do not work as expected.
    """
    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        fget = fget if fget is None else classmethod(fget)
        fset = fset if fset is None else classmethod(fset)
        fdel = fdel if fdel is None else classmethod(fdel)
        doc = fget.__doc__ if doc is None else doc
        super(classproperty, self).__init__(fget, fset, fdel, doc)

    def __get__(self, obj, clstype=None):
        return self.fget.__get__(None, clstype)()
