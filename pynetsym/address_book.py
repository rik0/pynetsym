import logging

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
        try:
            self.registry.pop(id_or_agent)
        except KeyError:
            for k, v in self.registry.iteritems():
                if v is id_or_agent:
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