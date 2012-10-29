

def identity(x):
    return x

class DefaultIndexMap(object):
    def __init__(self, dictionary={},
            default_function=identity, **kwargs):
        self.elements = {}
        self.elements.update(dictionary, **kwargs)
        self.default_function = default_function

    def _get_one(self, item):
        try:
            return self.elements[item]
        except KeyError:
            try:
                return self.default_function(item)
            except Exception as e:
                raise KeyError(e)

    def __getitem__(self, item):
        return self._get_one(item)