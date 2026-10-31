#!/usr/bin/env python3
"""Offline orthographic model review; images are not Unreal screenshots."""
from PIL import Image, ImageDraw, ImageFont
import json, struct, pathlib, math
ROOT=pathlib.Path(__file__).resolve().parent

def review(path):
 data=path.read_bytes();jslen=struct.unpack_from('<I',data,12)[0];doc=json.loads(data[20:20+jslen]);bin_off=20+jslen+8
 acc=doc['accessors'];views=doc['bufferViews']
 def get(i,fmt,n):
  a=acc[i];v=views[a['bufferView']];o=bin_off+v['byteOffset'];stride=struct.calcsize(fmt)*n
  return [struct.unpack_from('<'+fmt*n,data,o+j*stride) for j in range(a['count'])]
 tris=[]
 for mesh in doc['meshes']:
  for pr in mesh['primitives']:
   pos=get(pr['attributes']['POSITION'],'f',3);ids=[x[0] for x in get(pr['indices'],'H',1)]
   c=doc['materials'][pr['material']]['pbrMetallicRoughness']['baseColorFactor']
   for k in range(0,len(ids),3):
    p=[pos[ids[k+i]] for i in range(3)]
    ux,uy,uz=[p[1][i]-p[0][i] for i in range(3)]
    vx,vy,vz=[p[2][i]-p[0][i] for i in range(3)]
    nx,ny,nz=uy*vz-uz*vy,uz*vx-ux*vz,ux*vy-uy*vx
    norm=math.sqrt(nx*nx+ny*ny+nz*nz) or 1
    if nz < -0.15*norm: continue
    light=max(.42,min(1,.64+.25*nz/norm+.15*nx/norm+.06*ny/norm))
    color=tuple(int(max(0,min(1,c[i]*light))*255) for i in range(3))
    tris.append((sum(q[2] for q in p)/3,p,color))
 im=Image.new('RGB',(480,680),(230,224,209));draw=ImageDraw.Draw(im)
 draw.ellipse((70,626,410,649),fill=(194,185,164))
 scale=310
 for z,p,c in sorted(tris):
  pts=[(240+q[0]*scale,626-q[1]*scale) for q in p]
  draw.polygon(pts,fill=c)
 draw.rectangle((0,0,480,60),fill=(39,51,58))
 draw.text((20,16),path.stem.upper()+'  •  3D LOOKDEV',fill=(242,228,198))
 draw.text((15,656),'Offline mesh review • not an Unreal render',fill=(65,60,53))
 return im

if __name__=='__main__':
 images=[review(ROOT/'out'/(name+'.glb')) for name in ('Ender','Ionia','Lyra','Reson','Aepex')]
 for name,im in zip(('Ender','Ionia','Lyra','Reson','Aepex'),images):im.save(ROOT/'out'/(name+'_review.png'))
 group=Image.new('RGB',(480*5,680),(230,224,209))
 for i,im in enumerate(images):group.paste(im,(i*480,0))
 group.save(ROOT/'out/Cast_review.png')
 print('rendered',group.size)

