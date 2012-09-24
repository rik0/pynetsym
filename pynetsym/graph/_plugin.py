class _RegisteredPlugins:
    _plugins = set()

    @classmethod
    def has(cls, what):
        return what in cls._plugins

    @classmethod
    def can_test(cls, what):
        return what in cls._plugins, 'Missing module %s' % what

    @classmethod
    def register(cls, what):
        cls._plugins.add(what)

has = _RegisteredPlugins.has
can_test = _RegisteredPlugins.can_test
register = _RegisteredPlugins.register