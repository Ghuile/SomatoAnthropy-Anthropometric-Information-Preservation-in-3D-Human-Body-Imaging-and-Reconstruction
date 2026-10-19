"""Render the native MHR template and one-at-a-time control bounds, without fitting.

Only zero identity/expression and authored control values are created. External
model assets and generic topology attachments stay local. No participant parameter
or mesh input is accepted. Output is a mechanism illustration, not a study result.
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

from somatoanthropy.data.nomo_released_metrology import mapped_anchors, measure
from somatoanthropy.geometry.anthropometry.mhr_sites import validate_atlas
from somatoanthropy.reconstruction import check_hashes, load_native, native_forward

ROOT = Path(__file__).resolve().parents[1]


def template_controls(spec, only_neutral=False):
    """Nineteen template settings: neutral plus each of nine separate bounds."""
    neutral = dict(
        identity_coeffs=np.zeros((1, 45), np.float32),
        lbs_model_params=np.zeros((1, 204), np.float32),
        face_expr_coeffs=np.zeros((1, 72), np.float32),
    )
    result = [("neutral", neutral)]
    if only_neutral:
        return result
    for row in spec["parameter_audit"]:
        for bound in ["minimum", "maximum"]:
            value = {k: v.copy() for k, v in neutral.items()}
            value["lbs_model_params"][0, row["index"]] = row["bounds"][bound]
            result.append((row["name"] + "/" + bound, value))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--model-root",
        type=Path,
        required=True,
        help="Local root containing the pinned assets/mhr/v1 tree",
    )
    parser.add_argument(
        "--atlas",
        type=Path,
        required=True,
        help="Locally supplied LOD0 generic surface attachments",
    )
    parser.add_argument("--region-masks", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--only-neutral", action="store_true")
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Choose a new output directory")
    pins = json.loads((ROOT / "configs/model_hashes.json").read_text("utf-8"))
    # Verify all code and LOD0 assets actually used; no model download occurs.
    pins = {k: v for k, v in pins.items() if "/lod1/" not in k}
    check_hashes(args.model_root, pins)
    sys.path.insert(0, str(args.model_root / "assets/mhr/v1/code"))
    spec = json.loads((ROOT / "configs/control_release.json").read_text("utf-8"))
    model, faces = load_native(
        args.model_root / "assets/mhr/v1/lod0",
        0,
        spec["original_fitting"]["parameter_names"],
        20261019,
    )
    atlas = json.loads(args.atlas.read_text("utf-8"))
    with np.load(args.region_masks, allow_pickle=False) as masks:
        pelvis = masks["pelvis"].copy()
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection

    settings = template_controls(spec, args.only_neutral)
    fig, axes = plt.subplots(5, 4, figsize=(12, 15))
    records = []
    for ax, (label, controls) in zip(axes.flat, settings):
        raw, skeleton = native_forward(model, controls)
        vertices = raw.astype(float) * 0.01
        validate_atlas(atlas, vertices, faces)
        floor = float(vertices[:, 1].min())
        # Root position comes from this template forward, never a fitted person.
        names = list(model.character.skeleton.joint_names)
        root = skeleton.reshape(-1, 8)[names.index("root"), :3] * 0.01
        anchors = mapped_anchors(vertices, faces, atlas)
        sites, _ = measure(vertices, faces, root, anchors, pelvis)
        waist = sites["waist"]
        # B1's official frame conversion is float32 and floor-aligned.
        transformed = np.column_stack(
            (vertices[:, 0], -vertices[:, 2], vertices[:, 1] - floor)
        ).astype(np.float32)
        levels = dict(
            P=float(waist["plane_origin_m"][1]),
            B1=floor + 0.61 * float(transformed[:, 2].max()),
            offset=float(anchors["umbilicus_model_surface"][1] + 0.005),
        )
        tri = vertices[faces]
        order = np.argsort(tri[:, :, 2].mean(axis=1))
        normals = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        shade = 0.55 + 0.35 * np.abs(normals[:, 2]) / (np.linalg.norm(normals, axis=1) + 1e-15)
        rgba = np.column_stack((shade * 0.64, shade * 0.78, shade * 0.84, np.ones(len(shade))))
        ax.add_collection(
            PolyCollection(
                tri[order][:, :, [0, 1]], facecolors=rgba[order], linewidths=0, rasterized=True
            )
        )
        for name, color, style in [
            ("P", "#087f91", "-"),
            ("B1", "#b95729", "--"),
            ("offset", "#6164a9", ":"),
        ]:
            ax.axhline(levels[name], color=color, linestyle=style, linewidth=0.9)
        ax.set_xlim(-1.1, 1.1)
        ax.set_ylim(floor - 0.05, floor + 2.3)
        ax.set_aspect("equal")
        ax.axis("off")
        ax.set_title(label.replace("scale_", "").replace("/", "\n"), fontsize=8)
        records.append(
            dict(
                setting=label,
                planes_y_m=levels,
                P_fallback=bool(waist["fallback_applied"]),
                height_m=float(np.ptp(vertices[:, 1])),
                identity="zero template",
                expression="zero",
            )
        )
    for ax in list(axes.flat)[len(settings) :]:
        ax.axis("off")
    fig.suptitle(
        "MHR template: nine authored controls at bounds\nP solid teal; B1 dashed orange; offset dotted purple",
        fontsize=12,
    )
    fig.text(
        0.5,
        0.012,
        "Meta MHR template assets: Apache-2.0. No participant inputs or fitting. Planes are engineering proxies.",
        ha="center",
        fontsize=8,
    )
    args.output.mkdir(parents=True)
    fig.savefig(args.output / "template-controls.png", dpi=160, facecolor="white")
    plt.close(fig)
    metadata = dict(
        model_revision="4998cec385b1aaa07abdefba71bfba2f83c7db32",
        template_only=True,
        fitting_executed=False,
        articulation="Authored zero controls; not the study T90 transfer",
        measurement="Released-pose adaptive selector on template; B1 61%-height plane; umbilicus+0.005 m offset",
        local_attachment_hashes={
            k: hashlib.sha256(p.read_bytes()).hexdigest()
            for k, p in [("atlas", args.atlas), ("masks", args.region_masks)]
        },
        settings=records,
        asset_notice="third_party/MHR-assets-Apache-2.0.txt",
    )
    (args.output / "template-provenance.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    print(f"{len(records)} template forwards rendered; no participant fits.")


if __name__ == "__main__":
    main()
