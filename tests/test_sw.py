import unittest
from pynetsym.generation_models import watts_strogatz

class TestWS(unittest.TestLoader):
    def testRun(self):
       sim = watts_strogatz.WS()
       sim.run()
