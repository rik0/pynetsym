import abc

from pynetsym import metautil

class AddressingError(Exception):
    """
    Error signaling that something with the addressing of
    a message went wrong.

    """

    def __init__(self, *args, **kwargs):
        super(AddressingError, self).__init__(*args, **kwargs)

get_root_address_book, \
set_root_address_book = metautil.encapsulate_global('root', {})

class AddressBook(object):
    """
    The Address book holds information on every agent in the system.

    An agent that is not in the AddressBook is virtually unreachable.
    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def register(self, identifier, agent):
        """
        Binds the identifier with the agent

        @param identifier: the identifier to bind the agent to
        @type identifier: hashable
        @param agent: the agent to bind
        @type agent: Agent
        @raise AddressingError: if identifier is already bound
        @raise TypeError: if the identifier has a type that is not recognized
            by the AddressBook
        """
        pass

    @abc.abstractmethod
    def resolve(self, identifier):
        """
        Resolves :param: identifier to the actual agent.

        @raise AddressingError: if the agent is not registered.
        """
        pass

    def unregister(self, identifier):
        raise NotImplementedError()
    
    def list(self):
        raise NotImplementedError()
    

class FlatAddressBook(AddressBook):
    """
    The Address book holds information on agents.

    This AddressBook uses a flat namespace.
    """

    def __init__(self):
        """
        Creates the address book.
        """
        self.name_registry = {}

    def register(self, identifier, agent):
        if (identifier in self.name_registry
                and self.name_registry[identifier] is not agent):
            raise AddressingError(
                    "Could not rebind agent %r to identifier %r." % (
                        agent, identifier))
        else:
            self.name_registry[identifier] = agent

    def unregister(self, identifier):
        try:
            del self.name_registry[identifier]
        except KeyError:
            raise AddressingError(
                    "Could not remove unregistered identifier %r" % (
                    identifier))

    def resolve(self, identifier):
        try:
            return self.name_registry[identifier]
        except KeyError:
            raise AddressingError(
                "Could not find node with address %r." % identifier)

    def list(self):
        return self.name_registry.viewkeys()
    
class NamespacedAddressBook(AddressBook):
    def __init__(self, E={}, **F):
        self.namespaces = {}
        self.namespaces.update(E, **F)

    def resolve_namespace(self, namespace):
        try:
            return self.namespaces[namespace]
        except KeyError:
            raise AddressingError(
                "Could not find specified namespace '%s'" % namespace)

    def unregister_namespace(self, namespace):
        try:
            del self.namespaces[namespace]
        except KeyError:
            raise AddressingError(
                "Could not find specified namespace '%s'" % namespace)

    def register_namespace(self, namespace, address_book):
        try:
            current = self.namespaces[namespace]
            if current is not address_book:
                raise AddressingError(
                    "Could not rebind address_book %r to namespace %r." % (
                        address_book, namespace))
        except KeyError:
            self.namespaces[namespace] = address_book
    
    def resolve(self, namespace, *rest):
        address_book = self.resolve_namespace(namespace)
        return address_book.resolve(*rest)

    def register(self, namespace, *rest):
        address_book = self.resolve_namespace(namespace)
        address_book.register(*rest)
