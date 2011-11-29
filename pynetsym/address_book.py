from exceptions import Exception, KeyError
import logging
from pynetsym.core import Agent

__author__ = 'enrico'

class AddressingError(Exception):
    def __init__(self, *args, **kwargs):
        super(AddressingError, self).__init__(*args, **kwargs)


class AddressBook(object):
    def __init__(self):
        self.registry = {}

    def register(self, identifier, agent, check=None):
        if check is None:
            self._log_if_rebind(identifier, agent)
            self.registry[identifier] = agent
        elif check(identifier, agent):
            self.registry[identifier] = agent


    def unregister(self, id_or_agent):
        if isinstance(id_or_agent, Agent):
            self._unregister_by_value(id_or_agent)
        else:
            self.registry.pop(id_or_agent)

    def _unregister_by_value(self, agent):
        for k, v in self.registry.iteritems():
            if v is agent:
                break
        else:
            return
        self.registry.pop(k)

    def resolve(self, identifier):
        try:
            return self.registry[identifier]
        except KeyError:
            raise AddressingError

    def _log_if_rebind(self, identifier, agent):
        try:
            old_agent = self.registry[identifier]
            if old_agent is agent:
                pass
            else:
                logging.warning(
                    "Rebinding agent %s from %s to %s",
                    identifier, old_agent, agent)
        except KeyError:
            # ok
            pass
        return True