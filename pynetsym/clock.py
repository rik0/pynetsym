import gevent
from gevent.greenlet import LinkedCompleted
from traits.api import false, Instance, true, List, Int

from .core import Agent
from .termination import TerminationChecker
from .activator import Activator

class BaseClock(Agent):
    name = 'clock'
    activator_can_terminate = false()
    clock_loop_g = Instance(gevent.Greenlet)

    active = true(transient=True)
    observers = List

    def register_observer(self, name):
        self.observers.append(name)

    def unregister_observer(self, name):
        self.observers.remove(name)

    def join(self):
        try:
            return super(BaseClock, self).join()
        except LinkedCompleted:
            return True

    def start_clock(self):
        """
        Here the clock actually starts ticking.
        """
        self.active = True
        self.clock_loop_g = gevent.spawn_link(self.clock_loop)

    def positive_termination(self, originator, motive):
        if originator == TerminationChecker.name:
            self.clock_loop_g.join()

    def clock_loop(self):
        raise NotImplementedError()

    def send_tick(self):
        for observer in self.observers:
            self.send(observer, 'ticked')
        return self.send(Activator.name, 'tick')

    def send_simulation_ended(self):
        return self.send(Activator.name, 'simulation_ended')

    def simulation_end(self):
        self.active = False
        self.send_simulation_ended().get()

    def ask_to_terminate(self):
        return self.send(
            TerminationChecker.name, 'check',
            requester=self.name)


class AsyncClock(BaseClock):
    remaining_ticks = Int

    def clock_loop(self):
        while self.remaining_ticks:
            self.send_tick()
            self.remaining_ticks -= 1
        else:
            self.simulation_end()


class Clock(BaseClock):
    def clock_loop(self):
        while self.active:
            waiting = self.send_tick()
            waiting.get()
            should_terminate = self.ask_to_terminate()
            self.active = not should_terminate.get()
        else:
            self.simulation_end()