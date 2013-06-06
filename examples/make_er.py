"""
This simple script creates G(n,m) ER random graphs of
arbitrary dimension and saves them to a file in HDF5 format
as sparse matrices.
"""
import h5py
import numpy as np
import numpy.random as rr
import argparse

bufsize = 10

def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output')
    parser.add_argument('-n', '--number-of-nodes', type=int)
    parser.add_argument('-m', '--number-of-edges', type=int)

    namespace = parser.parse_args()

    n = namespace.number_of_nodes
    m = namespace.number_of_edges

    ofile = h5py.File(namespace.output, 'w')
    indptr = ofile.create_dataset('indptr', (n+1, ), np.int64)
    indptr.write_direct(np.arange(0, m*n + 1, m, dtype=np.int64))
    indices = ofile.create_dataset('indices', (m * n, ), dtype=np.int32)
    # data = ofile.create_dataset('data', (m * n, ), dtype=np.int8)

    for index in xrange(n/bufsize):
        indices[index*m*bufsize:(index+1)*m*bufsize] =\
                rr.random_integers(0, n-1, m * bufsize)

    # data[:] = 1

    ofile.close()

if __name__ == '__main__':
    run()
