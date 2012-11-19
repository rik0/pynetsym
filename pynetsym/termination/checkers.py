from pynetsym import core


class TerminationChecker(core.Agent):
    name = 'termination_checker'

    def __init__(self, graph, conditions):
        self.graph = graph
        self.conditions = list(conditions)
        self.active = True

    def add_condition(self, condition):
        self.conditions.append(condition)

    def check(self, requester):
        for condition in self.conditions:
            check = condition.check(self.graph)
            if check:
                self.motive = condition.motive
                self.active = False
                self.send(requester, 'positive_termination',
                          originator=self.name,
                          motive=self.motive)
                return True
        else:
            return False

    def _start(self):
        self.setup()
        while self.active:
            message, result = self.read()
            self.process(message, result)
            self.cooperate()
        else:
            return self.motive
