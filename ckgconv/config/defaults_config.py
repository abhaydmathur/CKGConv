from torch_geometric.graphgym.register import register_config


@register_config("overwrite_defaults")
def overwrite_defaults_cfg(cfg):
    """Overwrite the default config values that are first set by GraphGym in
    torch_geometric.graphgym.config.set_cfg

    WARNING: At the time of writing, the order in which custom config-setting
    functions like this one are executed is random; see the referenced `set_cfg`
    Therefore never reset here config options that are custom added, only change
    those that exist in core GraphGym.
    """

    # Overwrite default dataset name
    cfg.dataset.name = "none"

    # Overwrite default rounding precision
    cfg.round = 5


@register_config("extended_cfg")
def extended_cfg(cfg):
    """General extended config options."""

    # Additional name tag used in `run_dir` and `wandb_name` auto generation.
    cfg.name_tag = ""

    # In training, if True (and also cfg.train.enable_ckpt is True) then
    # always checkpoint the current best model based on validation performance,
    # instead, when False, follow cfg.train.eval_period checkpointing frequency.

    cfg.best_by_loss = False  # choose the best epoch by loss rether than by metrics
    # --------------------
    cfg.train.ckpt_best = True
    cfg.tensorboard_each_run = True

    cfg.vp_momentum = 1.0  # adding momentum update to val_perf ---> to smooth the model selection based on val_perf
