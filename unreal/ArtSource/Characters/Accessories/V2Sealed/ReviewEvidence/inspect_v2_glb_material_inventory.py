"""Read-only glTF/GLB material inventory and bounded model-space lens/strap hints."""
from pathlib import Path
import json,struct,hashlib,math
P=Path(r"C:\Users\Admin\work\TSTSS-V5-FaceAuthorityReview-20261103\V2_Sealed_Goggles_Output\Ender_Sealed_Aviator_Goggles_V2_NONCANONICAL.glb")
sha="5b1b5c5ac0b1be754d9e19b3bd9cec293c819259d18b39e8ad8f56228d22b5cb"
data=P.read_bytes()
assert hashlib.sha256(data).hexdigest()==sha
assert data[:4]==b"glTF"
n,kind=struct.unpack_from("<I4s",data,12)
assert kind==b"JSON"
obj=json.loads(data[20:20+n])
print("SOURCE_SHA",sha,"MESHES",len(obj.get("meshes",[])),"MATERIALS",len(obj.get("materials",[])))
for i,m in enumerate(obj.get("materials",[])):
    p=m.get("pbrMetallicRoughness",{})
    print(json.dumps({"index":i,"name":m.get("name"),"base_color":p.get("baseColorFactor"),
     "metallic":p.get("metallicFactor"),"roughness":p.get("roughnessFactor"),
     "alphaMode":m.get("alphaMode","OPAQUE"),"alphaCutoff":m.get("alphaCutoff"),
     "doubleSided":m.get("doubleSided",False),"extensions":list(m.get("extensions",{}).keys()),
     "emissive":m.get("emissiveFactor")},sort_keys=True))
print("IMAGES",len(obj.get("images",[])),"TEXTURES",len(obj.get("textures",[])))
