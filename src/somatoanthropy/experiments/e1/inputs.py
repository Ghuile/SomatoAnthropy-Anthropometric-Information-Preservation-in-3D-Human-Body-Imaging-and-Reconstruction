"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

import hashlib
import io
import sys
import zipfile
from pathlib import Path

import numpy as np
import trimesh

from somatoanthropy.data.mpii_humanshape.loader import points_array, template_arrays
from somatoanthropy.data.nomo.meshes import read_mesh
from somatoanthropy.geometry.mpii_mhr_fit01.core import source_to_working
from somatoanthropy.geometry.nomo_caesar_mhr_fit04.core import transform


def pair_meshes(c, r):
    ds = r["dataset"]
    if ds == "NHANES" or not r["surface_eligible"]:
        raise ValueError("INELIGIBLE_SURFACE_PAIR")
    b = c.arrays(r["fitted_mesh"])
    bv, bf = (np.asarray(b["vertices"], float), b["faces"])
    meta = dict(
        lod=r["lod"],
        unit=r["unit"],
        source_transform="saved historical transform only",
        pose="own source and saved fitted articulation",
        no_posthoc_alignment=True,
    )
    if ds == "NOMO":
        a = read_mesh(c.pin(r["source_path"], r["source_sha256"]).read_bytes())
        av, af = (transform(a.vertices, r["source_to_working"]), a.faces)
        meta["source_transform_matrix"] = r["source_to_working"]
    elif ds == "UCSC":
        a = read_mesh(c.pin(r["source_path"], r["source_sha256"]).read_bytes())
        prov = c.read(r["model_provenance"])
        matrix = prov["source_alignment"]["source_to_working_matrix"]
        av, af = (transform(a.vertices, matrix), a.faces)
        meta["source_transform_matrix"] = matrix
    elif ds == "MPII":
        a = points_array(c.pin(r["source_path"], r["source_sha256"]).read_bytes())
        prov = c.read(r["model_provenance"])
        links = c.read(Path(r["mesh"]).parent / "source_links.json")
        variant = links["variant"]
        template = {
            "caesar_wsx": "caesar_wsx_shape_space/caesar-norm-wsx",
            "caesar_nh": "caesar_nh_shape_space/caesar-norm-nh",
            "caesar": "caesar_shape_space/caesar",
        }[variant]
        _, af, _, _ = template_arrays(
            c.pin(
                c.root / "data/raw/mpii_humanshape/v1.0/extracted" / template / "model.dat"
            ).read_bytes()
        )
        bv += np.asarray(prov["source_alignment"]["translation_metres"])
        av = source_to_working(a)
        meta.update(
            source_variant=variant,
            source_axis_matrix=prov["source_to_working_rotation"],
            source_scale=prov["source_to_working_scale"],
            saved_fitted_translation=prov["source_alignment"]["translation_metres"],
        )
    elif ds == "HBW":
        a = c.arrays(c.pin(r["source_path"], r["source_sha256"]))
        av, af = (a["vertices"], a["faces"])
        bv *= 0.01
        meta["native_cm_conversion"] = 0.01
    elif ds == "HIT":
        a = c.arrays(c.pin(r["source_path"], r["source_sha256"]))
        original = Path(r["fitted_parameters"]).parent / "transforms.json"
        tr = c.read(original)
        av = a["vertices"] @ np.asarray(tr["source_to_fitting_rotation"]).T
        af = a["faces"]
        bv = bv * 0.01 + np.asarray(tr["native_to_fitting_translation_m"])
        meta["saved_transform"] = tr
    elif ds == "FAUST":
        p = c.pin(r["source_path"])
        with zipfile.ZipFile(p) as z:
            raw = z.read(r["source_member"])
        if hashlib.sha256(raw).hexdigest() != r["source_sha256"]:
            raise ValueError("SOURCE_MEMBER_HASH_MISMATCH")
        a = trimesh.load(io.BytesIO(raw), file_type="ply", process=False)
        av, af = (np.asarray(a.vertices), np.asarray(a.faces))
        meta["saved_transform"] = c.read(Path(r["fitted_mesh"]).parent / "transforms.json")
    elif ds == "DFAUST":
        import h5py

        ref = r["source_member"]
        p = c.pin(r["source_path"], ref["container_sha256"])
        with h5py.File(p, "r") as h:
            av = np.asarray(h[ref["key"]][:, :, ref["frame"]])
            af = np.asarray(h["faces"])
            if af.shape[1] != 3:
                af = af.T
        meta["saved_transform"] = c.read(Path(r["fitted_mesh"]).parent / "transforms.json")
    else:
        raise ValueError(ds)
    return ((np.asarray(av, float), np.asarray(af, int)), (bv, np.asarray(bf, int)), meta)


def canonical_mesh(c, r):
    d = c.arrays(r["canonical_mesh"])
    v = np.asarray(d["vertices"], float)
    if r["dataset"] == "HIT":
        v *= 0.01
        v[:, 1] -= v[:, 1].min()
    return (v, d["faces"])
