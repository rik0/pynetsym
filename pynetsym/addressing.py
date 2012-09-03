
from pynetsym import metautil, node_db

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

    def register(self, agent, identifier):
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

    def resolve(self, identifier):
        """
        Resolves :param: identifier to the actual agent.

        @raise AddressingError: if the agent is not registered.
        """
        pass

    def unregister(self, identifier):
        raise NotImplementedError()

    def list(self):
        return list(self.list_iter())

    def list_iter(self):
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

    def register(self, agent, identifier):
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
                    "Could not remove not registered identifier %r" % (
                    identifier))

    def resolve(self, identifier):
        try:
            return self.name_registry[identifier]
        except KeyError:
            raise AddressingError(
                "Could not find node with address %r." % identifier)

    def list_iter(self):
        return self.name_registry.iterkeys()

    def list(self):
        return self.name_registry.viewkeys()

class ResumingAddressBook(FlatAddressBook):
    def __init__(self, node_db):
        super(ResumingAddressBook, self).__init__()
        self.node_db = node_db

    def resolve(self, identifier):
        try:
            return self.name_registry[identifier]
        except KeyError:
            try:
                node = self.node_db.recover(identifier)
                node._establish_agent()

            except node_db.MissingNode:
                raise AddressingError(
                    "Could not find node with address %r." % identifier)

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

    def register(self, agent, namespace, *rest):
        address_book = self.resolve_namespace(namespace)
        address_book.register(agent, *rest)

    def unregister(self, namespace, *rest):
        address_book = self.resolve_namespace(namespace)
        address_book.unregister(*rest)

    def list_iter(self):
        for namespace, ab in self.namespaces.iteritems():
            for identifier in ab.list():
                yield namespace, identifier


class AutoResolvingAddressBook(NamespacedAddressBook):
    def __init__(self, E={}, **F):
        super(AutoResolvingAddressBook, self).__init__(E, **F)
        self.resolvers = []

    def add_resolver(self, namespace, checker):
        self.resolvers.append((checker, namespace))

    def resolve_identifier(self, identifier):
        for resolver_check, namespace in self.resolvers:
            if resolver_check(identifier):
                return self.resolve_namespace(namespace)
        else:
            raise AddressingError(
                "Could not find namespace for '%s'" % identifier)

    def resolve(self, identifier):
        address_book = self.resolve_identifier(identifier)
        return address_book.resolve(identifier)

    def register(self, agent, identifier):
        address_book = self.resolve_identifier(identifier)
        address_book.register(agent, identifier)

    def unregister(self, identifier):
        address_book = self.resolve_identifier(identifier)
        address_book.unregister(identifier)

    def list_iter(self):
        return itertools.imap(operator.itemgetter(1),
                       super(AutoResolvingAddressBook, self).list_iter())

