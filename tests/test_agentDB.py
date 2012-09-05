from unittest import TestCase
from pynetsym import core

class TestAgentDB(TestCase):

    def setUp(self):
        self.runtime = core.MinimalAgentRuntime()
        self.node_db = self.runtime.node_db
        self.agent_id = 'agent'
        self.agent = self.runtime.spawn_agent(core.Agent,
                                              identifier=self.agent_id)

    def test_recover(self):
        self.node_db.store(self.agent)
        agent = self.node_db.recover(self.agent_id)
        self.assertEquals(self.agent_id, agent.id)
        self.assertIsInstance(agent, self.agent.__class__)

    def test_store(self):
        self.node_db.store(self.agent)
