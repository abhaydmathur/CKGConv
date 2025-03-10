import torch
from torch_geometric.graphgym import cfg
from torch_geometric.graphgym.register import register_edge_encoder


@register_edge_encoder("LinearEdge")
class LinearEdgeEncoder(torch.nn.Module):
    def __init__(self, emb_dim):
        super().__init__()
        if cfg.dataset.name in ["MNIST", "CIFAR10"]:
            self.in_dim = 1
        elif cfg.dataset.name.startswith("attributed_triangle-"):
            self.in_dim = 2
        else:
            self.in_dim = cfg.dataset.edge_encoder_num_types
            # raise ValueError("Input edge feature dim is required to be hardset "
            #                  "or refactored to use a cfg option.")

        self.encoder = torch.nn.Linear(self.in_dim, emb_dim)

    def forward(self, batch):
        batch.edge_attr = self.encoder(batch.edge_attr.view(-1, self.in_dim))
        return batch
