from pynetsym import core, configurators, simulation
from pynetsym.configurators.misc import either_p
from scipy import stats
import numpy as np
import collections
import functools
import itertools
import networkx as nx
import pprint


UPDATE_PARAM = 1. / 48
CREATE_CONTENT_PARAM = 1. / 48


def probability(str_):
    p = float(str_)
    if p < 0. or p > 1.:
        raise ValueError("p=%s is not 0 <= p <= 1.")
    else:
        return p


def add_null_object(*args):
    def attr_setter(cls):
        cls.null = cls(*args)
        return cls
    return attr_setter


@add_null_object(None, -1, [])
@functools.total_ordering
class Content(object):
    counter = itertools.count()
    all_content = []

    @classmethod
    def insert_into_stats(cls, content):
        if content.index > 0:
            cls.all_content.append(content)

    def __init__(self, author, age, expected_recipients):
        self.index = next(self.counter)
        self.author = author
        self.age = age
        self.expected_recipients = frozenset(expected_recipients)
        self.receivers = set()
        self.insert_into_stats(self)

    def mark_received(self, by_whom):
        assert by_whom in self.expected_recipients
        self.receivers.add(by_whom)

    @property
    def missing_receivers(self):
        return self.expected_recipients - self.receivers

    def success_rate(self):
        if self.expected_recipients:
            return float(len(self.receivers))/len(self.expected_recipients)
        else:
            return 1.

    def __repr__(self):
        return ('Content{{index={}, author={}, '
            'age={}, followers={}, received={}}}').format(
                self.index, self.author, self.age,
                self.expected_recipients, self.receivers)

    def __lt__(self, other):
        if self.index < other.index:
            return True
        else:
            return False

    def __eq__(self, other):
        try:
            return self.index == other.index
        except AttributeError:
            raise ValueError('Cannot compare {} with {}.'.format(self, other))

    @classmethod
    def how_many(cls):
        return len(cls.all_content)

    @classmethod
    def average_success_rate(cls):
        return np.average([c.success_rate() for c in cls.all_content])


class State(object):
    def __init__(self, node):
        self.node = node


class OfflineState(State):
    def generate(self, age):
        pass

    def update(self, age):
        pass

    def pushing_new_content(self, content):
        pass

    def send_me_new_content(self, since, from_):
        return []


class OnlineState(State):
    def generate(self, age):
        node = self.node
        graph = self.node.graph.handle
        assert isinstance(graph, nx.DiGraph)
        content = Content(node.id, age,
            graph.predecessors_iter(node.id))
        node.send_all(graph.predecessors_iter(node.id),
            'pushing_new_content',
            content=content)

    def update(self, age):
        node = self.node
        graph = self.node.graph.handle
        assert isinstance(graph, nx.DiGraph)
        require_content_from = set(graph.successors_iter(node.id))

        for followee in graph.successors_iter(node.id):
            for follower in graph.predecessors_iter(followee):
                if follower != node.id:
                    require_content_from.add(follower)

        node.send_all(require_content_from,
            'send_me_new_content',
            since=node.most_recently_received(),
            from_=set(graph.successors_iter(node.id)),
            to=node.id)

    def pushing_new_content(self, content):
        self.node.receive_content(content)

    def send_me_new_content(self, since, from_):
        contents = self.node.contents
        new_contents = [c for c in contents if c > since and c.author in from_]
        return new_contents


class Node(core.Node):
    def initialize(self):
        self.online_state = OnlineState(self)
        self.offline_state = OfflineState(self)
        self._state = self.offline_state
        self.contents = []

    def generate(self, age):
        self.go_online()
        self._state.generate(age)
        return self.id, 1

    def update(self, age):
        self.go_online()
        self._state.update(age)
        return self.id, 1

    def pushing_new_content(self, content):
        self._state.pushing_new_content(content)

    def send_me_new_content(self, since, from_, to):
        contents = self._state.send_me_new_content(since, from_)
        self.send(to, 'receive_contents', contents=contents)

    def go_offline(self):
        self._state = self.offline_state

    def go_online(self):
        self._state = self.online_state

    def receive_contents(self, contents):
        contents.sort()
        for content in contents:
            content.mark_received(self.id)
        self.contents.extend(contents)

    def receive_content(self, content):
        content.mark_received(self.id)
        self.contents.append(content)
        self.contents.sort()

    def most_recently_received(self):
        for content in reversed(self.contents):
            if content.author != self.id:
                return content
        else:
            return Content.null


class BittorrentNode(Node):
    def initialize(self):
        super(BittorrentNode, self).initialize()
        self._state = self.online_state
        self.offline_state = self.online_state

    def go_offline(self):
        pass

    def go_online(self):
        pass


class Activator(simulation.Activator):
    activator_options = {'generation_probability', 'update_probability'}
    separator = object()

    def setup(self):
        self.age = 0
        self.to_stop = collections.defaultdict(set)

    def initialize_variates(self):
        number_of_nodes = self.graph.number_of_nodes()
        self.generation_variate = stats.binom(
            number_of_nodes, self.generation_probability)
        self.update_variate = stats.binom(
            number_of_nodes, self.update_probability)

    def tick(self):
        self.initialize_variates()
        # todo... check what we have to do when stuff is awake or not
        self.put_to_sleep()
        self.generation_stage()
        self.update_stage()
        self.next_age()

    def next_age(self):
        self.age += 1

    def put_to_sleep(self):
        nodes = self.to_stop[self.age]
        self.send_all(nodes, 'go_offline')

    def mark_for_offline(self, seq):
        for node_id, steps in seq:
            time = self.age + steps
            self.to_stop[time].add(node_id)

    def generation_stage(self):
        number_of_nodes = self.generation_variate.rvs()
        nodes = self.graph.random_nodes(number_of_nodes)
        answers = self.send_all(nodes, 'generate', age=self.age)
        self.mark_for_offline(answers.get())


    def update_stage(self):
        number_of_nodes = self.update_variate.rvs()
        nodes = self.graph.random_nodes(number_of_nodes)
        answers = self.send_all(nodes, 'update', age=self.age)
        self.mark_for_offline(answers.get())


class Simulation(simulation.Simulation):
    command_line_options = (
        ('--generation-probability',
            dict(type=probability, default=CREATE_CONTENT_PARAM)),
        ('--update-probability',
            dict(type=probability, default=UPDATE_PARAM)),
    )

    activator_type = Activator
    graph_options = dict(graph=nx.DiGraph())

    class configurator_type(configurators.StartingNXGraphConfigurator):
        initialize = True
        node_cls = either_p(Node, BittorrentNode, 0.77)
        node_options = {}


def main(starting_graph, steps=100):
    sim = Simulation()
    sim.run(starting_graph=starting_graph, steps=steps)
    return sim.handle


if __name__ == '__main__':
    #starting_graph = nx.fast_gnp_random_graph(100, 0.2, directed=True)
    # starting_graph = nx.complete_graph(100, create_using=nx.DiGraph())
    starting_graph = nx.powerlaw_cluster_graph(1000, 8, 0.1)

    graph = main(starting_graph)

    #pprint.pprint(Content.all_content)
    print Content.how_many()
    print Content.average_success_rate()
    print 'Bittorrent nodes', len([node for node, data in graph.nodes(data=True)
        if isinstance(data['agent'], BittorrentNode)])

