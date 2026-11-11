"""Generate original, source-controlled, noncanonical 3D party-equipment review GLBs.
Three members ONLY: Ender and Ionia in the opening; Lyra joins after splashdown.
Source coordinates: glTF 2.0 Y-up, meters. Models are static; fitting requires rig review.
"""
import hashlib, json, math, struct
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "Generated"
TAU = math.tau
# base RGB, metallic, roughness, emissive
PALETTE = {
 "wood":([.19,.087,.045,1],0,.76,None),"leather":([.095,.050,.032,1],.03,.81,None),
 "cloth":([.065,.12,.16,1],0,.88,None),"linen":([.50,.44,.34,1],0,.83,None),
 "brass":([.58,.40,.15,1],.83,.35,None),"gold":([.82,.63,.27,1],.87,.24,None),
 "steel":([.48,.57,.60,1],.9,.29,None),"iron":([.12,.16,.18,1],.74,.51,None),
 "teal":([.04,.38,.42,1],.30,.30,[.004,.09,.10]),
 "earth":([.32,.41,.21,1],.16,.58,None),
 "water":([.12,.38,.66,1],.26,.25,[.008,.04,.12]),
 "glass":([.13,.27,.33,1],.14,.15,[.008,.03,.035]),
 "white":([.81,.81,.74,1],.05,.45,None),
}
ITEMS = [
 # owner, ID, gameplay slot, geometry family, stage, narrative note
 ("Ender","ResonanceStaff","weapon","existing_staff","prelude","Use preserved centered-wrap, double-ferrule source"),
 ("Ender","EngineersVest","armor","vest","prelude","Working engineer layered leather/cloth"),
 ("Ender","SealedAviatorGoggles","accessory","goggles","prelude","Twin sealed protective lenses, character-fit pending"),
 ("Ender","HarmonicCalibrationKit","utility","case","prelude","Portable engine tools, no innate magic grant"),
 ("Ionia","CaptainSaber","weapon","saber","prelude","Provisional captain sidearm"),
 ("Ionia","CaptainsCoat","armor","coat","prelude","Provisional travel-worn captain outfit"),
 ("Ionia","EarthCompass","accessory","compass","prelude","Earth affinity design motif; not an ability"),
 ("Ionia","ChartCase","utility","case","prelude","Navigation instruments and charts"),
 ("Lyra","WaterFocus","weapon","focus","post_splashdown","Provisional water-channeling implement"),
 ("Lyra","TravelCoat","armor","coat","post_splashdown","Provisional traveler outfit"),
 ("Lyra","WaterPendant","accessory","pendant","post_splashdown","Water affinity design motif"),
 ("Lyra","HealersSatchel","utility","satchel","post_splashdown","Healing supplies prop; not free spells"),
 ("Shared","RestorativeVial","prop","vial","post_splashdown","Scene prop; not an unlocked consumable"),
 ("Shared","ResonanceCapacitor","prop","capacitor","prelude","Engine repair prop, noncanonical"),
]
ACCENT={"Ender":"teal","Ionia":"earth","Lyra":"water","Shared":"brass"}
class Mesh:
 def __init__(self): self.geo={k:[] for k in PALETTE}
 def add(self,mat,v,f):
  vv=np.asarray(v,np.float32); ff=np.asarray(f,np.uint32)
  if len(vv)<3 or len(ff)<1 or not np.isfinite(vv).all(): raise ValueError("bad geometry")
  self.geo[mat].append((vv,ff))
 def box(self,x,y,z,sx,sy,sz,mat):
  p=np.array([x,y,z],np.float32)
  v=np.array([[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]],np.float32)
  v=v*np.array([sx,sy,sz],np.float32)/2+p
  f=[(0,2,1),(0,3,2),(4,5,6),(4,6,7),(0,1,5),(0,5,4),
     (1,2,6),(1,6,5),(2,3,7),(2,7,6),(3,0,4),(3,4,7)]
  self.add(mat,v,f)
 def bar(self,p,q,r,mat,sides=16):
  a=np.array(p,float);b=np.array(q,float);v0=b-a
  v0/=np.linalg.norm(v0)
  u=np.cross(v0,[0,0,1])
  if np.linalg.norm(u)<.01:u=np.cross(v0,[1,0,0])
  u/=np.linalg.norm(u);w=np.cross(v0,u)
  v=[];f=[]
  for c in (a,b):
   for i in range(sides):
    ang=TAU*i/sides;v.append(c+r*(u*math.cos(ang)+w*math.sin(ang)))
  for i in range(sides):
   j=(i+1)%sides;f.extend([(i,j,i+sides),(j,j+sides,i+sides)])
  self.add(mat,v,f)
 def cylinder(self,y0,y1,r,mat,x=0,z=0,top=None,sides=24):
  if top is None:top=r
  v=[];f=[]
  for y,rr in ((y0,r),(y1,top)):
   for i in range(sides):
    a=i*TAU/sides;v.append((x+rr*math.cos(a),y,z+rr*math.sin(a)))
  v.extend(((x,y0,z),(x,y1,z)))
  for i in range(sides):
   j=(i+1)%sides;f.extend([(i,j,i+sides),(j,j+sides,i+sides),
                           (2*sides,j,i),(2*sides+1,i+sides,j+sides)])
  self.add(mat,v,f)
 def orb(self,x,y,z,rx,ry,rz,mat,rings=12,sides=24):
  v=[];f=[]
  for i in range(rings+1):
   phi=(i+.001)*math.pi/(rings+.002)
   for j in range(sides):
    ang=j*TAU/sides
    v.append((x+rx*math.sin(phi)*math.cos(ang),y+ry*math.cos(phi),
              z+rz*math.sin(phi)*math.sin(ang)))
  for i in range(rings):
   for j in range(sides):
    a=i*sides+j;b=i*sides+(j+1)%sides
    f.extend([(a,b,a+sides),(b,b+sides,a+sides)])
  self.add(mat,v,f)
 def ring(self,x,y,z,r,minor,mat,axis="z",sides=32,tube=10):
  v=[];f=[]
  for i in range(sides):
   a=TAU*i/sides
   for j in range(tube):
    b=TAU*j/tube;rr=r+minor*math.cos(b)
    if axis=="z": v.append((x+rr*math.cos(a),y+rr*math.sin(a),z+minor*math.sin(b)))
    else: v.append((x+rr*math.cos(a),y+minor*math.sin(b),z+rr*math.sin(a)))
  for i in range(sides):
   for j in range(tube):
    aa=i*tube+j;bb=((i+1)%sides)*tube+j;cc=i*tube+(j+1)%tube;dd=((i+1)%sides)*tube+(j+1)%tube
    f.extend([(aa,bb,cc),(bb,dd,cc)])
  self.add(mat,v,f)
 def sword_blade(self,points,width,mat):
  v=[];f=[]
  for x,y,r in points:v.extend([(x-r,y,0),(x,y,width),(x+r,y,0),(x,y,-width)])
  for i in range(len(points)-1):
   for j in range(4):
    a=i*4+j;b=i*4+(j+1)%4;c=a+4;d=b+4
    f.extend([(a,b,c),(b,d,c)])
  f.extend([(0,2,1),(0,3,2)])
  self.add(mat,v,f)
 def glb(self,path,label):
  binary=bytearray();views=[];acc=[];prims=[];materials=[]
  def store(arr,target):
   while len(binary)%4:binary.append(0)
   off=len(binary);binary.extend(arr.tobytes())
   views.append({"buffer":0,"byteOffset":off,"byteLength":arr.nbytes,"target":target})
   return len(views)-1
  def access(arr,typ,component,target):
   arr=np.ascontiguousarray(arr)
   obj={"bufferView":store(arr,target),"componentType":component,"count":len(arr),"type":typ}
   if typ=="VEC3":
    obj["min"]=np.min(arr,axis=0).astype(float).tolist()
    obj["max"]=np.max(arr,axis=0).astype(float).tolist()
   acc.append(obj)
   return len(acc)-1
  triangles=0
  for key,parts in self.geo.items():
   if not parts:continue
   vlist=[];flist=[];offset=0
   for vv,ff in parts:
    vlist.append(vv);flist.append(ff+offset);offset+=len(vv)
   v=np.concatenate(vlist).astype(np.float32);f=np.concatenate(flist).astype(np.uint32)
   triangles+=len(f)
   normals=np.zeros_like(v)
   e=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]])
   for j in range(3):np.add.at(normals,f[:,j],e)
   normals/=np.maximum(np.linalg.norm(normals,axis=1,keepdims=True),1e-14)
   color,metal,rough,emit=PALETTE[key]
   material={"name":key,"doubleSided":True,
     "pbrMetallicRoughness":{"baseColorFactor":color,"metallicFactor":metal,"roughnessFactor":rough}}
   if emit:material["emissiveFactor"]=emit
   mi=len(materials);materials.append(material)
   prims.append({"attributes":{"POSITION":access(v,"VEC3",5126,34962),
     "NORMAL":access(normals.astype(np.float32),"VEC3",5126,34962)},
     "indices":access(f.reshape(-1),"SCALAR",5125,34963),"material":mi})
  if not prims: raise ValueError("empty model")
  doc={"asset":{"version":"2.0","generator":"TSTSS Original Party Equipment Source v1"},
    "scene":0,"scenes":[{"nodes":[0]}],"nodes":[{"mesh":0,"name":label}],
    "meshes":[{"name":label,"primitives":prims}],"buffers":[{"byteLength":len(binary)}],
    "bufferViews":views,"accessors":acc,"materials":materials,
    "extras":{"creator_approved":False,"review_only":True,"skills_granted":False,"rigged":False}}
  j=json.dumps(doc,separators=(",",":")).encode()
  while len(j)%4:j+=b" "
  while len(binary)%4:binary.append(0)
  blob=(b"glTF"+struct.pack("<II",2,12+8+len(j)+8+len(binary))
       +struct.pack("<I4s",len(j),b"JSON")+j
       +struct.pack("<I4s",len(binary),b"BIN\x00")+binary)
  if path.exists():raise FileExistsError(str(path))
  path.write_bytes(blob)
  return {"sha256":hashlib.sha256(blob).hexdigest(),"bytes":len(blob),
          "triangles":triangles,"material_slots":len(materials),"mesh_count":1}

def make(owner,model_id,shape):
 m=Mesh();accent=ACCENT[owner]
 if shape=="vest" or shape=="coat":
  # Stylized torso wearable preview; NOT skin- or character-conforming.
  m.box(0,0,0,.44,.64,.25,"cloth" if owner!="Lyra" else "linen")
  m.box(0,.23,.01,.36,.08,.29,"leather")
  for s in (-1,1):
   m.box(s*.23,.18,.015,.14,.16,.31,"leather")
   m.box(s*.15,-.25,-.14,.06,.40,.04,"brass")
   m.box(s*.18,-.08,.15,.095,.18,.032,accent)
  m.box(0,-.23,.05,.44,.075,.29,"leather")
  for x in (-.12,.12):m.orb(x,-.23,.198,.017,.018,.014,"gold")
  if shape=="coat":
   m.box(-.13,-.48,0,.19,.47,.27,"cloth")
   m.box(.13,-.48,0,.19,.47,.27,"cloth")
   m.box(0,.27,-.05,.18,.16,.11,"linen")
   m.bar((-.06,.26,.15),(.08,-.20,.15),.014,"brass")
  else:
   m.box(-.08,.10,.15,.14,.15,.028,"leather")
   m.box(.08,.10,.15,.14,.15,.028,"leather")
 elif shape=="goggles":
  for x in (-.055,.055):
   m.cylinder(-.018,.018,.046,"brass",x,0)
   m.orb(x,0,.023,.043,.043,.008,"glass")
   m.ring(x,0,.023,.044,.006,"gold")
   m.box(x,-.04,-.016,.095,.009,.04,"leather")
  m.bar((-.02,0,0),(.02,0,0),.012,"leather")
  m.bar((-.10,-.012,-.018),(-.17,-.014,-.018),.011,"leather")
  m.bar((.10,-.012,-.018),(.17,-.014,-.018),.011,"leather")
 elif shape=="saber":
  m.cylinder(-.33,-.06,.018,"leather")
  m.orb(0,-.34,0,.027,.026,.027,"gold")
  m.bar((-.11,-.045,0),(.11,-.045,0),.011,"brass")
  m.sword_blade([(0,-.045,.024),(.01,.13,.032),(.042,.31,.027),(.065,.54,.016),(.070,.71,.001)],.009,"steel")
  m.orb(0,-.04,0,.023,.015,.022,accent)
 elif shape=="focus":
  m.cylinder(-.48,.22,.013,"wood")
  for yy in (-.42,-.09,.17):m.cylinder(yy,yy+.026,.02,"brass")
  m.orb(0,.32,0,.061,.105,.047,"water")
  m.ring(0,.32,0,.067,.009,"gold")
  for s in (-1,1):m.bar((s*.058,.29,0),(s*.012,.40,0),.006,"brass")
  m.orb(0,-.48,0,.024,.025,.024,"brass")
 elif shape in ("compass","pendant"):
  m.orb(0,0,0,.075,.075,.013,"brass")
  m.orb(0,0,.018,.061,.061,.012,accent)
  m.ring(0,0,.023,.067,.007,"gold")
  for i in range(8):
   a=TAU*i/8;m.bar((.049*math.cos(a),.049*math.sin(a),.033),
     (.056*math.cos(a),.056*math.sin(a),.033),.004,"steel")
  m.bar((0,0,.039),(.0,.038,.04),.005,"white")
  m.ring(0,.088,0,.012,.004,"brass")
  if shape=="pendant":
   m.bar((-.013,.089,0),(-.16,.20,0),.0025,"leather")
   m.bar((.013,.089,0),(.16,.20,0),.0025,"leather")
 elif shape=="case":
  m.box(0,0,0,.29,.18,.16,"leather")
  m.box(0,.10,0,.29,.025,.16,"brass")
  m.box(0,.05,.09,.065,.05,.013,"gold")
  m.bar((-.045,.11,-.02),(-.045,.17,-.02),.008,"iron")
  m.bar((.045,.11,-.02),(.045,.17,-.02),.008,"iron")
  m.bar((-.045,.17,-.02),(.045,.17,-.02),.008,"iron")
  for x in (-.122,.122):
   for z in (-.067,.067):m.orb(x,.03,z,.007,.007,.007,"brass")
 elif shape=="satchel":
  m.box(0,-.03,0,.25,.21,.12,"leather")
  m.box(0,.07,.067,.25,.10,.02,"linen")
  m.box(0,.01,.082,.035,.035,.015,"gold")
  m.bar((-.11,.08,0),(-.13,.34,0),.012,"leather")
  m.bar((.11,.08,0),(.13,.34,0),.012,"leather")
  m.bar((-.13,.34,0),(.13,.34,0),.012,"leather")
  for i in range(3):
   m.cylinder(.045,.18,.015,"glass",x=(i-1)*.068,z=-.07)
   m.cylinder(.18,.20,.018,"brass",x=(i-1)*.068,z=-.07)
 elif shape=="vial":
  m.cylinder(-.06,.085,.023,"glass")
  m.cylinder(.087,.114,.027,"wood")
  m.cylinder(-.049,.035,.022,"water")
  m.ring(0,.043,0,.024,.003,"brass",axis="y")
 elif shape=="capacitor":
  m.cylinder(-.12,.12,.04,"iron")
  m.cylinder(-.15,-.11,.056,"brass")
  m.cylinder(.11,.15,.056,"brass")
  m.cylinder(-.086,.086,.045,"teal")
  for i in range(8):
   t=i*TAU/8
   m.bar((.054*math.cos(t),-.12,.054*math.sin(t)),
         (.054*math.cos(t),.12,.054*math.sin(t)),.005,"gold")
  m.orb(0,.165,0,.03,.023,.03,"steel")
 else:raise ValueError(shape)
 return m

def validate_glb(path):
 raw=path.read_bytes()
 if raw[:4]!=b"glTF" or struct.unpack_from("<II",raw,4)!=(2,len(raw)):
  raise ValueError("invalid glb header: "+path.name)
 jl,jt=struct.unpack_from("<I4s",raw,12)
 if jt!=b"JSON" or jl%4:raise ValueError("invalid glb json")
 doc=json.loads(raw[20:20+jl])
 if len(doc["meshes"])!=1 or doc.get("skins") or doc.get("animations"):
  raise ValueError("not a static review mesh")
 mins=[];maxs=[]
 for p in doc["meshes"][0]["primitives"]:
  pos=doc["accessors"][p["attributes"]["POSITION"]]
  mins.append(pos["min"]);maxs.append(pos["max"])
 return {"bounds_m":[[min(x[i] for x in mins),max(x[i] for x in maxs)] for i in range(3)],
         "primitives":len(doc["meshes"][0]["primitives"])}

def main():
 OUT.mkdir(exist_ok=True)
 manifest={"schema_version":1,"generator":"generate_party_equipment.py",
  "source_convention":"glTF2 Y-up meters; UE imported length in cm",
  "review_only":True,"creator_approved":False,
  "automatic_item_grants":False,"spells_granted":False,
  "available_party":["Ender","Ionia"],"joins_post_splashdown":["Lyra"],
  "excluded_party":["Reson","Aepex"],"entries":[]}
 for owner,name,slot,shape,stage,note in ITEMS:
  filename=f"{owner}_{name}_REVIEW.glb"
  path=OUT/filename
  record={"owner":owner,"id":f"{owner}.{name}","slot":slot,
   "stage":stage,"notes":note,"relative_path":f"Generated/{filename}",
   "rig_attached":False,"collision_tested":False,"creator_approved":False,
   "runtime_equippable":False,"is_full_character_outfit":False}
  if shape=="existing_staff":
   # Deterministic provenance-checked existing reviewed model; do not regenerate/copy here.
   src=Path(r"C:\TSTSS_EnderStaffV1_20261104\private_generated\Ender_DoubleFerrule_CenteredWrap_Staff_V1_NONCANONICAL.glb")
   if not src.exists():raise FileNotFoundError("Missing reviewed original staff: "+str(src))
   if path.exists():raise FileExistsError(str(path))
   path.write_bytes(src.read_bytes())
   record["reused_prior_review_staff"]=True
   record["static_import_only"]=True
  else:
   record.update(make(owner,name,shape).glb(path,name))
  record.update(validate_glb(path))
  record["sha256"]=hashlib.sha256(path.read_bytes()).hexdigest()
  manifest["entries"].append(record)
  print(owner,name,record["sha256"][:12],record["bounds_m"])
 output=HERE/"party_equipment_manifest.review.json"
 if output.exists():raise FileExistsError(str(output))
 output.write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
 print("COMPLETE",len(manifest["entries"]),"models",sum(x["bytes"] for x in manifest["entries"] if "bytes" in x)/1024/1024,"MiB")

if __name__=="__main__": main()
