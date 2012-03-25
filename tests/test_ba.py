import unittest
from pynetsym.generation_models import barabasi_albert

class TestBA(unittest.TestLoader):
    def testRun(self):
       sim = barabasi_albert.BA()
       sim.run()

