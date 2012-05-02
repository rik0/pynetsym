from unittest import TestCase
from pynetsym import core, storage
import gevent

class Agent(core.Agent):
    def __init__(self, identifier, address_book, value=0):
        super(Agent, self).__init__(identifier, address_book)
        self.val = value

    def answer(self):
        self.val = 42
        self.kill()

    def question(self, agent_id):
        self.send(agent_id, 'answer')


class TestAgent(TestCase):
    def setUp(self):
        graph_wrapper = storage.NXGraphWrapper()
        address_book = core.AddressBook(graph_wrapper)
        self.agent_a_id = 'a'
        self.agent_a = Agent(self.agent_a_id, address_book)
        self.agent_b_id = 'b'
        self.agent_b = Agent(self.agent_b_id, address_book)
        self.agent_a.start()
        self.agent_b.start()
        gevent.sleep(0)

    def test_id(self):
        self.assertEqual(self.agent_a_id, self.agent_a.id)
        self.assertEqual(self.agent_b_id, self.agent_b.id)

    def test_send(self):
        self.agent_a.send(self.agent_b_id, 'question',
                agent_id=self.agent_a_id)
        self.agent_a.join()
        self.assertEqual(42, self.agent_a.val)

