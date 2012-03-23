from unittest import TestCase
from pynetsym import core, backend

class TestAgent(TestCase):
    def setUp(self):
        graph_wrapper = backend.NXGraphWrapper()
        address_book = core.AddressBook(graph_wrapper)
        self.agent_a_id = 'a'
        self.agent_a = core.Agent(self.agent_a_id, address_book)
        self.agent_b_id = 'b'
        self.agent_b = core.Agent(self.agent_b_id, address_book)
        self.agent_a.start()
        self.agent_b.start()

    def test_id(self):
        self.assertEqual(self.agent_a_id, self.agent_a.id)
        self.assertEqual(self.agent_b_id, self.agent_b.id)

    def test_deliver(self):
        def answer(node_a):
            self.value = 42
            node_a.kill()

        message = core.Message(None, answer)
        self.agent_a.deliver(message)
        self.agent_a.join()
        self.assertEqual(42, self.value)

    def test_send(self):
        self.value = None

        def question(node_b):
            def answer(node_a):
                self.value = 42
                node_a.kill()

            return answer

        self.agent_a.send(self.agent_b_id, question)
        self.agent_a.join()
        self.assertEqual(42, self.value)




