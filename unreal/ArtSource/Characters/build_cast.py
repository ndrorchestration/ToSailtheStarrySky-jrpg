#!/usr/bin/env python3
"""Original stylized TSTSS character lookdev. Generates glTF 2.0 GLB static meshes.

No third-party mesh/texture assets. These are articulated-looking static art studies,
not skinned or game-ready characters. Coordinates: metres, Y up, +Z forward.
"""
import json, math, struct, pathlib, hashlib
from dataclasses import dataclass

OUT = pathlib.Path(__file__).resolve().parent / 'out'
OUT.mkdir(exist_ok=True)

PALETTES = {
 'Ender': dict(height=1.74, build=.92, skin='#c99972', hair='#354c35', shirt='#e8d9b8', coat='#667044', pants='#45443d', boots='#49372c', trim='#bb8951', accent='#277c76', eyes='#3aaa68'),
 'Ionia': dict(height=1.68, build=.88, skin='#deb18c', hair='#c99a56', shirt='#efe4d3', coat='#253a52', pants='#384753', boots='#48362b', trim='#d9b364', accent='#537d8f', eyes='#529469'),
 'Lyra': dict(height=1.65, build=.84, skin='#d9a782', hair='#a3472d', shirt='#eee0ca', coat='#315772', pants='#3b5365', boots='#55402d', trim='#bd9256', accent='#4f8c98', eyes='#6f9e82'),
 'Reson': dict(height=1.93, build=1.18, skin='#ad7656', hair='#372e27', shirt='#e0ceb2', coat='#554434', pants='#4b443e', boots='#382b23', trim='#b78c5a', accent='#8a3f31', eyes='#6d8567'),
 'Aepex': dict(height=1.85, build=.96, skin='#bf8969', hair='#714a2d', shirt='#c9bda3', coat='#3f3c39', pants='#353839', boots='#382d27', trim='#bd8753', accent='#923e32', eyes='#77918b')
}

def rgb(h):
 return [int(h[i:i+2],16)/255 for i in (1,3,5)] + [1]

class Builder:
 def __init__(self, name):
  self.name=name; self.parts=[]; self.materials=[]; self.mat_ids={}
 def mat(self, color, metal=0, rough=.8):
  k=(color,metal,rough)
  if k not in self.mat_ids:
   self.mat_ids[k]=len(self.materials)
   self.materials.append({'name':color,'pbrMetallicRoughness':{'baseColorFactor':rgb(color),'metallicFactor':metal,'roughnessFactor':rough},'doubleSided':True})
  return self.mat_ids[k]
 def mesh(self, name, verts, faces, color, metal=0, rough=.8):
  # Flat faces are retained as editable named parts; vertex normals provide smooth shading.
  normals=[[0.,0.,0.] for _ in verts]
  for a,b,c in faces:
   u=[verts[b][j]-verts[a][j] for j in range(3)]
   v=[verts[c][j]-verts[a][j] for j in range(3)]
   n=(u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
   for i in (a,b,c):
    for j in range(3):normals[i][j]+=n[j]
  normals=[tuple(t/max(math.sqrt(sum(x*x for x in n)),1e-9) for t in n) for n in normals]
  self.parts.append((name,verts,normals,faces,self.mat(color,metal,rough)))
 def ellipsoid(self,name,center,radii,color,segments=16,rings=10,metal=0,rough=.8):
  cx,cy,cz=center;rx,ry,rz=radii;vs=[];fs=[]
  for j in range(rings+1):
   phi=math.pi*j/rings
   for i in range(segments):
    th=2*math.pi*i/segments
    vs.append((cx+rx*math.sin(phi)*math.cos(th),cy+ry*math.cos(phi),cz+rz*math.sin(phi)*math.sin(th)))
  for j in range(rings):
   for i in range(segments):
    a=j*segments+i;b=j*segments+(i+1)%segments;c=b+segments;d=a+segments
    fs.extend(((a,d,b),(b,d,c)))
  self.mesh(name,vs,fs,color,metal,rough)
 def tube(self,name,points,radii,color,sides=10,metal=0,rough=.8):
  vs=[];fs=[]
  for k,p in enumerate(points):
   p0=points[max(0,k-1)];p1=points[min(len(points)-1,k+1)]
   t=[p1[i]-p0[i] for i in range(3)];tl=math.sqrt(sum(x*x for x in t)) or 1;t=[x/tl for x in t]
   axis=[0,0,1] if abs(t[2])<.9 else [1,0,0]
   u=[t[1]*axis[2]-t[2]*axis[1],t[2]*axis[0]-t[0]*axis[2],t[0]*axis[1]-t[1]*axis[0]]
   ul=math.sqrt(sum(x*x for x in u)) or 1;u=[x/ul for x in u]
   v=[t[1]*u[2]-t[2]*u[1],t[2]*u[0]-t[0]*u[2],t[0]*u[1]-t[1]*u[0]]
   rr=radii[k] if isinstance(radii,list) else radii
   for i in range(sides):
    th=2*math.pi*i/sides
    vs.append(tuple(p[j]+rr*(math.cos(th)*u[j]+math.sin(th)*v[j]) for j in range(3)))
  for k in range(len(points)-1):
   for i in range(sides):
    a=k*sides+i;b=k*sides+(i+1)%sides;c=b+sides;d=a+sides
    fs.extend(((a,d,b),(b,d,c)))
  self.mesh(name,vs,fs,color,metal,rough)
 def tapered(self,name,a,b,ra,rb,color,metal=0,rough=.8):
  self.tube(name,[a,b],[ra,rb],color,12,metal,rough)
 def save(self,path):
  buffer=bytearray();views=[];access=[];primitives=[]
  def write(raw,target):
   while len(buffer)%4:buffer.append(0)
   off=len(buffer);buffer.extend(raw);v=len(views);views.append({'buffer':0,'byteOffset':off,'byteLength':len(raw),'target':target});return v
  # One glTF mesh per character. Group by material so Unreal imports a single
  # review mesh with a bounded number of sections rather than 50+ loose assets.
  groups={}
  part_map=[]
  for name,verts,norms,faces,mat in self.parts:
   group=groups.setdefault(mat,{'verts':[],'norms':[],'indices':[]})
   start=len(group['verts'])
   group['verts'].extend(verts);group['norms'].extend(norms)
   group['indices'].extend(start+i for face in faces for i in face)
   part_map.append({'name':name,'material':mat,'firstVertex':start,'vertexCount':len(verts)})
  for mat,group in sorted(groups.items()):
   verts=group['verts'];norms=group['norms'];indices=group['indices']
   if max(indices,default=0)>65535:raise ValueError('16-bit material section overflow')
   v=write(b''.join(struct.pack('<3f',*p) for p in verts),34962)
   pa=len(access);access.append({'bufferView':v,'componentType':5126,'count':len(verts),'type':'VEC3','min':[min(p[j] for p in verts) for j in range(3)],'max':[max(p[j] for p in verts) for j in range(3)]})
   v=write(b''.join(struct.pack('<3f',*p) for p in norms),34962)
   no=len(access);access.append({'bufferView':v,'componentType':5126,'count':len(norms),'type':'VEC3'})
   v=write(struct.pack('<%dH'%len(indices),*indices),34963)
   ix=len(access);access.append({'bufferView':v,'componentType':5123,'count':len(indices),'type':'SCALAR','min':[0],'max':[max(indices)]})
   primitives.append({'attributes':{'POSITION':pa,'NORMAL':no},'indices':ix,'material':mat})
  while len(buffer)%4:buffer.append(0)
  doc={'asset':{'version':'2.0','generator':'TSTSS original lookdev generator v2'},'scene':0,'scenes':[{'name':self.name+' lookdev','nodes':[0]}], 'nodes':[{'name':self.name+'_lookdev','mesh':0}], 'meshes':[{'name':self.name+'_lookdev','primitives':primitives,'extras':{'partMap':part_map}}], 'materials':self.materials,'buffers':[{'byteLength':len(buffer)}],'bufferViews':views,'accessors':access}
  js=json.dumps(doc,separators=(',',':')).encode()
  js+=b' ' * ((-len(js))%4)
  data=b'glTF'+struct.pack('<II',2,12+8+len(js)+8+len(buffer))+struct.pack('<I4s',len(js),b'JSON')+js+struct.pack('<I4s',len(buffer),b'BIN\0')+buffer
  path.write_bytes(data)
  return {'file':path.name,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'mesh_parts':len(self.parts),'mesh_count':1,'material_sections':len(primitives),'materials':len(self.materials)}

def make(name):
 p=PALETTES[name];b=Builder(name);h=p['height'];s=h/1.74;w=p['build'];
 # Anatomy and layered clothing; each component has its own edit/replacement boundary.
 b.ellipsoid('Head sculpt', (0,1.50*s,.015),(.112*w,.145*s,.105),p['skin'],20,14)
 b.tapered('Neck',(0,1.38*s,0),(0,1.48*s,0),.053,.049,p['skin'])
 b.ellipsoid('Hair crown',(0,1.62*s,-.012),(.124*w,.095*s,.112),p['hair'],20,10)
 b.ellipsoid('Left ear',(-.118*w,1.50*s,.01),(.022,.044,.026),p['skin'])
 b.ellipsoid('Right ear',(.118*w,1.50*s,.01),(.022,.044,.026),p['skin'])
 b.ellipsoid('Torso shirt',(0,1.13*s,0),(.198*w,.264*s,.105),p['shirt'],20,12)
 b.ellipsoid('Tailored outer layer',(0,1.13*s,-.024),(.205*w,.258*s,.105),p['coat'],20,12)
 b.ellipsoid('Front shirt opening',(0,1.165*s,.084),(.074*w,.215*s,.023),p['shirt'],16,10)
 b.tapered('Waist belt',(-.19*w,.91*s,.086),(.19*w,.91*s,.086),.021,.021,p['boots'])
 b.ellipsoid('Belt buckle',(0,.91*s,.11),(.031,.028,.013),p['trim'],12,8,.8,.3)
 b.ellipsoid('Pelvis',(0,.82*s,0),(.18*w,.13*s,.103),p['pants'])
 for side,sgn in [('L',-1),('R',1)]:
  x=sgn*.138*w
  b.ellipsoid(side+' shoulder',(x,1.295*s,0),(.080*w,.075,.081),p['coat'])
  b.tapered(side+' upper sleeve',(x,1.29*s,0),(sgn*.233*w,1.085*s,0),.069*w,.058*w,p['shirt'])
  b.ellipsoid(side+' sleeve cuff',(sgn*.233*w,1.075*s,0),(.06*w,.024,.064),p['coat'])
  b.tapered(side+' forearm',(sgn*.233*w,1.07*s,0),(sgn*.255*w,.88*s,.035),.052*w,.037*w,p['skin'])
  b.ellipsoid(side+' hand',(sgn*.255*w,.846*s,.037),(.039*w,.058,.031),p['skin'])
  b.tapered(side+' thigh',(sgn*.092*w,.78*s,0),(sgn*.111*w,.49*s,0),.091*w,.075*w,p['pants'])
  b.ellipsoid(side+' knee',(sgn*.111*w,.465*s,.011),(.078*w,.082,.078),p['pants'])
  b.tapered(side+' shin',(sgn*.112*w,.47*s,0),(sgn*.116*w,.14*s,0),.072*w,.056*w,p['boots'] if name in ('Ionia','Reson') else p['pants'])
  b.ellipsoid(side+' boot',(sgn*.116*w,.095*s,.047),(.078*w,.105*s,.135),p['boots'],16,10)
  b.tapered(side+' boot cuff',(sgn*.116*w,.19*s,0),(sgn*.116*w,.27*s,0),.077*w,.070*w,p['boots'])
  b.tapered(side+' boot trim',(sgn*.116*w,.195*s,.068),(sgn*.116*w,.195*s,.075),.013,.013,p['trim'],.5,.5)
 # Eyes, irises, catchlights and understated brows; front is +Z.
 for side,sgn in [('L',-1),('R',1)]:
  x=sgn*.047*w
  b.ellipsoid(side+' sclera',(x,1.514*s,.108),(.026,.016,.009),'#f3e7d4',12,8)
  b.ellipsoid(side+' iris',(x,1.514*s,.117),(.009,.011,.004),p['eyes'],12,8,.05,.35)
  b.ellipsoid(side+' pupil',(x,1.514*s,.121),(.004,.008,.002),'#211b18',10,7)
  b.ellipsoid(side+' eye glint',(x-.003,1.519*s,.123),(.0025,.0025,.001),'#ffffff',8,6)
  b.tapered(side+' brow',(x-sgn*.023,1.545*s,.111),(x+sgn*.018,1.55*s,.11),.007,.006,p['hair'])
 b.ellipsoid('Nose',(0,1.482*s,.115),(.016,.030,.020),p['skin'],12,8)
 b.tapered('Mouth',(-.027,1.439*s,.105),(.027,1.439*s,.105),.0035,.0035,'#805b50')
 # Texture-free small accessories: stitching, straps and restrained metal trim.
 b.tapered('Crossbody strap',(-.15*w,1.34*s,.104),(.14*w,.84*s,.113),.014,.015,p['boots'])
 b.ellipsoid('Satchel',(.205*w,.82*s,.015),(.105,.115,.045),p['boots'])
 b.ellipsoid('Satchel flap',(.205*w,.866*s,.054),(.095,.040,.016),p['trim'],14,8)
 b.ellipsoid('Satchel catch',(.205*w,.846*s,.073),(.013,.013,.005),p['accent'],10,8,.55,.4)
 if name=='Ender':
  # Brass forehead goggles with translucent-looking green lenses; staff is full height.
  for sgn in (-1,1):
   b.ellipsoid('Goggle rim '+str(sgn),(sgn*.057,1.63*s,.104),(.041,.032,.015),p['trim'],16,8,.85,.24)
   b.ellipsoid('Goggle glass '+str(sgn),(sgn*.057,1.63*s,.116),(.030,.023,.006),p['accent'],16,8,.25,.18)
  b.tapered('Goggle bridge',(-.015,1.63*s,.12),(.015,1.63*s,.12),.007,.007,p['trim'],.8,.3)
  b.tapered('Full staff',(-.35,0,.08),(-.35,1.84,.08),.019,.019,'#624730')
  b.tapered('Center hand wrap',(-.35,.83,.08),(-.35,1.01,.08),.027,.027,'#c0a47b')
  for y in (.01,1.83): b.ellipsoid('Brass staff ferrule '+str(y),(-.35,y,.08),(.026,.018,.026),p['trim'],12,8,.88,.28)
 elif name=='Ionia':
  for side in (-1,1):
   for k in range(9):
    t=k/8; x=side*(.104+.026*math.sin(k*2.2));y=(1.62-.57*t)*s;z=.005-.035*t
    b.ellipsoid('Captain curl %s %s'%(side,k),(x,y,z),(.030,.039,.03),p['hair'],10,7)
  b.tapered('Captain jacket gold seam L',(-.105,1.35*s,.09),(-.055,.96*s,.10),.006,.006,p['trim'],.6,.35)
  b.tapered('Captain jacket gold seam R',(.105,1.35*s,.09),(.055,.96*s,.10),.006,.006,p['trim'],.6,.35)
  for y in (1.18,1.08,.98):b.ellipsoid('Jacket button '+str(y),(.082,y*s,.107),(.009,.009,.005),p['trim'],10,6,.8,.3)
 elif name=='Lyra':
  for side in (-1,1):
   for k in range(12):
    t=k/11; a=k*2.5+side
    b.ellipsoid('Lyra wave %s %s'%(side,k),(side*(.11+.018*math.sin(a)),(1.61-.58*t)*s,-.015-.02*t),(.031,.037,.034),p['hair'],10,7)
  b.ellipsoid('Blue robe skirt',(0,.85*s,0),(.226,.25*s,.14),p['coat'],20,12)
  b.tapered('Embroidered robe center',(0,1.26*s,.112),(0,.66*s,.133),.005,.005,p['trim'],.3,.7)
 elif name=='Reson':
  b.ellipsoid('Red scarf',(0,1.365*s,.012),(.152,.052,.107),p['accent'],18,9)
  b.tapered('Utility bandolier',(-.185,1.34*s,.105),(.17,.90*s,.125),.034,.033,p['boots'])
  b.ellipsoid('Pike handle holster',(-.208,.91*s,-.05),(.025,.19,.025),p['trim'],12,8,.5,.5)
 elif name=='Aepex':
  b.ellipsoid('High undercut top',(.015,1.68*s,-.015),(.115,.055,.10),p['hair'],16,10)
  for k in range(5):
   b.tapered('Arm tattoo '+str(k),(-.257,1.015*s-k*.027,.057),(-.206,1.025*s-k*.027,.065),.003,.003,p['accent'])
  b.ellipsoid('Tool pouch',(-.18,.83*s,.04),(.075,.085,.044),p['trim'])
  b.ellipsoid('Diagnostic lens',(-.19,.875*s,.082),(.021,.021,.007),p['accent'],12,8,.4,.3)
 return b

if __name__=='__main__':
 manifest={'status':'UNRIGGED_LOOKDEV_CANDIDATE','reference':'approved cast sheet Oct 30, 2026; repo character locks','characters':[]}
 for name in ('Ender','Ionia','Lyra','Reson','Aepex'):
  b=make(name);manifest['characters'].append({'name':name,'height_m':PALETTES[name]['height'],**b.save(OUT/(name+'.glb'))})
 (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 print(json.dumps(manifest,indent=2))

