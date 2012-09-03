from pynetsym import geventutil, addressing, node_db

import collections
import gevent
import gevent.event as event
import gevent.queue as queue

import greenlet

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

    _address_book = t.Instance(
        addressing.AddressBook, transient=True, allow_none=False)
    _default_queue = t.Instance(
        queue.Queue, transient=True, allow_none=False)
    _greenlet = t.Instance(
        gevent.Greenlet, transient=True, allow_none=False)
    _node_db = t.Instance(
        node_db.NodeDB, transient=True, allow_none=False)

    initialize = t.false(transient=True) # check me!

    id = t.Either(t.Int, t.Str)

    __ = t.PythonValue(transient=True)

#    @classmethod
#    def create_agent(cls, class_=None, **kwargs):
#        class_ = cls if class_ is None else class_
#        agent = class_(**kwargs)
#        return agent

    def _awaken_agent(self, identifier):
        node = self._node_db.recover(identifier)
        node._establish_agent(self._address_book, self._node_db)
        return node

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

    def sleep(self, seconds):
        gevent.sleep(seconds)

    def setup(self):
        """
        Additional initialization before the run loop goes here.
        """

    def _start(self):
        """
        Override to customize the agent's behavior.
        """
        self.setup()
        return self.run_loop()

    def _free_agent(self):
        self._address_book.unregister(self.id)
        del self._address_book
        del self._default_queue
        del self._greenlet

    def start(self, address_book, node_db, identifier=None):
        if identifier is None and hasattr(self, 'name'):
            self.id = self.name
        else:
            self.id = identifier
        self._address_book = address_book
        self._address_book.register(self, self.id)
        self._default_queue = queue.Queue()
        self._node_db = node_db
        self._greenlet = gevent.Greenlet(self._start)
        self._greenlet.link_exception(self.boo)

        self._greenlet.start()

    def boo(self, what):
        print self
        print what

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

    def _resolve(self, identifier):
        try:
            receiver = self._address_book.resolve(identifier)
        except addressing.AddressingError, e:
            try:
                receiver = self._awaken_agent(identifier)
            except node_db.MissingNode:
                raise e
        return receiver

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
        receiver = self._resolve(receiver_id)
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
            raise value
            result.set_exception(value)
        else:
            result.set(value)

    def can_be_collected(self):
        """
        Override this if the Agent should not be collected
        """
        return False

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
            try:
                message, result = self.read(timeout=0.01)
                self.process(message, result)
                del message, result
                self.cooperate()
            except NoMessage:
                if self.can_be_collected():
                    print 'collecting'
                    return self
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


