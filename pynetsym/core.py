from pynetsym import geventutil, addressing, storage
import collections
import gevent
import gevent.event as event
import gevent.queue as queue

from traits import api as t

class NoMessage(queue.Empty):
    pass

_M = collections.namedtuple('Message', 'sender payload parameters')

class Message(_M):
    """
    An immutable object that is used to send a message among agents.
    """


class Agent(t.HasTraits):
    """
    An Agent is the basic class of the simulation. Agents communicate
    asynchronously with themselves.
    """

    _address_book = t.Trait(addressing.AddressBook, transient=True)
    _default_queue = t.Trait(queue.Queue, transient=True)
    _greenlet = t.Trait(gevent.Greenlet, transient=True)

    __ = t.PythonValue(transient=True)

    id = t.PythonValue

    def establish_agent(self, address_book):
        self._address_book = address_book
        self._address_book.register(self, self.id)
        self._default_queue = queue.Queue()
        self._greenlet = gevent.Greenlet(self._start)

    def free_agent(self):
        self._address_book.unregister(self.id)
        del self._address_book
        del self._default_queue
        del self._greenlet

    @classmethod
    def create_agent(cls, class_=None, **kwargs):
        class_ = cls if class_ is None else class_
        agent = class_(**kwargs)
        return agent


    def __init__(self, identifier, address_book):
        """
        Initializes the Agent object setting variables and registering
        the agent in the address book.

        @param identifier: the identifier the agent has in the system
        @type identifier: int|str
        @param address_book: the address book where we want to register
        @type address_book: AddressBook
        @param error_level: describe what should happen when a message
            cannot be delivered
        @type error_level: int (IGNORE|LOG_ERROR|EXCEPTION)
        @return: the Agent
        """
        self.id = identifier
        self.establish_agent(address_book)

    def deliver(self, message, result):
        """
        Delivers message to this agent.
        @param message: the message
        @type message: Message
        @param result: dataflow-like object we use to feed-back answers
        @type result: event.AsyncResult
        """
        self._default_queue.put((message, result))

    def cooperate(self):
        """
        Release control
        """
        gevent.sleep()

    def join(self):
        return self._greenlet.join()

    def link_value(self, *args):
        return self._greenlet.link_value(*args)

    def link_exception(self, *args):
        return self._greenlet.link_exception(*args)

    def link(self, *args):
        return self._greenlet.link(*args)

    def unlink(self, *args):
        return self._greenlet.unlink(*args)

    def sleep(self, seconds):
        gevent.sleep(seconds)

    def _start(self):
        return self.run_loop()

    def start(self):
        self._greenlet.start()

    def kill(self):
        return self._greenlet.kill()

    def read(self, timeout=None):
        """
        Reads the next message that was sent to this agent.

        @param timeout: can specify a timeout
        @attention: It is not really meant to be called directly unless you are building a runloop.
            Strictly speaking it is not non public, though.
        @return: (Message, event.AsyncResult)
        @raise: NoMessage if no message arrives after timeout
        """
        try:
            entry = self._default_queue.get(timeout=timeout)
            if getattr(self, 'DEBUG_RECEIVE', False):
                self.log_received(entry[0])
            return entry
        except queue.Empty, e:
            raise NoMessage(e)

    def log_received(self, msg):
        gl = gevent.getcurrent()
        print '[', gl, ']', self.id, ': got', msg.payload, 'from', msg.sender

    def send_all(self, receivers, message, **additional_parameters):
        return geventutil.SequenceAsyncResult(
            [self.send(receiver_id, message, **additional_parameters)
             for receiver_id in receivers])

    def send(self, receiver_id, message_name, **additional_parameters):
        """
        Send a message to the specified agent.

        @param receiver_id: the id of the receiving agent
        @param message_name: the name of the receiving agent method or
            a function taking the agent as its first argument (unbound
            methods are just perfect).
        @param additional_parameters: additional parameters to be passed
            to the function
        """
        receiver = self._address_book.resolve(receiver_id)
        message = Message(self.id, message_name, additional_parameters)
        if getattr(self, 'DEBUG_SEND', False):
            self.log_message(message_name, receiver)
        result = event.AsyncResult()
        receiver.deliver(message, result)
        return result

    def log_message(self, payload, receiver):
        gl = gevent.getcurrent()
        print '[', gl, '] Sending', payload, 'from', self.id, 'to', receiver.id

    def process(self, message, result):
        """
        Processes the message. This means calling the message payload with
        self as argument.

        """
        action_name = message.payload
        try:
            bound_method = getattr(self, action_name)
        except AttributeError:
            value = self.unsupported_message(
                action_name, **message.parameters)
        else:
            value = bound_method(**message.parameters)
            del bound_method
        if isinstance(value, Exception):
            result.set_exception(value)
        else:
            result.set(value)

    def run_loop(self):
        """
        Agent main run loop.

            1. read a message from the queue
            2. process the message and elaborate the answer
            3. if the answer is not None, send it to the original message
            4. release control

        The format of answer shall be either:
            1. a string indicating the message name to be send
            2. a tuple where the first element is the name of the
                message to be sent and the second element is a
                dictionary of additional parameters that will be
                passed along.

        @attention: checks regarding message_processor and similar
            are not made
        """
        while 1:
            message, result = self.read()
            self.process(message, result)
            del message, result
            self.cooperate()
        return self

    def unsupported_message(self, name, **additional_parameters):
        """
        Prints out something if we received a message we could not process.
        """
        print (
            ('%s received "%s" message with parameters %s: '
             'could not process.') %
            (self, name, additional_parameters))

    def __str__(self):
        return '%s(%s)' % (self.__class__.__name__, self.id)


class Node(Agent):
    """
    A Node in the social network.
    """

    graph = t.Trait(storage.GraphWrapper, transient=True)
    #_ = t.Disallow()


    def __init__(self, identifier, address_book, graph):
        """
        Create a Node in the network.
        @param identifier: the identifier to bind the Node to
        @type identifier: int|str
        @param address_book: the address book where we want to register
        @type address_book: AddressBook
        @param graph: the graph backing the social network
        @type graph: storage.GraphWrapper
        @return: the Node
        """
        super(Node, self).__init__(identifier, address_book)
        self.graph = graph

    def __str__(self):
        return 'Node-%s' % (self.id, )

    def link_to(self, criterion_or_node):
        """
        Sends an 'accept_link' message to the specified node.

        @param criterion_or_node: The node to link may be an identifier
            or a callable extracting the node from the graph
        @type criterion_or_node:
            id | callable(L{graph<graph.Graph>}) -> L{Node<Node>}
        @return: an asyncronous value representing whether the
            connection succeeded or not.
        """
        if callable(criterion_or_node):
            target_node = criterion_or_node(self.graph)
        else:
            target_node = criterion_or_node
        return self.send(target_node, 'accept_link',
                         originating_node=self.id)

    def unlink_from(self, criterion_or_node):
        """
        Sends a 'drop_link' message to the specified node.

        @param criterion_or_node: The node to link may be an identifier
            or a callable extracting the node from the graph
        @type criterion_or_node:
            id | callable(L{graph<graph.Graph>}) -> L{Node<Node>}
        @return: None
        """
        if callable(criterion_or_node):
            target_node = criterion_or_node(self.graph.handle)
        else:
            target_node = criterion_or_node
        self.send(target_node, 'drop_link',
                  originating_node=self.id)

    def accept_link(self, originating_node):
        """
        Accepts an 'accept_link' message (modifying the network).

        @param originating_node: the node that required the connection
        @type originating_node: int
        """
        self.graph.add_edge(originating_node, self.id)
        return True

    def drop_link(self, originating_node):
        """
        Accepts a 'drop_link' message (modifying the network).

        @param originating_node: the node that required the drop
        @type originating_node: int
        """
        self.graph.remove_edge(originating_node, self.id)
        return True

    def can_be_collected(self):
        """
        Override this if the Agent should not be collected
        """
        return True

    def run_loop(self):
        while 1:
            try:
                message, result = self.read(timeout=0.01)
                self.process(message, result)
                del message, result
                self.cooperate()
            except NoMessage:
                if self.can_be_collected():
                    return self
        return self