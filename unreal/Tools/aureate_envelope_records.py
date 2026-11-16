"""Convert two native-review snapshots to provisional verifier input.

Coordinate system: UE centimeters and component-local bounds. Quaternion input
is Unreal XYZW; verifier quaternions use WXYZ. Never grants game authority.
"""
import math, re
ROLES=("hull","bridge","quarters","deck")
WINGS=("FORE_PORT","FORE_STARBOARD","AFT_PORT","AFT_STARBOARD")
ALL=ROLES+WINGS
def vec(v,n,name):
    if not isinstance(v,(list,tuple)) or len(v)!=n or any(isinstance(x,bool) or not isinstance(x,(float,int)) or not math.isfinite(x) for x in v):
        raise ValueError(name+" must contain finite numbers")
    return [float(x) for x in v]
def quat(v):
    x,y,z,w=vec(v,4,"quaternion")
    norm=math.sqrt(w*w+x*x+y*y+z*z)
    if abs(norm-1)>1e-4: raise ValueError("invalid unit quaternion")
    return [w/norm,x/norm,y/norm,z/norm]
def rotate(q,v):
    w,x,y,z=q; a,b,c=v
    return [(1-2*(y*y+z*z))*a+2*(x*y-w*z)*b+2*(x*z+w*y)*c,
            2*(x*y+w*z)*a+(1-2*(x*x+z*z))*b+2*(y*z-w*x)*c,
            2*(x*z-w*y)*a+2*(y*z+w*x)*b+(1-2*(x*x+y*y))*c]
def validate(snapshot,mapping):
    if not isinstance(snapshot,dict) or snapshot.get("schema")!="aureate_envelope_snapshot_v1" or snapshot.get("units")!="cm":
        raise ValueError("invalid snapshot schema/units")
    if not isinstance(snapshot.get("frame"),str) or not snapshot["frame"].strip(): raise ValueError("missing frame")
    if not isinstance(snapshot.get("map_package"),str) or not snapshot["map_package"].startswith("/Game/"): raise ValueError("invalid map package")
    if not isinstance(snapshot.get("map_sha256"),str) or not re.fullmatch(r"[0-9a-f]{64}",snapshot["map_sha256"]): raise ValueError("invalid map hash")
    if not isinstance(mapping,dict) or set(mapping)!=set(ALL) or any(not isinstance(x,str) or not x for x in mapping.values()) or len(set(mapping.values()))!=len(ALL):
        raise ValueError("mapping must uniquely specify all eight roles")
    rows=snapshot.get("actors")
    if not isinstance(rows,list): raise ValueError("invalid actors")
    lookup={}
    for row in rows:
        if not isinstance(row,dict) or not isinstance(row.get("label"),str) or not row["label"]: raise ValueError("invalid actor label")
        label=row["label"]
        if label in lookup: raise ValueError("duplicate actor label")
        lookup[label]=row
    result={}
    for role in ALL:
        a=lookup.get(mapping[role])
        if a is None: raise ValueError("missing actor "+role)
        if not isinstance(a.get("mesh"),str) or not a["mesh"]: raise ValueError("missing mesh")
        lo=vec(a.get("bounds_min"),3,"bounds_min"); hi=vec(a.get("bounds_max"),3,"bounds_max")
        if any(h<=l for l,h in zip(lo,hi)): raise ValueError("invalid bounds")
        scale=vec(a.get("scale"),3,"scale")
        if any(v<=0 for v in scale): raise ValueError("scale must be positive")
        result[role]={"mesh":a["mesh"],"lo":lo,"hi":hi,"position":vec(a.get("position"),3,"position"),"q":quat(a.get("rotation_xyzw")),"scale":scale}
    return result
def equivalent(a,b):
    return a==b
def same_rotation(a,b):
    return equivalent(a,b) or equivalent(a,[-x for x in b])
def same_geometry(a,b):
    return a["mesh"]==b["mesh"] and equivalent(a["lo"],b["lo"]) and equivalent(a["hi"],b["hi"])
def build_config(start,end,start_labels,end_labels,clearance):
    if isinstance(clearance,bool) or not isinstance(clearance,(int,float)) or not math.isfinite(clearance) or clearance<0: raise ValueError("invalid required clearance")
    a=validate(start,start_labels); b=validate(end,end_labels)
    if start["frame"]!=end["frame"]: raise ValueError("frame mismatch")
    obstacles=[]; wings=[]
    for role in ALL:
        left,right=a[role],b[role]
        if not same_geometry(left,right): raise ValueError("geometry mismatch "+role)
        center=[(x+y)/2 for x,y in zip(left["lo"],left["hi"])]
        half=[(y-x)/2 for x,y in zip(left["lo"],left["hi"])]
        if role in ROLES:
            if not (equivalent(left["position"],right["position"]) and equivalent(left["scale"],right["scale"]) and same_rotation(left["q"],right["q"])):
                raise ValueError("moving obstacle cannot be represented: "+role)
            v=rotate(left["q"],[x*y for x,y in zip(center,left["scale"])])
            part={"center":[x+y for x,y in zip(left["position"],v)],
                  "half_extents":[x*y for x,y in zip(half,left["scale"])],"rotation_quat":left["q"]}
            obstacles.append({"role":role,"parts":[part]})
        else:
            def pose(x): return {"position":x["position"],"rotation_quat":x["q"],"scale":x["scale"]}
            wings.append({"identity":role,"parts":[{"center":center,"half_extents":half}],
                          "pose_from":pose(left),"pose_to":pose(right)})
    return {"schema_version":1,"provisional":True,"units":"cm","required_clearance":float(clearance),
            "transition":"USER_SUPPLIED_ENDPOINTS_NOT_NATIVE_ANIMATION",
            "obstacles":obstacles,"wings":wings}
