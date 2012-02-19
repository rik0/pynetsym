"""
Some generations models bundled with pynetsym.

Use these as a starting point to learn what you can do.
"""
import pynetsym

def load_simulation(name):
    """
    Loads a simulation by name. A simulation instance is returned.
    @param name: the name of the simulation (in generation_nodels).
    @type name: str
    @return: the simulation instance
    @rtype: simulation.Simulation
    """
    import importlib
    module = importlib.import_module(name)
    for k, v in module:
        if issubclass(v, pynetsym.simulation.Simulation):
            sim = v()
            return sim