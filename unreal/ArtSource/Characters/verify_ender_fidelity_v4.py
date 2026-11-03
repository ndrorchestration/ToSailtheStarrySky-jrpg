"""V4 source geometry and art-authority validation. Engine-free only."""
import hashlib
import json
from pathlib import Path
from build_ender_fidelity_v4 import PREDECESSOR_HASHES, LANDMARKS, ORDER
from verify_ender_fidelity_v1 import check as validate_glb

REQUIRED=(
    "V4 closed facial topology cheek jaw and orbital volumes",
    "V4 L anatomically scaled ear","V4 R anatomically scaled ear",
    "V4 L shallow eye almond","V4 R shallow eye almond",
    "V4 L green iris","V4 R green iris",
    "V4 L upper lid edge","V4 R lower lid edge",
    "V4 narrow nasal dorsum","V4 restrained nasal tip",
    "V4 L alar wing","V4 R nostril shadow",
    "V3 swept front lock 00","V3 swept front lock 27",
    "V2 L tailored waistcoat cloth","V2 R tailored waistcoat cloth",
    "Full staff","Center hand wrap","Brass staff ferrule 1.83",
)

def verify(folder):
    folder=Path(folder)
    data=json.loads((folder/"receipt.json").read_text(encoding="utf-8"))
    assert data["status"]=="V4_UNRIGGED_NONCANONICAL_FACIAL_TOPOLOGY_STUDY"
    assert data["version"]=="ender_anatomy_v4"
    assert data["height_order_canon"]==ORDER
    assert data["pinned_predecessors"]==PREDECESSOR_HASHES
    assert data["model_space_landmarks_m"]=={k:list(v) for k,v in LANDMARKS.items()}
    assert data["reference_space_measured_from_approved_image"] is False
    assert "HOLD" in data["unresolved_hair_color"]
    for k in ("author_approved_likeness","cinematic_quality","approved_art_replaced",
              "v3_replaced","skinned","rigged","animation_ready","production_game_asset",
              "native_import_verified","native_render_verified","art_approval"):
        assert data[k] is False,k
    p=validate_glb(folder/data["source"]["file"],data,REQUIRED)
    assert 16000<=p["triangles"]<=28000
    assert 170<=p["named_parts"]<=240
    for rel,expected in PREDECESSOR_HASHES.items():
        from build_ender_fidelity_v4 import ROOT
        assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==expected
    return {**p,"status":"V4_GLTF_TOPOLOGY_PASS_CINEMATIC_LIKENESS_HOLD","approval":False}

if __name__=="__main__":
    import sys
    print(json.dumps(verify(Path(sys.argv[1])),indent=2))
