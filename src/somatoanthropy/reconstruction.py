"""Runtime adapter to the pinned native model and original optimisers."""

from __future__ import annotations

import hashlib
import importlib
from pathlib import Path
from typing import Any

import numpy as np

MHR_REVISION = "4998cec385b1aaa07abdefba71bfba2f83c7db32"
CLAD_REVISION = "a2140a74555a6382e1712ec1a5d8dc939b59e655"


def check_hashes(root: Path, pins: dict[str, str]) -> None:
    for name, digest in pins.items():
        path = (root / name.replace("\\", "/")).resolve()
        if not path.is_relative_to(root.resolve()):
            raise ValueError("ASSET_ESCAPES_ROOT")
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError("MISSING_OR_CHANGED_ASSET:" + name)


def load_native(asset_root: Path, lod: int, names: list[str], seed: int) -> Any:
    """Use the upstream model. Caller must verify the code and asset hashes first."""
    import torch
    from mhr.mhr import MHR

    torch.set_num_threads(1)
    torch.manual_seed(seed)
    model = (
        MHR.from_files(
            asset_root,
            device=torch.device("cpu"),
            lod=lod,
            wants_pose_correctives=True,
        )
        .eval()
        .requires_grad_(False)
    )
    if list(model.character.parameter_transform.names)[:-117] != names:
        raise ValueError("PINNED_NATIVE_CONTROL_MAPPING_CHANGED")
    if model.pose_correctives_model is None:
        raise ValueError("POSE_CORRECTIVES_REQUIRED")
    expected = {0: 147274, 1: 36874}[lod]
    faces = np.asarray(model.character.mesh.faces, dtype=np.int64)
    if faces.shape != (expected, 3):
        raise ValueError("PINNED_NATIVE_TOPOLOGY_CHANGED")
    return model, faces


def native_forward(model: Any, controls: dict[str, Any]) -> tuple[Any, Any]:
    import torch

    with torch.inference_mode():
        vertices, skeleton = model(
            *(
                torch.tensor(controls[k], dtype=torch.float32)
                for k in ("identity_coeffs", "lbs_model_params", "face_expr_coeffs")
            ),
            apply_correctives=True,
        )
    return vertices[0].numpy(), skeleton[0].numpy()


def clad_api(pins: dict[str, str]) -> tuple[Any, ...]:
    """Verify the installed upstream bytes before exposing the tested B1 API."""
    package = importlib.import_module("clad_body")
    root = Path(package.__file__).resolve().parent.parent
    for name, digest in pins.items():
        if not name.replace("\\", "/").startswith("clad_body/"):
            continue
        path = root / name.replace("\\", "/")
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError("CLAD_BODY_PIN_MISMATCH:" + name)
    from clad_body.load.mhr import MhrBody, _mhr_yup_cm_to_canonical
    from clad_body.measure import measure
    from clad_body.measure._slicer import torso_circumference_at_z

    return MhrBody, _mhr_yup_cm_to_canonical, measure, torso_circumference_at_z
