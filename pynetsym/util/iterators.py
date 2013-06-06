
def inits(iterable):
    """
    The inits function returns all initial segments of the argument, shortest first.

    For example,

    >>> list(inits(""))
    [[]]
    >>> list(inits("abc"))
    [[], ['a'], ['a', 'b'], ['a', 'b', 'c']]
    """

    parts = []

    for item in iter(iterable):
        yield list(parts)
        parts.append(item)
    yield list(parts)


if __name__ == '__main__':
    import doctest
    doctest.testmod()