# from typing import Optional, Callable, List
#
# import os
# import glob
# import os.path as osp
#
# import torch
# from torch_geometric.data import (InMemoryDataset, Data, download_url,
#                                   extract_tar, extract_zip)
# from torch_geometric.utils import remove_isolated_nodes
#
# from torch_geometric.data import InMemoryDataset
# from torch_geometric.data.data import Data
# import scipy.io as sio
# import numpy as np
# import matplotlib.pyplot as plt
# from torch_geometric.utils import to_scipy_sparse_matrix,get_laplacian,remove_self_loops
# from numpy.linalg import eig,eigh
# import math
#
#
# """
# This is a modified class of LearningFitlers data from BernNet
# https://github.com/ivam-he/BernNet/tree/main/LearningFilters
# """
#
#
# class TwoDGrid(InMemoryDataset):
#     def __init__(self, root, transform=None, pre_transform=None):
#         super(TwoDGrid, self).__init__(root, transform, pre_transform)
#         self.data, self.slices = torch.load(self.processed_paths[0])
#
#     @property
#     def raw_file_names(self):
#         return ["2Dgrid.mat"]
#
#     @property
#     def processed_file_names(self):
#         return 'data.pt'
#
#     def download(self):
#         pass
#
#     def process(self):
#         # Read data into huge `Data` list.
#         b = self.processed_paths[0]
#         a = sio.loadmat(self.raw_paths[0])  # 'subgraphcount/randomgraph.mat')
#
#         # list of adjacency matrix
#         A = a['A']
#         # list of output
#         F = a['F']
#         F = F.astype(np.float32)
#         # Y=a['Y']
#         # Y=Y.astype(np.float32)
#         M = a['mask']
#         M = M.astype(np.float32)
#
#         data_list = []
#         E = np.where(A > 0)
#         edge_index = torch.Tensor(np.vstack((E[0], E[1]))).type(torch.int64)
#         x = torch.tensor(F)
#         # y=torch.tensor(Y)
#         m = torch.tensor(M)
#
#         x_tmp = x[:, 0:1]
#         data_list.append(Data(edge_index=edge_index, x=x, x_tmp=x_tmp, m=m))
#
#         if self.pre_filter is not None:
#             data_list = [data for data in data_list if self.pre_filter(data)]
#
#         if self.pre_transform is not None:
#             data_list = [self.pre_transform(data) for data in data_list]
#
#         data, slices = self.collate(data_list)
#         torch.save((data, slices), self.processed_paths[0])
#
#
# def visualize(y):
#     # y=tensor.detach().cpu().numpy()
#     y = np.reshape(y, (100, 100))
#     plt.imshow(y.T);
#     plt.colorbar();
#     plt.show()
#
#
# def myeign(L, root='data/2Dgrid'):
#     if os.path.exists(osp.join(root,'eigenvalues.npy')) and os.path.exists(osp.join(root, 'eigenvectors.npy')):
#
#         eigenvalues = np.load(osp.join(root,'eigenvalues.npy'))
#         eigenvectors = np.load(osp.join(root, 'eigenvectors.npy'))
#     else:
#         eigenvalues, eigenvectors = eigh(L)
#         np.save(osp.join(root, 'eigenvalues.npy'), eigenvalues)
#         np.save(osp.join(root, 'eigenvectors.npy'), eigenvectors)
#
#     return eigenvalues, eigenvectors
#
#
# def filtering(filter_type, root='data/2Dgrid'):
#     # dataset = TwoDGrid(root='data/2Dgrid', pre_transform=None)
#     dataset = TwoDGrid(root=root, pre_transform=None)
#     data = dataset[0]
#     x = data.x.numpy()
#
#     # print(data.edge_index)
#     adj = to_scipy_sparse_matrix(data.edge_index).todense()
#     nnodes = adj.shape[0]
#     D_vec = np.sum(adj, axis=1).A1
#     # print(D_vec.tolist())
#     D_vec_invsqrt_corr = 1 / np.sqrt(D_vec)
#     D_invsqrt_corr = np.diag(D_vec_invsqrt_corr)
#     # print(D_invsqrt_corr)
#     L = np.eye(nnodes) - D_invsqrt_corr @ adj @ D_invsqrt_corr
#     # print(L)
#     eigenvalues, eigenvectors = myeign(L, root=root)
#     # print(eigenvalues[3])
#
#     # low-pass
#     if filter_type == 'low':
#         value_tmp = [math.exp(-10 * (xxx - 0) ** 2) for xxx in eigenvalues]
#
#     # high-pass
#     elif filter_type == 'high':
#         value_tmp = [1 - math.exp(-10 * (xxx - 0) ** 2) for xxx in eigenvalues]
#
#     # band-pass
#     elif filter_type == 'band':
#         value_tmp = [math.exp(-10 * (xxx - 1) ** 2) for xxx in eigenvalues]
#
#     # band_rejection
#     elif filter_type == 'rejection':
#         value_tmp = [1 - math.exp(-10 * (xxx - 1) ** 2) for xxx in eigenvalues]
#
#     # comb
#     elif filter_type == 'comb':
#         value_tmp = [abs(np.sin(xxx * math.pi)) for xxx in eigenvalues]
#
#     # low_band
#     elif filter_type == 'low_band':
#         y = []
#         for i in eigenvalues:
#             if i < 0.5:
#                 y.append(1)
#             elif i < 1 and i >= 0.5:
#                 y.append(math.exp(-100 * (i - 0.5) ** 2))
#             else:
#                 y.append(math.exp(-50 * (i - 1.5) ** 2))
#         value_tmp = y
#
#     value_tmp = np.array(value_tmp)
#     value_tmp = np.diag(value_tmp)
#     # print(value_tmp[5000][5000])
#
#     y = eigenvectors @ value_tmp @ eigenvectors.T @ x
#     np.save(osp.join(root, 'y_' + filter_type + '.npy'), y)
#
#     return y
