

def subdict(dct, keys, on_error=None):
    """
    Return a subdictionary of dct that contains only the keys specified in keys
    @param dct: the original dictionary
    @type dct: dict
    @param keys: the sequence of keys to copy
    @param on_error: a function that is called if a key in keys is not in dct
        on_error(new_dict, dct, k)
    @return: the sub-dictionary
    @rtype: dict
    """

    d = type(dct)()
    for k in keys:
        try:
            d[k] = dct[k]
        except (KeyError, IndexError) as e:
            if on_error is not None:
                on_error(d, dct, k)
    return d

def splitdict(dct, keys):
    """
    Splits a dictionary in two dictionaries, one with the keys in @param keys
    one with the remaining keys.

    @param dct: the starting dictionary
    @type dct: dict
    @param keys: the keys to put in the first dictionary
    @type keys: iterable
    @return: A tuple of two dictionaries, the first containes the keys in
        @param keys
    @rtype: (dict, dict)
    """
    included = type(dct)()
    excluded = type(dct)()
    for k, v in dct.iteritems():
        if k in keys:
            included[k] = v
        else:
            excluded[k] = v
    return included, excluded
