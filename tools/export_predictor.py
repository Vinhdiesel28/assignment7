from pathlib import Path
import shutil
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT.parent / "results" / "diabetes" / "models"
state = torch.load(SOURCE / "baseline_lr001.pth", map_location="cpu", weights_only=True)
np.savez_compressed(
    ROOT / "web" / "bundle" / "diabetes_mlp.npz",
    w1=state["network.0.weight"].numpy(),
    b1=state["network.0.bias"].numpy(),
    w2=state["network.2.weight"].numpy(),
    b2=state["network.2.bias"].numpy(),
)
shutil.copy2(SOURCE / "preprocessor.joblib", ROOT / "web" / "bundle" / "preprocessor.joblib")
print("Đã xuất MLP PyTorch sang NumPy và sao chép preprocessor.")
