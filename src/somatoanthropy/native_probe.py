"""Native control mapping query retained from the original E2-1 probe.

Reads the loaded model only. It does not forward geometry, fit, optimize, or
record machine resource information. Provenance is in claim-pipeline-provenance.
"""

from somatoanthropy.reconstruction import MHR_REVISION


def probe_controls(model, names):
    character = model.character
    transform = character.parameter_transform.transform.numpy()
    joints = [j.name for j in character.skeleton.joints]
    mapping = transform.reshape(-1, 7, transform.shape[1])
    rows = []
    for i, name in enumerate(names):
        affected = []
        for joint in range(len(joints)):
            for channel in range(7):
                value = float(mapping[joint, channel, i])
                if value != 0:
                    affected.append(
                        dict(
                            joint=joints[joint],
                            channel=("tx", "ty", "tz", "rx", "ry", "rz", "scale")[channel],
                            coefficient=value,
                        )
                    )
        rows.append(dict(index=i, name=name, affected_joint_channels=affected))
    limits = [str(x) for x in character.parameter_limits]
    return dict(rows=rows, limits=limits, model_revision=MHR_REVISION)
