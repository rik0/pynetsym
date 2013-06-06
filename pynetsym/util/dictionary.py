def extract_sub_dictionary(dct, keys):
    """
    Extracts a sub-dictionary of dct with the keys specified in keys.
    """
    return {k: v for k, v in dct.iteritems() if k in keys}