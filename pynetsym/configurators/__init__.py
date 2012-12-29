__all__ = [
    'Either',
    'IConfigurator',
    'AbstractConfigurator',
    'BasicConfigurator',
    'BasicH5Configurator',
]



from .predicates import Either
from .interface import IConfigurator
from .basic import AbstractConfigurator, BasicConfigurator
from .h5_configurator import BasicH5Configurator
try:
    import networkx
    del networkx
except ImportError:
    pass
else:
    from nx_configurator import NXGraphConfigurator
    __all__.append('NXGraphConfigurator')


