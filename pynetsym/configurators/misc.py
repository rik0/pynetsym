import random

def either_p(cls_a, cls_b, p):
    assert 0 <= p <= 1
    def either(configurator, *args):
        if random.random() < p:
            return cls_a(*args)
        else:
            return cls_b(*args)
    return either
