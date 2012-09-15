import functools


def notifies(event, kind):
    def add_notifications(func):
        def aux(self, *args, **kwargs):
            try:
                ## execute the function
                res = func(self, *args, **kwargs)
            except Exception:
                ## exceptions in the function body are propagated
                raise
            else:
                observers = self.observers.get((event, kind), ())
                for observer, suppress_exception in observers:
                    try:
                        observer(event, kind, self, *args, **kwargs)
                    except Exception, e:
                        if suppress_exception:
                            pass
                        else:
                            raise e
                return res  # TODO: recently added: check if it works
        functools.update_wrapper(aux, func)
        return aux
    return add_notifications


def notifier(cls):
    observers = {}

    def register_observer(self, observer, event, kind,
                          suppress_exceptions=False):
        current_observers = observers.setdefault((event, kind), set())
        current_observers.add((observer, suppress_exceptions))

    def unregister_observer(self, observer, event=None, kind=None):
        raise NotImplementedError()

    cls.register_observer = register_observer
    cls.unregister_observer = unregister_observer
    cls.observers = property(lambda self: observers)
    return cls
