from scipy import sparse
import networkx as nx
import h5py
npzfile = h5py.File('foo.hd5', 'r')
n = npzfile['indptr'].len() - 1
shape = n, n
M = sparse.csr_matrix(
        (npzfile['data'], npzfile['indices'], npzfile['indptr']),
        shape=shape)
G = nx.from_scipy_sparse_matrix(M)
nx.draw(G)
