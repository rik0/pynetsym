import abc
import inspect
import decorator

def copy_doc(cls):
    """Copy documentation from method with same name of cls

    This is meant to be used as a decorator.

    cls the class from which to get the method.

    """

    def copy_doc_aux(method):
        original_method = getattr(cls, method.func_name)
        original_doc = inspect.getdoc(original_method)
        method.__doc__ = original_doc
        return method

    return copy_doc_aux



def extract_interface(cls, debug=False):
    """

    """

    class _T(object):
        __metaclass__ = abc.ABCMeta

    @decorator.decorator
    def stub(_f, *_args, **_kw):
        pass

    to_skip = set(dir(_T)) - set(dir(type))
    def should_process(name):
        if name in to_skip:
            return False
        elif name.startswith('_') and not name.startswith('__'):
            return False
        return True

    def processor(new_cls):
        for name, method in inspect.getmembers(cls):
            if callable(method):
                if should_process(name):
                    try:
                        func = method.im_func
                    except AttributeError:
                        if debug: print name
                    else:
                        setattr(new_cls, name, abc.abstractmethod(stub(func)))
        return new_cls

    return processor
