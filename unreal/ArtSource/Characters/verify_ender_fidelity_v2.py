"""V2 strictly checks authored cloth panels and hair cards, without assuming convexity."""
import json
from pathlib import Path
import sys
from verify_ender_fidelity_v1 import check as check_curved

REQUIRED=(
    "Sculpt face with jaw","Sculpt nose tip","Sculpt upper lip",
    "V2 crown crest","V2 tapered scalp underlayer",
    "V2 fringe hair card 00","V2 fringe hair card 22",
    "V2 L side hair card 00","V2 R side hair card 06",
    "V2 nape hair card 16","V2 L tailored waistcoat cloth",
    "V2 R tailored waistcoat cloth","V2 L shaped lapel",
    "V2 R shaped lapel","V2 chest tab 3",
)

def verify(folder):
    folder=Path(folder)
    receipt=json.loads((folder/"receipt.json").read_text(encoding="utf-8"))
    assert receipt["status"]=="NONCANONICAL_UNRIGGED_TAILORING_HAIR_V2_STUDY"
    assert receipt["original_approved_art_replaced"] is False
    assert receipt["baseline_glb_changed"] is False
    assert receipt["art_approval"] is False
    assert "NOT RESOLVED" in receipt["hair_color_state"]
    assert receipt["height_order_canon"]=="Reson > Aepex > Ender > Ionia > Lyra"
    proof=check_curved(folder/receipt["source"]["file"],receipt,required_parts=REQUIRED)
    assert 16000<=proof["triangles"]<=26000
    assert 165<=proof["named_parts"]<=240
    return {"status":"V2_UNRIGGED_SOURCE_VALIDATED_ART_HOLD",**proof,
            "approval":False,"reference_proof":"not yet established"}

if __name__=="__main__":
    if len(sys.argv)!=2:raise SystemExit("usage: verify_ender_fidelity_v2.py <candidate-folder>")
    print(json.dumps(verify(sys.argv[1]),indent=2))
