from pynetsym import core, NodeManager
from pynetsym.termination import TerminationChecker
from pynetsym.util import gather_from_ancestors, extract_subdictionary, SequenceAsyncResult

class Activator(core.Agent):
    """
    The Activator chooses what happens at each step of the simulation.

    The tick method is called at each simulation step. The default behavior
    is to call choose_node to select a random node and send it an activate
    message.

    tick, simulation_ended and choose_node are meant to be overrode by
    implementations.
    """
    name = 'activator'
    activator_options = {'graph'}

    def __init__(self, graph, **additional_arguments):
        activator_options = gather_from_ancestors(
            self, 'activator_options')
        activator_arguments = extract_subdictionary(
            additional_arguments,
            activator_options)
        self.graph = graph
        vars(self).update(activator_arguments)

    def activate_nodes(self):
        node_ids = self.nodes_to_activate()
        for node_id in node_ids:
            self.send(node_id, 'activate')

    def destroy_nodes(self):
        self.dying_nodes = self.nodes_to_destroy()
        for node_id in self.dying_nodes:
            # notice: this is "beautifully" queued
            self.send(node_id, 'kill')

    def create_nodes(self):
        to_create = self.nodes_to_create()
        node_ids = SequenceAsyncResult(
            [self.send(NodeManager.name, 'create_node',
                       cls=node_class, parameters=node_parameters)
             for node_class, node_parameters in to_create])
        self.fresh_nodes = node_ids.get()

    def simulation_ended(self):
        return self.send(NodeManager.name, 'simulation_ended').get()

    def tick(self):
        self.destroy_nodes()
        self.create_nodes()
        self.activate_nodes()

    def signal_termination(self, reason):
        self.send(TerminationChecker.name, 'require_termination',
                reason=reason).get()

    def nodes_to_activate(self):
        return [self.graph.random_selector.random_node()]

    def nodes_to_destroy(self):
        return {}

    def nodes_to_create(self):
        return {}


class SyncActivator(Activator):
    """
    This Activator variant always waits for the nodes to acknowledge the
    activate message, thus making it essentially serial.
    """

    def activate_nodes(self):
        node_ids = self.nodes_to_activate()
        for node_id in node_ids:
            done = self.send(node_id, 'activate')
            done.get()