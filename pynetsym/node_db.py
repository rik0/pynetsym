from traits.api import Interface, HasTraits, SingletonHasStrictTraits
from traits.api import Instance, Module, Dict, Either, Int, Str
from traits.api import implements

class MissingNode(Exception):
    pass


class ISerialize(Interface):
    def loads(self, pickled_representation):
        """
        Loads a pickled representation previously created with :meth: dumps.
        """
        pass

    def dumps(self, obj):
        """
        Creates a pickled representation of object.
        """
        pass


class PythonPickler(SingletonHasStrictTraits):
    implements(ISerialize)
    pickle_module = Module

    def __init__(self):
        try:
            import cPickle as pickle_module
        except ImportError:
            import pickle as pickle_module
        self.pickle_module = pickle_module

    def loads(self, pickled_representation):
        return self.pickle_module.loads(pickled_representation)

    def dumps(self, obj):
        return self.pickle_module.dumps(obj,
                                        self.pickle_module.HIGHEST_PROTOCOL)

class JSONPickle(SingletonHasStrictTraits):
    implements(ISerialize)
    pickle_module = Module

    def __init__(self):
        import jsonpickle
        self.pickle_module = jsonpickle

    def loads(self, pickled_representation):
        return self.pickle_module.decode(pickled_representation)

    def dumps(self, obj):
        return self.pickle_module.encode(obj)


class IAgentStorage(Interface):
    def recover(self, identifier):
        """
        Recovers the agent saved under identifier.
        """
        pass

    def store(self, agent):
        """
        Stores the state of the specified agent.
        """
        pass


class NodeDB(HasTraits):
    implements(IAgentStorage)

    pickling_module = Instance(ISerialize, allow_none=False)
    storage = Dict(key_trait=Either(Int, Str),
                   value_trait=Str, allow_none=False)

    def __init__(self, pickling_module, storage):
        """
        Creates a new NodeDB.

        @param pickling_module: something that is able to pickle Python
            objects. Pickle interface expected (loads and dumps).
        @param storage: object that can store pickled objects. Dictionary
            __getitem__/__setitem__ interface expected.
        """
        self.storage = storage
        self.pickling_module = pickling_module

    def recover(self, identifier):
        try:
            node = self.pickling_module.loads(self.storage.pop(identifier))
            return node
        except KeyError as e:
            raise MissingNode(e)

    def store(self, node):
        s = self.pickling_module.dumps(node)
        self.storage[node.id] = s
