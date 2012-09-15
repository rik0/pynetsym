import random

def choice_from_iter(iterator, max_value):
    if max_value <= 0:
        raise ValueError(
                ("Max should be positive, got %s instead" % max_value))
    chosen_index = random.randrange(0, max_value)
    for index, item in enumerate(iterator):
        if index == chosen_index:
            return item