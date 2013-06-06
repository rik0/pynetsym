import numpy
from traits.api import Interface, HasTraits, SingletonHasStrictTraits
from traits.api import Instance, Module, Dict, Either, CInt, Str
from traits.api import implements
from pynetsym.error import PyNetSymError


__all__ = [
    "MissingNode",
    "ISerialize",
    "PythonPickler",
    "JSONPickler",
    "IAgentStorage",
    "AgentDB"
]


class MissingNode(PyNetSymError):
    pass


class SerializationError(PyNetSymError):
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
        try:
            return self.pickle_module.loads(pickled_representation)
        except TypeError as e:
            raise SerializationError(e)

    def dumps(self, obj):
        try:
            return self.pickle_module.dumps(
                obj, self.pickle_module.HIGHEST_PROTOCOL)
        except TypeError as e:
            raise SerializationError(e)

try:
    import jsonpickle
except ImportError:
    __all__.remove("JSONPickler")
else:
    class NumpyFloatHandler(jsonpickle.handlers.BaseHandler):
        """
        Automatic conversion of numpy float  to python floats
        Required for jsonpickle to work correctly
        """
        def flatten(self, obj, data):
            """
            Converts and rounds a Numpy.float* to Python float
            """
            return round(obj,6)

    jsonpickle.handlers.registry.register(numpy.float, NumpyFloatHandler)
    jsonpickle.handlers.registry.register(numpy.float32, NumpyFloatHandler)
    jsonpickle.handlers.registry.register(numpy.float64, NumpyFloatHandler)

    class NumpyIntHandler(jsonpickle.handlers.BaseHandler):
        """
        Automatic conversion of numpy float  to python floats
        Required for jsonpickle to work correctly
        """
        def flatten(self, obj, data):
            """
            Converts and rounds a Numpy.float* to Python float
            """
            return int(obj)

    jsonpickle.handlers.registry.register(numpy.int8,  NumpyIntHandler)
    jsonpickle.handlers.registry.register(numpy.int16, NumpyIntHandler)
    jsonpickle.handlers.registry.register(numpy.int32, NumpyIntHandler)
    jsonpickle.handlers.registry.register(numpy.int64, NumpyIntHandler)
    jsonpickle.handlers.registry.register(numpy.int_,  NumpyIntHandler)

    class JSONPickler(SingletonHasStrictTraits):
        implements(ISerialize)
        pickle_module = Module

        def __init__(self):
            self.pickle_module = jsonpickle

        def loads(self, pickled_representation):
            try:
                return self.pickle_module.decode(pickled_representation)
            except Exception as e:
                raise SerializationError(e)

        def dumps(self, obj):
            try:
                return self.pickle_module.encode(obj)
            except Exception as e:
                raise SerializationError(e)


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


class AgentDB(HasTraits):
    implements(IAgentStorage)

    pickling_module = Instance(ISerialize, allow_none=False)
    storage = Dict(key_trait=Either(CInt, Str),
                   value_trait=Str, allow_none=False)

    def __init__(self, pickling_module, storage):
        """
        Creates a new AgentDB.

        :param pickling_module: something that is able to pickle Python
            objects. Pickle interface expected (loads and dumps).
        :param storage: object that can store pickled objects.
            Dictionary __getitem__/__setitem__ interface expected.
        :type storage: :class:`collections.MutableMapping
        """
        self.storage = storage
        self.pickling_module = pickling_module

    def recover(self, identifier):
        try:
            node = self.pickling_module.loads(self.storage[identifier])
            return node
        except KeyError as e:
            raise MissingNode(e)

    def store(self, node):
        s = self.pickling_module.dumps(node)
        self.storage[node.id] = s

try:
    import jsonpickle
    from pymongo import MongoClient
except ImportError:
    pass
else:
    def run_mongo(dbfile, port=27017, host='localhost'):
        """
        Convenience function to run a Mongo instance.

        It assumes mongod is on the PATH.

        :param dbfile: the db file to use
        :param port: the port to use
        :param host: the host to use
        :return:
        """
        import subprocess
        p = subprocess.Popen(['mongod',
            '--port', port,
            '--host', host,
            '--dbpath', dbfile])
        return p

    class MongoAgentDB(HasTraits):
        implements(IAgentStorage)

        db_name = 'pynetsym_agents'

        def __init__(self):
            self.client = MongoClient()
            self.client.drop_database(self.db_name)
            self.agents_db = self.client[self.db_name].agents

        def _mktypename(self, obj):
            cls = type(obj)
            return '%s.%s' % (cls.__module__, cls.__name__)

        def store(self, node):
            node.id = int(node.id)
            state = node.__getstate__()
            del state['__traits_version__']
            state['__agenttype__'] = self._mktypename(node)
            self.agents_db.update(
                    dict(_id=node.id),
                    {'$set': state},
                    upsert=True)

        def recover(self, identifier):
            identifier = int(identifier)
            state = self.agents_db.find_one({'_id': identifier})
            agent_type = \
                jsonpickle.unpickler.loadclass(state.pop('__agenttype__'))
            del state['_id']
            return agent_type(**state)






