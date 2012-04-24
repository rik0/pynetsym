from pynetsym import core


class TerminationChecker(core.Agent):
    name = 'termination_checker'

    def __init__(self, graph, address_book, *conditions):
        super(TerminationChecker, self).__init__(self.name, address_book)
        self.graph = graph
        self.conditions = list(conditions)
        self.active = True

    def add_condition(self, condition):
        self.condition.append(condition)

    def check(self):
        for condition in self.conditions:
            check = condition.check(self.graph)
            if check:
                self.motive = condition.motive
                self.active = False
                return check
        else:
            return False

    def _run(self):
        while self.active:
            message, result = self.read()
            self.process(message, result)
            self.cooperate()
        else:
            return self.motive

