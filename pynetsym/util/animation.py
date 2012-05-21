import os
from os import path

from pynetsym import core
from pynetsym import simulation
from pynetsym import mathutil

from matplotlib import pyplot as plt


class AnimationMaker(core.Agent):
    def __init__(self, identifier, address_book, directory):
        super(AnimationMaker, self).__init__(identifier, address_book)
        self.directory = directory
        self.counter = 0
        self.create_directory()
        self.register_to_clock()

    def create_directory(self):
        os.mkdir(self.directory)

    def register_to_clock(self):
        self.send(simulation.Clock.name, 'register_observer', self.id)

    def ticked(self):
        filename = 'frame%d.png' % self.counter
        filepath = path.join(self.tmp_directory, filename)
        fig = self.make_frame()
        fig.savefig(filepath)
        self.counter += 1

    def finished(self):
        pass


class DegreeDistributionAnimationMaker(AnimationMaker):
    def make_frame(self):
        fig = plt.figure(figsize=(5, 5))
        ax = fig.add_subplot(111)
        graph = self.graph.handle
        dst = mathutil.degrees_to_hist(graph.degree())
        ccdf = mathutil.ccdf(dst)
        ax.loglog(ccdf)
        return fig
