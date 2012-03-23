

def extract_options(dct, opts):
    return {k: v for k, v in dct.iteritems() if k in opts}
