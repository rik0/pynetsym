from unittest import TestCase
from pynetsym import core

import traits.api as t

class Agent(core.Agent):
    val = t.Int(0)

    def answer(self):
        self.val = 42
        self.kill()

    def question(self, agent_id):
        self.send(agent_id, 'answer')


class TestAgent(TestCase):
    def setUp(self):
        self.runtime = core.MinimalAgentRuntime()
        self.agent_a_id = 'a'
        self.agent_b_id = 'b'
        self.agent_a = self.runtime.spawn_agent(Agent, self.agent_a_id)
        self.agent_b = self.runtime.spawn_agent(Agent, self.agent_b_id)

    def test_id(self):
        self.assertEqual(self.agent_a_id, self.agent_a.id)
        self.assertEqual(self.agent_b_id, self.agent_b.id)

    def test_send(self):

        self.agent_a.send(self.agent_b_id, 'question',
                agent_id=self.agent_a_id)
        self.agent_a.join()
        self.assertEqual(42, self.agent_a.val)

