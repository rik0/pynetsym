import importlib
import warnings
from pynetsym.util.iterators import inits

__all__ = ['PluginManager']

class PluginManager(object):

    def __init__(self):
        self._plugins = set()
        self._missing = set()

    def has(self, what):
        module = self.require(what)
        if module is None:
            return False
        else:
            return True

    def can_test(self, what):
        return what in self._plugins, 'Missing module %s' % what

    def _register(self, what):
        self._plugins.add(what)

    def require(self, what):
        try:
            module = importlib.import_module(what)

            parts = what.split('.')
            parts_beginnings = inits(parts)
            next(parts_beginnings) # throw away empty subsequence
            for init in parts_beginnings:
                name = '.'.join(init)
            return module
        except ImportError:
            if what not in self._missing:
                warnings.warn('Cannot import %s' % what)
            else:
                self._missing.add(what)
            return None

    def conditional_import(self, if_has, then_import):
        if self.has(if_has):
            return importlib.import_module(then_import)

    def conditional_from_import(self, if_has, import_from, *names):
        if self.has(if_has):
            mod = importlib.import_module(import_from)
            return [(name, getattr(mod, name)) for name in names if hasattr(mod, name)]
        else:
            return []

    def conditional_from_import_into(self, if_has, import_from, into, *names):
        pairs = self.conditional_from_import(if_has, import_from, *names)
        into = importlib.import_module(into)
        for name, object in pairs:
            setattr(into, name, object)

    def conditional_from_import_into_exporting(self, if_has, import_from, into, namespace, *names):
        pairs = self.conditional_from_import(if_has, import_from, *names)
        into = importlib.import_module(into)
        for name, object in pairs:
            setattr(into, name, object)
            namespace.append(name)


_general_plugins = PluginManager()


globals().update({name: getattr(_general_plugins, name) for name in dir(_general_plugins) if not name.startswith('_')})
__all__.extend(name for name in dir(_general_plugins) if not name.startswith('_'))