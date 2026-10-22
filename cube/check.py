import torch
from pathlib import Path

checkpoint = torch.load(Path("checkpoints/best.pt"), map_location="cpu")
optimizer_state = checkpoint["optimizer_state_dict"]

for i, group in enumerate(optimizer_state["param_groups"]):
    print(f"Group {i} LR: {group['lr']}, weight_decay: {group['weight_decay']}")