"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

import shutil
import time
from pathlib import Path
from typing import Any

import numpy as np

from somatoanthropy.geometry.mpii_mhr_fit01.metrics import samples
from somatoanthropy.geometry.mpii_mhr_fit01.storage import write_json, write_npz


def resources(root: Path, config: dict[str, Any]) -> None:
    memory = dict((line.split(":", 1) for line in Path("/proc/meminfo").read_text().splitlines()))
    available = int(memory["MemAvailable"].strip().split()[0]) * 1024
    if available < config["minimum_available_ram_bytes"]:
        raise RuntimeError("Resource safety: insufficient available WSL RAM")
    if shutil.disk_usage(root).free < config["minimum_disk_free_bytes"]:
        raise RuntimeError("Resource safety: insufficient output disk")


def optimise(
    model: Any,
    names: list[str],
    faces: Any,
    source: Any,
    source_faces: Any,
    config: dict[str, Any],
    output: Path,
) -> dict[str, Any]:
    import torch
    from scipy.spatial import cKDTree

    started = time.monotonic()
    identity = torch.nn.Parameter(torch.zeros((1, config["dimensions"][0])))
    pose = torch.nn.Parameter(torch.zeros((1, len(config["pose_names"]))))
    expression = torch.zeros((1, config["dimensions"][2]))
    indices = torch.tensor([names.index(n) for n in config["pose_names"]])
    with torch.no_grad():
        neutral, skeleton = model(
            identity,
            torch.zeros((1, len(names))),
            expression,
            apply_correctives=config["apply_correctives"],
        )
    neutral = neutral.numpy()[0]
    center = (np.min(source, axis=0) + np.max(source, axis=0)) * 0.5
    translation = torch.nn.Parameter(
        torch.tensor(center - (neutral.min(0) + neutral.max(0)) * 0.005, dtype=torch.float32)
    )
    initial = neutral.astype(np.float64) * 0.01 + translation.detach().numpy()
    write_npz(
        output / "initial-geometry.npz", vertices=neutral, faces=faces, comparison_vertices=initial
    )
    history: list[dict[str, Any]] = []
    gradient: dict[str, float] = {}
    gradient_controls: dict[str, Any] = {}
    best: tuple[float, Any, Any, Any] | None = None
    bounds = torch.tensor(
        [
            config["root_rotation_bound_radians"]
            if n.startswith("root_")
            else config["pose_bound_radians"]
            for n in config["pose_names"]
        ]
    )

    def forward() -> tuple[Any, Any, Any]:
        controls = torch.zeros((1, len(names))).index_copy(1, indices, pose)
        native, joints = model(
            identity, controls, expression, apply_correctives=config["apply_correctives"]
        )
        return (native, native[0] * 0.01 + translation, joints)

    for stage_number, stage in enumerate(config["stages"]):
        count = stage["samples"]
        source_cloud, _, _ = samples(
            source, source_faces, count, config["seed"] + stage_number * 10
        )
        source_tensor = torch.tensor(source_cloud, dtype=torch.float32)
        source_tree = cKDTree(source_cloud)
        with torch.no_grad():
            current = forward()[1].numpy()
        _, face_ids, bary = samples(current, faces, count, config["seed"] + stage_number * 10 + 1)
        sample_faces = torch.tensor(faces[face_ids], dtype=torch.long)
        bary_tensor = torch.tensor(bary, dtype=torch.float32)
        optimizer = torch.optim.Adam(
            [
                {"params": [identity], "lr": stage["identity_lr"]},
                {"params": [pose], "lr": stage["pose_lr"]},
                {"params": [translation], "lr": stage["translation_lr"]},
            ]
        )
        start_identity, start_pose = (identity.detach().clone(), pose.detach().clone())
        for iteration in range(stage["iterations"]):
            if time.monotonic() - started > config["per_body_timeout_seconds"]:
                raise TimeoutError("Frozen per-body fitting budget exceeded")
            if iteration % 20 == 0:
                resources(output, config)
            optimizer.zero_grad(set_to_none=True)
            native, current, joints = forward()
            sampled = (current[sample_faces] * bary_tensor[..., None]).sum(1)
            detached = sampled.detach().numpy()
            target_tree = cKDTree(detached)
            fidx, bidx = ([], [])
            chunk = config["nearest_neighbour_chunk"]
            for begin in range(0, count, chunk):
                fidx.extend(target_tree.query(source_cloud[begin : begin + chunk])[1].tolist())
                bidx.extend(source_tree.query(detached[begin : begin + chunk])[1].tolist())
            dforward = ((source_tensor - sampled[torch.tensor(fidx)]) ** 2).sum(1)
            dbackward = ((sampled - source_tensor[torch.tensor(bidx)]) ** 2).sum(1)
            delta2 = config["robust_delta_metres"] ** 2

            def robust(d: Any) -> Any:
                return delta2 * (torch.sqrt(1 + d / delta2) - 1)

            data_loss = (robust(dforward).mean() + robust(dbackward).mean()) * 0.5
            prior = (
                config["identity_l2_weight"] * identity.square().mean()
                + config["pose_l2_weight"] * pose.square().mean()
            )
            loss = data_loss + prior
            if not torch.isfinite(loss):
                raise FloatingPointError("Nonfinite native fitting objective")
            loss.backward()
            for family, parameter in (
                ("identity", identity),
                ("pose", pose),
                ("translation", translation),
            ):
                if parameter.grad is None or not torch.isfinite(parameter.grad).all():
                    raise FloatingPointError(f"Invalid {family} gradient")
                gradient[family] = max(gradient.get(family, 0.0), float(parameter.grad.norm()))
                if config.get("trace_every_iteration", False):
                    previous = gradient_controls.get(family, np.zeros_like(parameter.grad.numpy()))
                    gradient_controls[family] = np.maximum(previous, np.abs(parameter.grad.numpy()))
            if (
                config.get("retain_best_final_stage", False)
                and stage_number == len(config["stages"]) - 1
                and (best is None or float(loss.detach()) < best[0])
            ):
                best = (
                    float(loss.detach()),
                    identity.detach().clone(),
                    pose.detach().clone(),
                    translation.detach().clone(),
                )
            torch.nn.utils.clip_grad_norm_(
                [identity, pose, translation], config["gradient_clip_norm"]
            )
            optimizer.step()
            with torch.no_grad():
                identity.clamp_(-config["identity_bound"], config["identity_bound"])
                pose.copy_(torch.maximum(torch.minimum(pose, bounds), -bounds))
            if (
                config.get("trace_every_iteration", False)
                or iteration % 10 == 0
                or iteration + 1 == stage["iterations"]
            ):
                row = {
                    "stage": stage["name"],
                    "iteration": iteration,
                    "robust_data_loss_m2": float(data_loss.detach()),
                    "regularisation": float(prior.detach()),
                    "elapsed_seconds": time.monotonic() - started,
                }
                history.append(row)
                if config.get("trace_every_iteration", False) and (
                    iteration % 20 == 0 or iteration + 1 == stage["iterations"]
                ):
                    write_json(output / "live-history.json", history, replace=True)
                    write_npz(
                        output / "checkpoints" / f"{stage_number}-{iteration:04d}.npz",
                        identity=identity.detach().numpy(),
                        pose=pose.detach().numpy(),
                        translation=translation.detach().numpy(),
                    )
                if iteration % 40 == 0:
                    print(
                        f"{output.name} {stage['name']} {iteration}/{stage['iterations']} loss={row['robust_data_loss_m2']:.6g} elapsed={row['elapsed_seconds']:.1f}s",
                        flush=True,
                    )
        history.append(
            {
                "stage": stage["name"],
                "identity_update_norm": float((identity.detach() - start_identity).norm()),
                "pose_update_norm": float((pose.detach() - start_pose).norm()),
            }
        )
    if (
        any((gradient.get(k, 0.0) <= 0 for k in ("identity", "pose", "translation")))
        or identity.detach().norm() == 0
    ):
        raise FloatingPointError("No effective trainable native parameter updates")
    with torch.no_grad():
        if best is not None:
            identity.copy_(best[1])
            pose.copy_(best[2])
            translation.copy_(best[3])
        native, comparison, joints = forward()
        controls = torch.zeros((1, len(names))).index_copy(1, indices, pose)
    write_npz(
        output / "mhr-parameters.npz",
        identity=identity.detach().numpy(),
        model=controls.detach().numpy(),
        expression=expression.numpy(),
    )
    write_npz(
        output / "mhr-native-geometry.npz",
        vertices=native.numpy()[0],
        faces=faces,
        skeleton=joints.numpy(),
    )
    return {
        "history": history,
        "gradient_max_norms": gradient,
        "per_control_max_absolute_gradients": {k: v.tolist() for k, v in gradient_controls.items()},
        "best_final_stage_objective": best[0] if best is not None else None,
        "elapsed_seconds": time.monotonic() - started,
        "translation_metres": translation.detach().numpy().tolist(),
        "identity_norm": float(identity.detach().norm()),
        "pose_norm": float(pose.detach().norm()),
        "native_parameter_only": True,
        "no_postfit_vertex_displacements": True,
    }
