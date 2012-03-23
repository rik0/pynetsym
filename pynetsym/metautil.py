import abc
import functools
import inspect
import types
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


def abstract_interface_from(cls, debug=False):
    """
    Extracts the public methods from cls and adds them as abstract methods to new_cls.
    new_cls is required to have a subclass of abc.ABCMeta as metaclass.

    Intended usage::
        @extract_interface(cls)
        class new_cls(super_cls):
            __metaclass__ = abc.ABCMeta
            pass

    @requires: cls to be an ABC
    """

    class _T(object):
        __metaclass__ = abc.ABCMeta

    #noinspection PyUnusedLocal
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

    def __get__(self, obj, type=None):
        return self.fget.__get__(None, type)()

class before(object):
    def __init__(self, before_action, *args, **kwargs):
        if callable(before_action):
            self.before_action = before_action
            self.before_args = args
            self.before_kwargs = kwargs
        else:
            raise TypeError("%s not callable." % before_action)

    def __call__(self, func):
        def aux(*args, **kwargs):
            before_value = self.before_action(
                *self.before_args, **self.before_kwargs)
            func_value = func(*args, **kwargs)
            if before_value is not None:
                return before_value, func_value
            else:
                return func_value
        functools.update_wrapper(aux, func)
        return aux


class DelegationError(StandardError):
    pass

class delegate(object):
    def __new__(cls, delegate_or_function):
        obj = super(delegate, cls).__new__(cls)
        obj.delegate_name = None
        if callable(delegate_or_function):
            func = delegate_or_function
            delegator = delegate('delegate')
            return delegator(func)
        else:
            obj.delegate_name = delegate_or_function
            return obj

    def __call__(self, func):
        def aux(bself, *args, **kwargs):
            try:
                delegate = getattr(bself, self.delegate_name)
                method = getattr(delegate, func.func_name)
            except AttributeError:
                raise DelegationError()
            else:
                method(*args, **kwargs)
        functools.update_wrapper(aux, func)
        return aux

def delegate_methods(methods, before=None, after=None):
    def add_delegates(cls):
        for name in methods:
            def method(self, *args, **kwargs):
                try:
                    m = getattr(self.delegate, name)
                except AttributeError, e:
                    raise DelegationError(e)
                else:
                    return m(*args, **kwargs)
            setattr(cls, name, method)
        return cls
    return add_delegates

class delegate_all(object):
    DEFAULT_EXCLUDED = ('__init__', )

    def __init__(self, cls, delegate_name='delegate', exclude=DEFAULT_EXCLUDED,
                 include_specials=False, include_properties=True, force=[],
                 override=False):
        self.cls = cls
        self.delegate_name = delegate_name
        self.exclude = set(exclude)
        self.include_specials = include_specials
        self.include_properties = include_properties
        self.force = set(force)
        self.override = override

    def is_property(self, attribute):
        return isinstance(attribute, property)

    def is_method(self, attribute):
        ## This is false for many special stuff coming from object
        ## e.g., __reduce__, __hash__, etc.
        return isinstance(attribute, types.MethodType)

    def is_method_or_property(self, attribute):
        return self.is_method(attribute) or self.is_property(attribute)

    def build_method(self, delegate_name, method_name):
        def method(self, *args, **kwargs):
                try:
                    delegate = getattr(self, delegate_name)
                    method = getattr(delegate, method_name)
                except AttributeError, e:
                    raise DelegationError(e.message)
                else:
                    return method(*args, **kwargs)
        return method


    def build_property(self, delegate_name, property_name):
        def fget(self):
            delegate = getattr(self, delegate_name)
            return getattr(delegate, property_name)
        def fset(self, value):
            delegate = getattr(self, delegate_name)
            setattr(delegate, property_name, value)
        def fdel(self):
            delegate = getattr(self, delegate_name)
            delattr(delegate, property_name)
        return property(fget, fset, fdel)

    def build_methods_list(self, new_cls):
        predicate = (self.is_method_or_property
                     if self.include_properties else self.is_method)
        methods = inspect.getmembers(self.cls, predicate)
        # remove special stuff if not included
        if not self.include_specials:
            methods = filter(
                lambda (name, method): not name.startswith('__'),
                methods)
        method_names = set(method_pair[0] for method_pair in methods)
        method_names -= self.exclude
        method_names |= self.force
        new_cls_methods = set(new_cls.__dict__.keys())
        if not self.override:
            method_names -= new_cls_methods
        return method_names

    def remove_abstract_methods(self, method_names, new_cls):
        metaclass = getattr(new_cls, '__metaclass__', type)
        if issubclass(metaclass, abc.ABCMeta):
            abstract_methods = set(new_cls.__abstractmethods__)
            abstract_methods -= method_names
            new_cls.__abstractmethods__ = frozenset(abstract_methods)

    def __call__(self, new_cls):
        method_names = self.build_methods_list(new_cls)

        for name in method_names:
            original = getattr(self.cls, name)
            if self.is_method(original):
                method = self.build_method(self.delegate_name, name)
                functools.update_wrapper(method, original)
                setattr(new_cls, name, method)
            elif self.is_property(original):
                setattr(new_cls, name,
                        self.build_property(self.delegate_name, name))

        self.remove_abstract_methods(method_names, new_cls)
        return new_cls

def accumulate_older_variants(child_obj, attr_name):
    import sys
    child_type = child_obj if isinstance(child_obj, type) else type(child_obj)

    reverted_mro = reversed(child_type.__mro__)

    values = set()
    for parent in reverted_mro:
        values.update(parent.__dict__.get(attr_name, set()))

    return values
