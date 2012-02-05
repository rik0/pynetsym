

def subdict(dct, keys, on_error=None):
    """
    Return a subdictionary of dct that contains only the keys specified in keys
    :param dct: the original dictionary
    :param keys: the sequence of keys to copy
    :param on_error: a function that is called if a key in keys is not in dct
        on_error(new_dict, dct, k)
    :return: the sub-dictionary
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
    included = type(dct)()
    excluded = type(dct)()
    for k, v in dct.iteritems():
        if k in keys:
            included[k] = v
        else:
            excluded[k] = v
    return included, excluded
