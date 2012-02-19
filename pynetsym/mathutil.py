from numpy import cumsum, sum

def cdf(dist):
    return 1 - (cumsum(dist, dtype=float)/sum(dist))

