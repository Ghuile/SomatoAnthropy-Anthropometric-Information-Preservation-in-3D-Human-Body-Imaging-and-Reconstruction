"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations

import hashlib
import io
import time

import numpy as np

from somatoanthropy.data.phase01_nomo import atomic_bytes, atomic_json
from somatoanthropy.geometry.mpii_mhr_fit01.fit import resources
from somatoanthropy.geometry.mpii_mhr_fit01.metrics import samples


def optimise(model, names, faces, source, source_faces, initial, translation0, config, arm, output):
    import torch
    from scipy.spatial import cKDTree

    output.mkdir(parents=True, exist_ok=True)
    cfg, protocol = (config["original_fitting"], config["continuation"])
    pose_ids = [names.index(n) for n in cfg["pose_names"]]
    rig_ids = config["released_indices"]
    pose_index, rig_index = (torch.tensor(pose_ids), torch.tensor(rig_ids))
    base = torch.tensor(initial["lbs_model_params"], dtype=torch.float32)
    identity = torch.nn.Parameter(torch.tensor(initial["identity_coeffs"], dtype=torch.float32))
    pose = torch.nn.Parameter(base[:, pose_ids].clone())
    rig = torch.nn.Parameter(base[:, rig_ids].clone(), requires_grad=arm == "released")
    expression = torch.tensor(initial["face_expr_coeffs"], dtype=torch.float32)
    translation = torch.nn.Parameter(torch.tensor(translation0, dtype=torch.float32))
    optimizer = torch.optim.Adam(
        [
            {"params": [identity], "lr": protocol["identity_lr"]},
            {"params": [pose], "lr": protocol["pose_lr"]},
            {"params": [translation], "lr": protocol["translation_lr"]},
            {"params": [rig], "lr": protocol["rig_lr"] if arm == "released" else 0},
        ]
    )
    bounds = torch.tensor(
        [
            cfg["root_rotation_bound_radians"]
            if n.startswith("root_")
            else cfg["pose_bound_radians"]
            for n in cfg["pose_names"]
        ]
    )
    rig_lo = torch.tensor([config["control_bounds"][str(i)]["minimum"] for i in rig_ids])
    rig_hi = torch.tensor([config["control_bounds"][str(i)]["maximum"] for i in rig_ids])

    def current():
        controls = base.index_copy(1, pose_index, pose).index_copy(1, rig_index, rig)
        native, joints = model(identity, controls, expression, apply_correctives=True)
        return (native[0] * 0.01 + translation, controls, joints)

    source_cloud, _, _ = samples(
        source, source_faces, protocol["samples"], protocol["source_sampling_seed"]
    )
    with torch.no_grad():
        initial_vertices = current()[0].numpy()
    _, face_ids, bary = samples(
        initial_vertices, faces, protocol["samples"], protocol["target_sampling_seed"]
    )
    matching = dict(
        source_cloud_sha256=hashlib.sha256(source_cloud.tobytes()).hexdigest(),
        target_face_ids_sha256=hashlib.sha256(face_ids.tobytes()).hexdigest(),
        target_barycentrics_sha256=hashlib.sha256(bary.tobytes()).hexdigest(),
        initial_vertices_sha256=hashlib.sha256(initial_vertices.tobytes()).hexdigest(),
        protocol=config["continuation"],
        pose_indices=pose_ids,
        released_indices=rig_ids,
    )
    sample_faces = torch.tensor(faces[face_ids])
    bary_tensor = torch.tensor(bary, dtype=torch.float32)
    source_tensor, source_tree = (
        torch.tensor(source_cloud, dtype=torch.float32),
        cKDTree(source_cloud),
    )
    parameters = dict(identity=identity, pose=pose, translation=translation, rig=rig)
    begin, history, best, gradient_max = (
        0,
        [],
        None,
        {k: np.zeros(tuple(p.shape)) for k, p in parameters.items()},
    )
    checkpoints = (
        sorted((output / "checkpoints").glob("*.pt")) if (output / "checkpoints").exists() else []
    )
    if checkpoints:
        state = torch.load(checkpoints[-1], weights_only=True)
        if state["matching"] != matching:
            raise ValueError("CHECKPOINT_MATCHING_PROTOCOL_CHANGED")
        begin, history, best = (state["next_iteration"], state["history"], state["best"])
        with torch.no_grad():
            for key, p in parameters.items():
                p.copy_(state["parameters"][key])
        optimizer.load_state_dict(state["optimizer"])
        gradient_max = {k: np.asarray(v) for k, v in state["gradient_max"].items()}
    start = time.monotonic()
    for iteration in range(begin, protocol["iterations"]):
        if time.monotonic() - start > protocol["timeout_seconds"]:
            raise TimeoutError("BOUNDED_CONTINUATION_TIMEOUT")
        if iteration % 10 == 0:
            resources(output, cfg)
        optimizer.zero_grad(set_to_none=True)
        vertices, controls, joints = current()
        sampled = (vertices[sample_faces] * bary_tensor[..., None]).sum(1)
        detached = sampled.detach().numpy()
        fidx = cKDTree(detached).query(source_cloud)[1]
        bidx = source_tree.query(detached)[1]
        a = ((source_tensor - sampled[torch.tensor(fidx)]) ** 2).sum(1)
        b = ((sampled - source_tensor[torch.tensor(bidx)]) ** 2).sum(1)
        delta2 = cfg["robust_delta_metres"] ** 2

        def robust(d):
            return delta2 * (torch.sqrt(1 + d / delta2) - 1)

        data_loss = 0.5 * (robust(a).mean() + robust(b).mean())
        identity_prior = cfg["identity_l2_weight"] * identity.square().mean()
        pose_prior = cfg["pose_l2_weight"] * pose.square().mean()
        rig_prior = protocol["rig_l2_weight"] * rig.square().mean()
        loss = data_loss + identity_prior + pose_prior + rig_prior
        if not torch.isfinite(loss):
            raise FloatingPointError("NONFINITE_OBJECTIVE")
        loss.backward()
        for key, p in parameters.items():
            if p.requires_grad:
                if p.grad is None or not torch.isfinite(p.grad).all():
                    raise FloatingPointError("INVALID_GRADIENT:" + key)
                gradient_max[key] = np.maximum(gradient_max[key], np.abs(p.grad.numpy()))
        if best is None or float(loss.detach()) < best["objective"]:
            best = dict(
                objective=float(loss.detach()),
                iteration=iteration,
                parameters={k: p.detach().clone() for k, p in parameters.items()},
            )
        norm = torch.nn.utils.clip_grad_norm_(
            [p for p in parameters.values() if p.requires_grad], cfg["gradient_clip_norm"]
        )
        history.append(
            dict(
                iteration=iteration,
                data_loss=float(data_loss.detach()),
                identity_prior=float(identity_prior.detach()),
                pose_prior=float(pose_prior.detach()),
                rig_prior=float(rig_prior.detach()),
                objective=float(loss.detach()),
                gradient_norm_before_clip=float(norm),
                rig_gradient_norm=float(rig.grad.norm()) if rig.grad is not None else 0,
            )
        )
        optimizer.step()
        with torch.no_grad():
            identity.clamp_(-cfg["identity_bound"], cfg["identity_bound"])
            pose.copy_(torch.maximum(torch.minimum(pose, bounds), -bounds))
            rig.copy_(torch.maximum(torch.minimum(rig, rig_hi), rig_lo))
        if (iteration + 1) % protocol["checkpoint_every"] == 0:
            state = dict(
                matching=matching,
                next_iteration=iteration + 1,
                parameters={k: p.detach().clone() for k, p in parameters.items()},
                optimizer=optimizer.state_dict(),
                history=history,
                best=best,
                gradient_max={k: v.tolist() for k, v in gradient_max.items()},
            )
            stream = io.BytesIO()
            torch.save(state, stream)
            atomic_bytes(output / "checkpoints" / f"{iteration + 1:04d}.pt", stream.getvalue())
            atomic_json(
                output / "trace" / f"{iteration + 1:04d}.json",
                history[-protocol["checkpoint_every"] :],
            )
            print(
                f"{output.parent.name}/{arm} {iteration + 1}/{protocol['iterations']} objective={float(loss.detach()):.7g}",
                flush=True,
            )
    with torch.no_grad():
        for key, p in parameters.items():
            p.copy_(best["parameters"][key])
        vertices, controls, joints = current()
    out = dict(
        identity_coeffs=identity.detach().numpy(),
        lbs_model_params=controls.detach().numpy(),
        face_expr_coeffs=expression.numpy(),
    )
    frozen = [i for i in range(204) if i not in pose_ids + (rig_ids if arm == "released" else [])]
    if not np.array_equal(
        out["lbs_model_params"][:, frozen], initial["lbs_model_params"][:, frozen]
    ):
        raise ValueError("FROZEN_CONTROL_MOVED")
    return (
        out,
        dict(
            matching=matching,
            history=history,
            best_iteration=best["iteration"],
            best_objective=best["objective"],
            translation=translation.detach().numpy().tolist(),
            gradient_max={k: v.tolist() for k, v in gradient_max.items()},
            elapsed_seconds=time.monotonic() - start,
            initial_controls_preserved=True,
            frozen_indices=frozen,
            resumed_from_iteration=begin,
            bound_hits=[
                names[i]
                for j, i in enumerate(rig_ids)
                if min(
                    abs(float(rig[0, j]) - float(rig_lo[j])),
                    abs(float(rig[0, j]) - float(rig_hi[j])),
                )
                < 1e-06
            ],
        ),
    )
