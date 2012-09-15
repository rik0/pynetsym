def extract_subdictionary(dct, opts):
    return {k: v for k, v in dct.iteritems() if k in opts}