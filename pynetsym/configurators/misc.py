import random

def either_p(cls_a, cls_b, p):
    assert 0 <= p <= 1
    if random.random() < p:
        return cls_a
    else:
        return cls_b
