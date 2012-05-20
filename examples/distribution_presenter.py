from pynetsym import mathutil
import random
from matplotlib import pyplot as plt


def distribution_gather(distribution, number_of_points):
    points = [distribution() for _i in xrange(number_of_points)]
    points.sort()
    return points

sample = distribution_gather(lambda: random.lognormvariate(1, 1), 10000)
plt.loglog(sample)
plt.show()