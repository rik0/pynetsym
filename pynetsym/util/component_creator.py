import copy
import inspect

from pynetsym import error
from .dictionary import extract_subdictionary



class ComponentError(error.PyNetSymError):
    pass

class ComponentCreator(object):
    def __init__(self, context, component_name):
        self.context = context
        self.component_name = component_name

    @property
    def factory_name(self):
        return '%s_type' % (self.component_name, )

    @property
    def options_name(self):
        return '%s_options' % (self.component_name, )

    @property
    def parameters_name(self):
        return '%s_parameters' % (self.component_name, )

    def factory(self):
        factory = getattr(self.context, self.factory_name, None)
        if factory is not None:
            return factory
        else:
            raise ComponentError('Cannot create component %s' % (
                self.component_name, ))

    def factory_signature(self, factory):
        if inspect.isfunction(factory):
            return inspect.getargspec(factory)
        elif hasattr(factory, '__init__'):
            return inspect.getargspec(factory.__init__)
        else:
            raise ComponentError("Invalid factory.")

    def options(self, factory):
        has_kw = False
        try:
            options = factory.options
        except AttributeError:
            try:
                options = getattr(self.context, self.options_name)
            except AttributeError:
                (options, additional_arguments_name,
                 kw_name, _defaults) = self.factory_signature(factory)
                if additional_arguments_name is not None:
                    raise ComponentError("Cannot use introspection with varargs.")
                if kw_name is not None:
                    has_kw = True
        return copy.copy(options), has_kw


    def compute_overriding_parameters(self, has_kw, options, overriding_parameters):
        if has_kw:
            reduced_parameters = overriding_parameters
        else:
            reduced_parameters = extract_subdictionary(
                overriding_parameters, options)
        return reduced_parameters

    def parameters(self, factory, options, overriding_parameters, has_kw):
        try:
            parameters = factory.parameters
        except AttributeError:
            parameters = getattr(self.context, self.parameters_name, {})
        parameters = copy.deepcopy(parameters)
        reduced_parameters = self.compute_overriding_parameters(
            has_kw, options, overriding_parameters)
        parameters.update(reduced_parameters)
        return parameters

    def build(self, parameters=None, set_=False):
        parameters = {} if parameters is None else parameters
        factory = self.factory()
        options, has_kw = self.options(factory)
        parameters = self.parameters(factory, options, parameters, has_kw)
        try:
            instance = factory(**parameters)
        except TypeError as e:
            raise ComponentError(e)
        if set_:
            setattr(self.context, self.component_name, instance)
        else:
            return instance



