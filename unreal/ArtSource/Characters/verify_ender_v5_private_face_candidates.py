"""Private Ender face-image candidate QA; *never* commit source art or pixel marks.

Uses only Python stdlib. Requires the approved source files in a private
directory; compares full SHA-256 against the public, unapproved source registry.
The output is a private candidate QA receipt, NOT image-to-MetaHuman matching.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
from verify_ender_v5_reference_priority import verify_reference_policy, POLICY_PATH

POINTS=("eye_image_left","eye_image_right","nose_tip","chin_point")
PREFERENCES={
 "early_steampunk":"earlier-realistic-face-candidate",
 "early_jrpg":"earlier-realistic-face-candidate",
 "individual_ender":"approved-individual-stylized-crosscheck",
}
APPROVAL_GATES=(
    "source_image_file_publicly_committed","secondary_recent_shipdeck_photo_used_for_landmarks",
    "metahuman_3d_index_assigned","creator_landmark_approval","facial_sculpt_changed",
    "hair_color_resolved","character_art_promoted",
)

def png_dimensions(path:Path):
    with path.open("rb") as file:
        h=file.read(24)
    if len(h)<24 or h[:8]!=b"\x89PNG\r\n\x1a\n" or h[12:16]!=b"IHDR":
        raise ValueError("Not a PNG with IHDR: "+str(path))
    w,h=struct.unpack(">II",h[16:24])
    if w<32 or h<32 or w>16000 or h>16000:
        raise ValueError("Source PNG dimensions impossible")
    return [w,h]

def verify_private_candidate(proposal,private_directory,policy=None):
    policy=json.loads(POLICY_PATH.read_text(encoding="utf-8")) if policy is None else policy
    verify_reference_policy(policy)
    if not isinstance(proposal,dict):
        raise ValueError("Private candidate must be an object")
    if proposal.get("project")!="To Sail the Starry Sky":
        raise ValueError("Wrong project")
    if proposal.get("status")!="CANDIDATE_2D_MARKS_NOT_REVIEWED":
        raise ValueError("Unreviewed 2D proposal prematurely promoted")
    if proposal.get("landmark_names")!="image-left/right, not anatomical handedness":
        raise ValueError("Unverified anatomical left/right mapping")
    if proposal.get("coordinate_system")!="0-based original image pixels; x right, y down":
        raise ValueError("Unknown image coordinate reference")
    gates=proposal.get("guardrails")
    if not isinstance(gates,dict) or set(gates)!=set(APPROVAL_GATES):
        raise ValueError("Required fail-closed guardrails missing")
    for key in APPROVAL_GATES:
        if gates.get(key) is not False:
            raise ValueError("False approval/native mapping or public-art promotion: "+key)
    sources={r["name"]:r for r in policy["earlier_face_reference_candidates"]}
    refs=proposal.get("references")
    if not isinstance(refs,list) or len(refs)!=3:
        raise ValueError("Exactly three creator-first references required")
    if {r.get("file") for r in refs}!=set(sources):
        raise ValueError("Candidate reference inventory drift")
    if {r.get("key") for r in refs}!=set(PREFERENCES):
        raise ValueError("Known reference views/keys drift")
    directory=Path(private_directory).resolve()
    if not directory.is_dir():
        raise ValueError("Private image directory missing")
    reports=[]
    for r in refs:
        if r.get("preference")!=PREFERENCES[r["key"]]:
            raise ValueError("Unreviewed reference priority promoted")
        filename=r["file"]
        if "/" in filename or "\\" in filename or ".." in filename:
            raise ValueError("Source path traversal prohibited")
        file=(directory/filename).resolve()
        if file.parent!=directory or not file.is_file():
            raise ValueError("Private source not found")
        sha=hashlib.sha256(file.read_bytes()).hexdigest()
        if r.get("sha256")!=sha or sources[filename]["sha256"]!=sha:
            raise ValueError("Private source SHA/registry drift: "+filename)
        dimensions=png_dimensions(file)
        if dimensions!=r.get("dimensions"):
            raise ValueError("Native image dimensions mismatch")
        crop=r.get("crop")
        if not isinstance(crop,list) or len(crop)!=4 or not all(type(x) is int for x in crop):
            raise ValueError("Invalid crop")
        x0,y0,x1,y1=crop
        if not(0<=x0<x1<=dimensions[0] and 0<=y0<y1<=dimensions[1]):
            raise ValueError("Crop outside private source")
        if x1-x0<90 or y1-y0<90:
            raise ValueError("Face crop implausibly small")
        points=r.get("points")
        if not isinstance(points,dict) or set(points)!=set(POINTS):
            raise ValueError("Four distinct feature names required")
        for name in POINTS:
            point=points[name]
            if not isinstance(point,list) or len(point)!=2 or any(type(c) is not int for c in point):
                raise ValueError("Private mark must be integer original-image pixels")
            px,py=point
            if not(x0<=px<x1 and y0<=py<y1):
                raise ValueError("Candidate feature outside chosen crop")
        left,right=[points[k] for k in POINTS[:2]]
        nose=points["nose_tip"]
        chin=points["chin_point"]
        if right[0]<=left[0] or (right[0]-left[0])<10:
            raise ValueError("Image-left/right eye order or separation invalid")
        if nose[1]<=min(left[1],right[1]) or chin[1]<=nose[1]:
            raise ValueError("Nose/chin vertical order invalid, possibly wrong pose")
        eye_span=math.dist(left,right)
        face_width=x1-x0
        ratio=eye_span/face_width
        warnings=[]
        if ratio<.10 or ratio>.35:
            warnings.append("EYE_SPAN_RATIO_UNUSUAL_REQUIRES_ARTIST")
        if abs(left[1]-right[1])>eye_span*.25:
            warnings.append("OBLIQUE_EYE_LINE_CAMERA_POSE_REQUIRED")
        if r["key"]=="individual_ender":
            warnings.append("STYLIZED_INDIVIDUAL_REFERENCE_CHIN_NOSE_REQUIRES_MANUAL_RECHECK")
        reports.append({
            "source_name":filename,
            "source_sha256_match":True,
            "native_dimensions_verified":True,
            "four_points_within_crop":True,
            "eye_span_pixels":round(eye_span,3),
            "eye_span_div_crop_width":round(ratio,5),
            "warnings":warnings,
            "actual_point_coordinates_emitted":False,
            "approved_2d_annotations":False,
        })
    return {
      "status":"PRIVATE_2D_SOURCES_AND_CANDIDATE_GEOMETRY_VALID_ARTIST_HOLD",
      "source_count":3,
      "candidate_marks":12,
      "checks":reports,
      "creator_face_selection_approved":False,
      "creator_point_positions_approved":False,
      "metahuman_index_mapping_approved":False,
      "metahuman_face_edited":False,
      "production_art_promoted":False,
      "source_art_uploaded_to_public_repo":False,
      "next_gate":"Creator/artist review of exact private image marks, then validated index selection with camera calibration",
    }

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--private-proposal",type=Path,required=True)
    p.add_argument("--private-image-directory",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    x=p.parse_args()
    if x.output.exists():
        raise FileExistsError("Do not overwrite an existing private review receipt")
    d=json.loads(x.private_proposal.read_text(encoding="utf-8-sig"))
    r=verify_private_candidate(d,x.private_image_directory)
    x.output.parent.mkdir(parents=True,exist_ok=True)
    x.output.write_text(json.dumps(r,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(r,indent=2,sort_keys=True))
