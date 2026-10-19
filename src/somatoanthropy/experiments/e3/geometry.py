"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

import numpy as np


def region_ids(masks, faces):
    names = masks["joint_names"][masks["dominant_joint"]]
    regions = {k: np.unique(faces[masks[k]]) for k in ("torso", "pelvis")}
    regions.update(
        abdomen_spine01_proxy=np.flatnonzero(np.isin(names, ["c_spine0", "c_spine1"])),
        neck_head=np.flatnonzero(
            np.char.startswith(names, "c_neck") | np.isin(names, ["c_head", "c_jaw"])
        ),
        upper_limbs=np.flatnonzero(
            np.isin(
                names,
                [
                    s + "_" + j
                    for s in ("l", "r")
                    for j in ("uparm", "lowarm", "wrist", "wrist_twist")
                ],
            )
        ),
        lower_limbs=np.flatnonzero(
            np.isin(
                names,
                [
                    s + "_" + j
                    for s in ("l", "r")
                    for j in ("upleg", "lowleg", "foot", "ball", "talocrural", "subtalar")
                ],
            )
        ),
    )
    if any((not len(x) for x in regions.values())):
        raise ValueError("EMPTY_NATIVE_REGION")
    return regions
