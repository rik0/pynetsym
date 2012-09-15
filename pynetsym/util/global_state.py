def encapsulate_global(key, encapsulated_globals={}):
    def get_encapsulated_global():
        try:
            return encapsulated_globals[key]
        except KeyError:
            raise NameError("Name '%s' is not defined" % key)

    def set_encapsulated_global(value):
        encapsulated_globals[key] = value
    return get_encapsulated_global, set_encapsulated_global