# ------- Shortest-path Distance: Naive implementation --------
from typing import Union, Any, Optional
import numpy as np
import torch
import torch.nn.functional as F
import torch_geometric as pyg
from torch_geometric.data import Data, HeteroData
from torch_geometric.transforms import BaseTransform
from torch_scatter import scatter, scatter_add, scatter_max

from torch_geometric.graphgym.config import cfg

from torch_geometric.utils import (
    get_laplacian,
    get_self_loop_attr,
    to_scipy_sparse_matrix,
)
import torch_sparse
from torch_sparse import SparseTensor
from einops import rearrange, reduce, repeat, einsum


def add_node_attr(data: Data, value: Any, attr_name: Optional[str] = None) -> Data:
    if attr_name is None:
        if "x" in data:
            x = data.x.view(-1, 1) if data.x.dim() == 1 else data.x
            data.x = torch.cat([x, value.to(x.device, x.dtype)], dim=-1)
        else:
            data.x = value
    else:
        data[attr_name] = value

    return data


#


@torch.no_grad()
def add_spd(
    data,
    walk_length=8,
    attr_name_abs="spd",  # name: 'rrwp'
    attr_name_rel="spd",  # name: ('rrwp_idx', 'rrwp_val')
    add_identity=True,
    add_uniform=False,
    denormalize=False,
    spd=False,
    topk: Optional[int] = None,
    use_sym=False,
    **kwargs,
):

    device = data.edge_index.device
    ind_vec = torch.eye(walk_length, dtype=torch.float, device=device)
    num_nodes = data.num_nodes
    edge_index, edge_weight = data.edge_index, data.edge_weight

    adj = SparseTensor.from_edge_index(
        edge_index,
        edge_weight,
        sparse_sizes=(num_nodes, num_nodes),
    )

    # Compute D^{-1} A:
    deg = adj.sum(dim=1)
    deg_inv = 1.0 / adj.sum(dim=1)
    deg_inv[deg_inv == float("inf")] = 0
    adj = adj * deg_inv.view(-1, 1)
    adj = adj.to_dense()

    pe_list = []
    i = 0
    pe_list.append(torch.eye(num_nodes, dtype=torch.float))
    cache = torch.eye(num_nodes, dtype=torch.float)

    out = adj
    pe_list.append(adj)
    i = i + 1

    cache += adj

    for j in range(i + 1, walk_length + 1):
        out = out @ adj
        pe_list.append(out)
        cache += out
        if cache.all():
            break

    pe = torch.stack(pe_list, dim=-1)  # n x n x k
    # abs_pe = pe.diagonal().transpose(0, 1)[:, 1:] # n x k

    adder = torch.zeros(1, pe.size(-1))
    adder[:, -1] = 1
    pe = (pe > 0).type(torch.float)
    pe[pe.sum(dim=-1) == 0] += adder

    rel_pe = SparseTensor.from_dense(pe, has_value=True)
    rel_pe_row, rel_pe_col, rel_pe_val = rel_pe.coo()
    rel_pe_val = torch.argmax(rel_pe_val, dim=-1)

    # rel_pe_idx = torch.stack([rel_pe_row, rel_pe_col], dim=-2)
    # Fixme: fatal bug --> pyg is right matmul, need row-sum to one, now is col-sum to one.
    rel_pe_idx = torch.stack([rel_pe_col, rel_pe_row], dim=0)

    data = add_node_attr(data, rel_pe_idx, attr_name=f"{attr_name_rel}_index")
    data = add_node_attr(data, rel_pe_val, attr_name=f"{attr_name_rel}_val")
    data.log_deg = torch.log(deg + 1)
    data.deg = deg.type(torch.long)

    return data
