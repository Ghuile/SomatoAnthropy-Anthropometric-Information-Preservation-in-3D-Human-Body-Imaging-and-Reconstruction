"""Research definitions extracted for SomatoAnthropy; provenance in docs/source_manifest.json."""

from __future__ import annotations
import numpy as np
import trimesh
from scipy.spatial import cKDTree
from somatoanthropy.geometry.anthropometry.adaptive_waist import select_adaptive
from somatoanthropy.geometry.anthropometry.engineering_wrap import RingEngine
from somatoanthropy.geometry.anthropometry.mhr_sites import anchor_position, surface_anchor
from somatoanthropy.geometry.anthropometry.three_landmark_hip import locate_landmarks

def mapped_anchors(vertices, faces, atlas):
    return {name: anchor_position(vertices, faces, atlas['anchors'][name]) for name in ('left_anterior_chest_feature', 'right_anterior_chest_feature', 'umbilicus_model_surface', 'upper_pelvis_surface')}

def project_anchors(source_vertices, source_faces, anchors):
    """Exact closest surface projection; no source reposing or optimization."""
    names = list(anchors)
    body = trimesh.Trimesh(source_vertices, source_faces, process=False)
    points, distances, face_ids = trimesh.proximity.closest_point_naive(body, np.array([anchors[n] for n in names]))
    return ({n: p for n, p in zip(names, points, strict=True)}, {n: dict(distance_m=float(d), source_face_id=int(fid), method='MHR_ATLAS_POINT_PROJECTED_TO_RELEASED_SOURCE_SURFACE') for n, d, fid in zip(names, distances, face_ids, strict=True)})

def source_region_mask(vertices, faces, mhr_vertices, mhr_faces, mhr_mask):
    """Transfer the existing pelvic region using nearest surface-face centres.

    This is an engineering correspondence, not participant landmark annotation.
    It does not deform either source or MHR surface.
    """
    centres = np.asarray(mhr_vertices)[mhr_faces].mean(axis=1)
    ids = cKDTree(centres).query(np.asarray(vertices)[faces].mean(axis=1))[1]
    return np.asarray(mhr_mask, dtype=bool)[ids]

def measure(vertices, faces, seed, anchors, pelvis_mask):
    engine = RingEngine(vertices, faces, seed[[0, 2]], reject_contact=False)
    chest_y = float((anchors['left_anterior_chest_feature'][1] + anchors['right_anterior_chest_feature'][1]) / 2)
    abdomen_y = float(anchors['umbilicus_model_surface'][1])
    sites = dict(chest=engine.section(chest_y), abdomen=engine.section(abdomen_y))
    if chest_y <= abdomen_y:
        raise ValueError('INVALID_RELEASED_ABDOMEN_CHEST_INTERVAL')
    count = int(np.ceil((chest_y - abdomen_y) / 0.005)) + 1
    levels = [y for y in np.linspace(abdomen_y, chest_y, count) if (y - abdomen_y) / (chest_y - abdomen_y) <= 0.5 + 1e-12]
    midpoint = (abdomen_y + chest_y) / 2
    levels = [y for y in levels if abs(y - midpoint) > 1e-12] + [midpoint]
    profile = []
    for y in sorted(levels):
        q = engine.section(float(y))
        profile.append(dict(normalized_height=float((y - abdomen_y) / (chest_y - abdomen_y)), raw_contour_cm=q.get('raw_contour_cm'), quality_state='PROXY_VALID' if q['geometry_quality'] == 'VALID' else 'CONTOUR_INVALID', world_y_m=float(y)))
    selection = select_adaptive(profile, 0.5, 0.01)
    if 'selected_normalized_height' in selection:
        waist_y = abdomen_y + selection['selected_normalized_height'] * (chest_y - abdomen_y)
        fallback = False
    else:
        waist_y = abdomen_y + 0.005
        fallback = True
    waist = engine.section(float(waist_y))
    waist.update(selection=selection, search_profile=profile, fallback_applied=fallback, search_interval_world_y_m=[abdomen_y, midpoint])
    sites['waist'] = waist
    try:
        crotch_attachment = surface_anchor(vertices, faces, pelvis_mask, seed, 1, False)
        crotch = anchor_position(vertices, faces, crotch_attachment)
        upper = anchors['upper_pelvis_surface']
        landmark = locate_landmarks(vertices, faces, pelvis_mask, float(crotch[1]), float(upper[1]))['A']
        hip = engine.section(float(landmark['point_m'][1]))
        hip.update(selected_landmark='A', landmarks={'A': landmark}, search_interval_world_y_m=[float(crotch[1]), float(upper[1])], crotch_point_m=crotch.tolist(), upper_gluteal_point_m=upper.tolist())
        if hip['geometry_quality'] == 'VALID':
            hip['points_m'] = hip['tape_points_m']
        sites['hip'] = hip
    except ValueError as error:
        sites['hip'] = dict(geometry_quality='INVALID', reason=str(error), value_cm=None, points_m=[], selected_landmark='A')
    for site, q in sites.items():
        quantity = 'tape_envelope_cm' if site == 'hip' else 'raw_contour_cm'
        q.update(interpretation_status='ENGINEERING_INTERPRETATION', engineering_value_cm=q.get(quantity), quantity=quantity, scientific_margins_approved=False, iso_conformance_claim=False)
    return (sites, engine)

def differences(source, mhr, matched_engine):
    rows = []
    for site in ('chest', 'waist', 'abdomen', 'hip'):
        a, b = (source[site], mhr[site])
        quantity = 'tape_envelope_cm' if site == 'hip' else 'raw_contour_cm'
        valid = a['geometry_quality'] == b['geometry_quality'] == 'VALID'
        source_value = a.get(quantity)
        target_value = b.get(quantity)
        primary = dict(site=site, mode='OWN_LATEST_RULES', source_cm=source_value, mhr_cm=target_value, valid=valid, signed_difference_cm=target_value - source_value if valid else None, source_reason=a['reason'], mhr_reason=b['reason'], source_limb_contact=a.get('limb_overlap', False), mhr_limb_contact=b.get('limb_overlap', False))
        rows.append(primary)
        if a['geometry_quality'] == 'VALID':
            same = matched_engine.section(a['plane_origin_m'][1])
            other = same.get(quantity)
            same_valid = same['geometry_quality'] == 'VALID'
            rows.append(dict(site=site, mode='SOURCE_PLANE_DIAGNOSTIC', source_cm=source_value, mhr_cm=other, valid=same_valid, signed_difference_cm=other - source_value if same_valid else None, source_reason=a['reason'], mhr_reason=same['reason'], source_limb_contact=a.get('limb_overlap', False), mhr_limb_contact=same.get('limb_overlap', False)))
        else:
            rows.append(dict(primary, mode='SOURCE_PLANE_DIAGNOSTIC', valid=False, signed_difference_cm=None, mhr_cm=None))
    return rows
