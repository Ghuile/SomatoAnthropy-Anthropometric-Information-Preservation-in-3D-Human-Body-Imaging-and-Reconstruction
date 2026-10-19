"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations
import numpy as np

def skeleton_points(mesh):
    move = mesh.get('working_translation', np.array([0.0, float(mesh['floor_translation_m']), 0.0]))
    return dict(zip(mesh['joint_names'].tolist(), mesh['skeleton'][:, :3] * 0.01 + move, strict=True))
