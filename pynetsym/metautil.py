import abc
import inspect
import decorator

def copy_doc(cls):
    """
    Copy documentation from method with same name of cls.

    @param cls: the class from which to get the method.

    @attention: This is meant to be used as a decorator.

    """

    def copy_doc_aux(method):
        original_method = getattr(cls, method.func_name)
        original_doc = inspect.getdoc(original_method)
        method.__doc__ = original_doc
        return method

    return copy_doc_aux



def extract_interface(cls, debug=False):
    """
    Extracts the public methods from cls and adds them as abstract methods to new_cls.
    new_cls is required to have a subclass of abc.ABCMeta as metaclass.

    ::
        @extract_interface(cls)
        class new_cls(super_cls):
            __metaclass__ = abc.ABCMeta
            pass

    @requires: cls to be an ABC
    """

    class _T(object):
        __metaclass__ = abc.ABCMeta

    @decorator.decorator
    def stub(_f, *_args, **_kw):
        pass

    to_skip = set(dir(_T)) - set(dir(type))
    to_skip.update(['__str__'])

    def should_process(name):
        if name in to_skip:
            return False
        elif name.startswith('_') and not name.startswith('__'):
            return False
        return True

    def processor(new_cls):
        try:
            if not issubclass(new_cls.__metaclass__, abc.ABCMeta):
                raise TypeError("Class metaclass should be abc.ABCMeta")
        except AttributeError:
            raise TypeError("Class metaclass should be abc.ABCMeta")

        new_abstract_methods = set()
        for name, method in inspect.getmembers(cls):
            if callable(method):
                if should_process(name):
                    try:
                        func = method.im_func
                    except AttributeError:
                        if debug: print name
                    else:
                        setattr(new_cls, name, abc.abstractmethod(stub(func)))
                        new_abstract_methods.add(name)
        else:
            # add the new abstract methods to the class
            new_cls.__abstractmethods__ |=  new_abstract_methods
            new_cls.__abstractmethods__ = frozenset(new_cls.__abstractmethods__)
        return new_cls

    return processor
