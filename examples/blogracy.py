from pynetsym import core, configurators, simulation
from pynetsym import geventutil
from pynetsym.configurators.misc import either_p
from scipy import stats
import collections
import itertools
import networkx as nx
import pprint
import functools


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

    def __init__(self, author, age, expected_recipients):
        self.index = next(self.counter)
        self.author = author
        self.age = age
        self.expected_recipients = frozenset(expected_recipients)
        self.all_content.append(self)
        self.receivers = set()

    def mark_received(self, by_whom):
        assert by_whom in self.expected_recipients
        self.receivers.add(by_whom)

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
    def avg_received(cls):
        global_missed = 0
        global_expected = 0
        for content in cls.all_content:
            missed = content.expected_recipients - content.receivers
            global_missed += len(missed)
            global_expected += len(content.expected_recipients)
        return float(global_missed) / global_expected


class State(object):
    def __init__(self, node):
        self.node = node


class OfflineState(State):
    def generate(self, age):
        pass

    def update(self, age):
        pass

    def created_content(self, content):
        pass

    def get_new_content(self, since, from_):
        return []


class OnlineState(State):
    def generate(self, age):
        node = self.node
        graph = self.node.graph.handle
        assert isinstance(graph, nx.DiGraph)
        content = Content(node.id, age,
            graph.predecessors_iter(node.id))
        node.send_all(graph.predecessors_iter(node.id),
            'created_content',
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

        contents = node.send_all(require_content_from,
            'get_new_content',
            since=node.most_recently_received(),
            from_=set(graph.successors_iter(node.id)))
        node.receive_contents(contents.flatten())

    def created_content(self, content):
        self.node.contents.append(content)
        # should be mostly ordered, preternaturally fast with timsort
        self.node.contents.sort()

    def get_new_content(self, since, from_):
        contents = self.node.contents
        new_contents = [c for c in contents if c > since and c.author in from_]
        return new_contents


class Node(core.Node):
    def initialize(self):
        self.online_state = OnlineState(self)
        self.offline_state = OfflineState(self)
        self.state = self.offline_state
        self.contents = []

    def generate(self, age):
        self.state = self.online_state
        self.state.generate(age)
        self.send(Activator.name, 'stop_me_at',
            agent=self.id, time=age+1)

    def update(self, age):
        self.state = self.online_state
        self.state.update(age)
        self.send(Activator.name, 'stop_me_at',
            agent=self.id, time=age+1)

    def created_content(self, content):
        self.state.created_content(content)

    def get_new_content(self, since, from_):
        return self.state.get_new_content(since, from_)

    def go_offline(self):
        self.state = self.offline_state

    def receive_contents(self, contents):
        contents.sort()
        for content in contents:
            content.mark_received(self.id)
        self.contents.extend(contents)

    def most_recently_received(self):
        for content in reversed(self.contents):
            if content.author != self.id:
                return content
        else:
            return Content.null


class BittorrentNode(Node):
    def initialize(self):
        super(BittorrentNode, self).initialize()
        self.state = self.online_state

    def go_offline(self):
        pass


class Activator(simulation.Activator):
    activator_options = {'generation_probability', 'update_probability'}
    separator = object()

    def setup(self):
        self.age = 0
        self.to_stop = {}

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
        nodes = self.to_stop.get(self.age, {})
        self.send_all(nodes, 'go_offline')

    def stop_me_at(self, agent, time):
        self.to_stop.setdefault(time, set()).add(agent)

    def generation_stage(self):
        number_of_nodes = self.generation_variate.rvs()
        nodes = self.graph.random_nodes(number_of_nodes)
        self.send_all(nodes, 'generate', age=self.age)

    def update_stage(self):
        number_of_nodes = self.update_variate.rvs()
        nodes = self.graph.random_nodes(number_of_nodes)
        self.send_all(nodes, 'update', age=self.age)


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

if __name__ == '__main__':
    sim = Simulation()
    sim.run(starting_graph=nx.fast_gnp_random_graph(1000, 0.2, directed=True),
        steps=10000)

    print Content.how_many()
    print Content.avg_received()
