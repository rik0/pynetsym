import unittest
from pynetsym.generation_models import bpa

class TestBPA(unittest.TestLoader):
    def testRun(self):
       sim = bpa.BPA()
       sim.run()
