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

    def process_arg_spec(self, arg_spec):
        arg_names, more_arg_name, kw_name, defaults = arg_spec
        if (more_arg_name is not None or
             kw_name is not None):
            raise ComponentError("Cannot use introspection with varargs or keyword args.")
        return arg_names

    def options(self, factory):
        try:
            return copy.copy(factory.options)
        except AttributeError:
            try:
                return copy.copy(getattr(self.context, self.options_name))
            except AttributeError:
                if inspect.isfunction(factory):
                    arg_spec = inspect.getargspec(factory)
                elif hasattr(factory, '__init__'):
                    arg_spec = inspect.getargspec(factory.__init__)
                else:
                    raise ComponentError(
                            'Cannot find options for %s' % (
                                self.component_name, ))
                return copy.copy(self.process_arg_spec(arg_spec))

    def parameters(self, options, simulation_parameters):
        program_specified_parameters = copy.deepcopy(getattr(self.context,
                self.parameters_name, {}))
        overriding_parameters = extract_subdictionary(
                simulation_parameters, options)
        program_specified_parameters.update(overriding_parameters)
        return program_specified_parameters



    def build(self, parameters=None, set_=False):
        parameters = {} if parameters is None else parameters
        factory = self.factory()
        options = self.options(factory)
        parameters = self.parameters(options, parameters)
        try:
            instance = factory(**parameters)
        except TypeError as e:
            raise ComponentError(e)
        if set_:
            setattr(self.context, self.component_name, instance)
        else:
            return instance



