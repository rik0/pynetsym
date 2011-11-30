import importlib

class PluginLoader(object):
    DEFAULT_PLUGINS_PATH = ['pynetsym.models']

    @classmethod
    def load(cls, name):
        if not name.startswith('.'):
            name = '.' + name
        for path in cls.DEFAULT_PLUGINS_PATH:
            try:
                return importlib.import_module(name, path)
            except ImportError:
                pass
        raise ImportError

    @classmethod
    def add_patha(cls, path):
        cls.DEFAULT_PLUGINS_PATH.insert(0, path)

    @classmethod
    def add_pathz(cls, path):
        cls.DEFAULT_PLUGINS_PATH.append(path)

    add_path = add_pathz

    @classmethod
    def remove_path(cls, path):
        cls.DEFAULT_PLUGINS_PATH.remove(path)

def load_plugin(name):
    return PluginLoader.load(name)