import copy
from pynetsym import addressing
from pynetsym import agent_db

import time
import sys
import collections

import gevent
import gevent.event as event
import gevent.queue as queue

from traits import api as t
from pynetsym.error import PyNetSymError
from pynetsym.util import SequenceAsyncResult

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

__all__ = [
    'Agent',
    'Logger',
    'MinimalAgentRuntime',
    'get_logger',
    'Logger'
]


class NoMessage(queue.Empty, PyNetSymError):
    pass


class AgentError(PyNetSymError):
    pass


_M = collections.namedtuple('Message', 'sender payload parameters')


class Message(_M):
    """
    An immutable object that is used to send a message among agents.
    """

    def __repr__(self):
        return '%s:%s%s' % (self.sender, self.payload, self.parameters)

    __str__ = __repr__


class Agent(t.HasTraits):
    """
    An Agent is the basic class of the simulation.

    Agents communicate asynchronously.
    """

    #DEBUG_RECEIVE = True
    #DEBUG_SEND = True

    _address_book = t.Instance(
        addressing.AddressBook, transient=True, allow_none=False)
    _default_queue = t.Instance(
        queue.Queue, transient=True, allow_none=False)
    _greenlet = t.Instance(
        gevent.Greenlet, transient=True, allow_none=False)
    _node_db = t.Instance(
        agent_db.IAgentStorage, transient=True, allow_none=False)

    id = t.Either(t.CInt, t.Str)

    __ = t.PythonValue(transient=True)

    def join(self):
        try:
            return self._greenlet.join()
        except (KeyboardInterrupt, SystemExit) as e:
            print "[%s] I was caught with the hands in the jam!" % self.id
            print self._create_error_text(self._greenlet)
            raise AgentError(e)

    def sleep(self, seconds):
        gevent.sleep(seconds)

    def setup(self):
        """
        Additional initialization before the run loop goes here.

        The default implementation is empty.
        """

    def _compute_identifier(self, identifier):
        if identifier is None:
            try:
                self.id = self.name
            except Exception:
                raise AgentError("%r is not a valid Agent Id." % identifier)
        else:
            self.id = identifier

    def start(self, address_book, agent_db, identifier=None):
        """
        Start executing the agent.

        :param address_book: the address book where the other agents references can be found.
        :type address_book: :class:`addressing.AddressBook`
        :param agent_db: the agent database that is used if this agent needs to be serialized
        :type agent_db: :class:`agent_db.IAgentStorage`
        :param identifier: this agent identifier. It is also added to the address book.
        :type identifier: str | int

        :return: the agent itself
        :rtype: :class:`Agent`
        """
        self._compute_identifier(identifier)
        self._address_book = address_book
        self._address_book.register(self, self.id)
        self._default_queue = queue.Queue()
        self._node_db = agent_db
        self._greenlet = gevent.Greenlet(self._start)

        self._greenlet.link_exception(self.on_error)
        if hasattr(self, 'on_completion'):
            self._greenlet.link_value(self.on_completion)
        self._greenlet.start()
        return self

    @property
    def started(self):
        """
        True if the agent has been started.
        """
        return ((self.id is not None) and
                (self._address_book is not None) and
                (self._greenlet is not None))

    def _revert_start(self, _source):
        self._address_book.unregister(self.id)
        del self._address_book
        del self._default_queue
        del self._node_db
        del self._greenlet

    def _create_error_text(self, source):
        ss = StringIO()
        print >> ss, self
        print >> ss, source
        print >> ss, 'succesful:', source.successful()
        print >> ss, 'value:', source.value
        print >> ss, 'exception:', source.exception
        if self._default_queue is not None:
            print >> ss, 'messages:', self._default_queue.qsize()
            if self._default_queue.qsize():
                import pprint

                pprint.pprint(
                    [message for message, _result in self._default_queue.queue],
                    stream=ss)
        return ss.getvalue()

    def on_error(self, source):
        """
        This handler is called when an error arises in the greenlet executing the agent.

        The default implementation logs the error. Other implementations may
        take different actions.

        :param source: the greenlet where the error originated.
        :type source: gevent.Greenlet
        """
        text = self._create_error_text(source)
        self._get_logger().put_error(self, text)

    def kill(self):
        return self._greenlet.kill()

    def read(self, timeout=None):
        """
        Reads the next message that was sent to this agent.

        :param timeout: can specify a timeout

        :return: (Message, event.AsyncResult)
        :raise: NoMessage if no message arrives after timeout

        .. warning::
            It is not really meant to be called directly unless you are building a runloop.
            Strictly speaking it is not non public, though.
        """
        try:
            entry = self._default_queue.get(timeout=timeout)
            if getattr(self, 'DEBUG_RECEIVE', False):
                self.log_received(entry[0])
            return entry
        except queue.Empty, e:
            raise NoMessage(e)

    def _get_logger(self, stream=sys.stderr):
        return get_logger(self._address_book, self._node_db, stream)

    def send_log(self, message, stream=sys.stdout):
        """
        Logs the message to the specified stream.
        :param message: the message to be logged
        :type message: :class:`Message`
        :param stream: the stream where the message will be printed
        """
        logger = self._get_logger(stream)
        logger.put_log(self.id, message)

    def log_sent(self, payload, receiver):
        """
        Mainly a debug hook that is called every time a messgage is sent,
        if the attribute DEBUG_SEND is True.
        """
        gl = gevent.getcurrent()
        if gl is not self._greenlet:
            message = "{%s} SEND %s to %s" % (
                gl, payload, receiver.id)
        else:
            message = "SEND %s to %s" % (
                payload, receiver.id)
        self.send_log(message)

    def log_received(self, msg):
        """
        Mainly a debug hook that is called every time a message is received,
        if the attribute DEBUG_RECEIVE is True.
        """
        gl = gevent.getcurrent()
        if gl is not self._greenlet:
            message = "RECV {%s} %s" % (gl, msg)
        else:
            message = "RECV %s" % (msg,)
        self.send_log(message)

    def _awaken_agent(self, identifier):
        agent = self._node_db.recover(identifier)
        agent.start(self._address_book, self._node_db, identifier)
        return agent

    def _store_agent(self):
        self._node_db.store(self)
        self._revert_start(self._greenlet)

    def _resolve(self, identifier):
        try:
            receiver = self._address_book.resolve(identifier)
        except addressing.AddressingError, e:
            try:
                receiver = self._awaken_agent(identifier)
            except agent_db.MissingNode:
                raise e
        return receiver

    def _handle_message(self, message, receiver):
        if getattr(self, 'DEBUG_SEND', False):
            self.log_sent(str(message), receiver)
        result = event.AsyncResult()
        receiver.deliver(message, result)
        return result

    def _handle_no_receiver(self, e):
        logger = self._get_logger()
        logger.put_log(self, e.message)
        result = event.AsyncResult()
        result.set_exception(e)
        return result

    def send(self, receiver_id, message_name, **additional_parameters):
        """
        Send a message to the specified agent.

        :param receiver_id: the id of the receiving agent
        :type receiver_id: int|str
        :param message_name: the name of the receiving agent method
        :type message_name: str
        :param `**additional_parameters`: additional parameters to be passed
            to the function
        """
        try:
            receiver = self._resolve(receiver_id)
        except addressing.AddressingError as e:
            result = self._handle_no_receiver(e)
            return result
        else:
            # FIXME: no true message passing semantics!
            message = Message(self.id, message_name, additional_parameters)
            result = self._handle_message(message, receiver)
            return result

    def sync_send(self, receiver_id, message_name, timeout=None,
                  **additional_parameters):
        """
        Like :func:`Agent.send`, but explicitly blocks until the message
            is processed by the receiver.
        """
        return self.send(receiver_id, message_name,
                         **additional_parameters).get(timeout=timeout)

    def _send_all_fixed_params(self, additional_parameters, message_name, receivers):
        message = Message(self.id, message_name, additional_parameters)
        result_sequence = []
        for receiver_id in receivers:
            try:
                receiver = self._resolve(receiver_id)
            except addressing.AddressingError as e:
                result = self._handle_no_receiver(e)
            else:
                result = self._handle_message(message, receiver)
            result_sequence.append(result)
        else:
            return SequenceAsyncResult(result_sequence)

    def _send_all_multi_params(self, additional_parameters, message_name, receivers):
        callable_stuff = {name: func
                          for name, func in additional_parameters.items()
                          if callable(func)}
        result_sequence = []
        for receiver_id in receivers:
            parameters = copy.copy(additional_parameters)
            parameters.update({name: func(receiver_id)
                               for name, func in callable_stuff.items()})
            result = self.send(receiver_id, message_name, **parameters)
            result_sequence.append(result)
        return SequenceAsyncResult(result_sequence)

    def send_all(self, receivers, message_name, **additional_parameters):
        """
        Like :func:`Agent.send`, but sends the messages to every agent in receivers.

        If some parameter in additional_parameters is a callable, it is called
        for each agent in receivers with the agent id as a parameter and
        the return value is sent instead of the callable.

        This is used for customizing the message sent to each agent.

        :param receivers: A collection of receivers
        :type receivers: iterable
        """
        if any(callable(param)
               for param in additional_parameters.values()):
            return self._send_all_multi_params(
                additional_parameters, message_name, receivers)
        else:
            return self._send_all_fixed_params(
                additional_parameters, message_name, receivers)

    def sync_send_all(self, receivers, message_name, **additional_parameters):
        """
        Like :func:`Agent.send_all`, but explicitly blocks until the message
            is processed by the receiver.
        """
        return self.send_all(receivers, message_name,
                             **additional_parameters).get()

    def process(self, message, result):
        """
        Processes the message.

        This means calling the message payload with self as argument.

        .. warning::
            This is not meant to be used direclty, unless you are writing
            a runloop.

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
        result.set(value)

    def can_be_collected(self):
        """
        Override this if the Agent should not be collected (i.e., serialized
            and put to sleep in the agent_db)
        """
        return False

    def _start(self):
        """
        Override to customize the agent's behavior.
        """
        self.setup()
        return self.run_loop()

    def run_loop(self):
        """
        Agent main run loop.

            1. read a message from the queue
            2. process the message and elaborate the answer
            3. if the answer is not None, send it to the original message
            4. release control
        """
        while 1:
            try:
                message, result = self.read(timeout=0.01)
                self.process(message, result)
                del message, result
            except NoMessage:
                if self.can_be_collected():
                    self._store_agent()
                    return self
            finally:
                self.cooperate()

    def unsupported_message(self, name, **additional_parameters):
        """
        Prints out something if we received a message we could not process.

        This is meant to be overridden, if a different behavior is desired.
        """
        print (
            ('%s received "%s" message with parameters %s: '
             'could not process.') %
            (self, name, additional_parameters))

    def deliver(self, message, result):
        """
        Delivers message to this agent.

        Typically this is not called directly by other agents.
        Use the source agent send message, instead.

        :param message: the message
        :type message: Message
        :param result: dataflow-like object we use to feed-back answers
        :type result: event.AsyncResult
        """
        self._default_queue.put((message, result))

    def cooperate(self):
        """
        Release control.

        Usually this is not explicitly needed.
        If in doubt, do not use it.
        """
        gevent.sleep()

    def __str__(self):
        return '%s(%s)' % (self.__class__.__name__, self.id)

    __repr__ = __str__


class Logger(Agent, t.SingletonHasTraits):
    """
    A system agents that is used to log stuff.

    The agents expect at least one logger to be running.
    Prebuilt agent environments (such as the :class:`simulation.Simulation`)
    create a Logger.
    """
    DEBUG_RECEIVE = False
    DEBUG_SEND = False

    name = 'logger'
    standard_stderr = sys.stderr

    def __init__(self, stream, error_stream=standard_stderr):
        self.stream = stream
        self.error_stream = error_stream

    def log_entry(self, sender, message, when=None):
        """
        Creates an entry in the log.
        """
        if when is None:
            full_line = '[%s: r%.3f] %s\n' % (sender, time.clock(), message)
        else:
            full_line = '[%s: s%.3f] %s\n' % (sender, when, message)
        self.stream.write(full_line)

    def put_log(self, sender, message):
        """
        The other agent can send a "put_log" message to the logger to
        print a message on the default stream.
        """
        result = event.AsyncResult()
        message = Message(sender,
                          'log_entry',
                          dict(sender=sender, message=message,
                               when=time.clock()))
        self.deliver(message, result)

    def put_error(self, sender, text):
        """
        The other agent can send a "put_log" message to the logger to
        print an error on the default stream.
        """
        result = event.AsyncResult()
        message = Message(sender, 'error_message',
                          dict(sender=sender, text=text))
        self.deliver(message, result)

    def stop_receiving(self):
        """
        Send this message for killing the logger.
        """
        while 1:
            try:
                message, result = self.read(timeout=0.01)
                self.process(message, result)
                del message, result
            except NoMessage:
                break
        self.kill()

    def error_message(self, sender, text):
        """
        This method actually writes on the stream.
        """
        ss = StringIO()
        ss.write('=' * 10)
        ss.write(str(sender))
        ss.write('=' * 10)
        ss.write('\n')
        ss.write(text)
        ss.write('=' * 80)
        ss.write('\n')
        self.error_stream.write(ss.getvalue())


def get_logger(address_book, node_db, stream=sys.stderr):
    """
    Gets the default logger.

    Factory function.
    """
    logger = Logger(stream)
    if not logger.started:
        logger.start(address_book, node_db)
    return logger


def _default_agent_db_factory():
    return agent_db.AgentDB(
        agent_db.PythonPickler(), dict())


class MinimalAgentRuntime(object):
    """
    Use this to establish a minimal agent runtime.

    If a more elaborate runtime is being used, this is not needed.
    Not necessary for Simulations: the Simulation class is just a more
    elaborate runtime.
    """

    def __init__(self, address_book_factory=addressing.FlatAddressBook,
            agent_db_factory=_default_agent_db_factory):
        self.address_book = address_book_factory()
        self.node_db = agent_db_factory()
        self.logger = self.create_agent(Logger, stream=sys.stdout)

    def create_agent(self, cls, **more_stuff):
        return cls(**more_stuff)

    def spawn_agent(self, cls, identifier=None, **more_stuff):
        agent = self.create_agent(cls, **more_stuff)
        self.start_agent(agent, identifier)
        return agent

    def start_agent(self, agent, identifier=None):
        agent.start(self.address_book, self.node_db, identifier)


GreenletExit = gevent.GreenletExit
