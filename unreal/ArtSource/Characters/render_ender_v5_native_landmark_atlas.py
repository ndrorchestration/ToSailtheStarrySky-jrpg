"""Render native 79-index MetaHuman landmark technical atlas and unmapped CSV.

NOT a native Unreal screenshot. This is an orthographic projection of the
read-only MetaHuman API coordinate receipt, using Pillow locally. No face
sculpting, skin authoring, 2D reference matching or creator approval.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from verify_ender_v5_native_landmark_atlas import check_payload

def build(data_file, destination):
    from PIL import Image, ImageDraw, ImageFont
    destination=Path(destination)
    if destination.exists():
        raise FileExistsError("Refuse overwrite of native technical atlas")
    data_file=Path(data_file)
    src=json.loads(data_file.read_text(encoding="utf-8"))
    proof=check_payload(src)
    destination.mkdir(parents=True,exist_ok=False)
    points=src["points"]
    rows=[]
    for p in points:
        xyz=p["xyz_cm"]
        rows.append({"native_index":p["index"],
                     "x_cm":xyz[0],"y_cm":xyz[1],"z_cm":xyz[2],
                     "human_reviewed_semantic_name":"",
                     "approved_reference_filename":"",
                     "image_pixel_x":"","image_pixel_y":"",
                     "status":"UNMAPPED_REQUIRES_HUMAN_REVIEW"})
    csv_path=destination/"v5_landmark_index_unmapped.csv"
    with csv_path.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys())
        w.writeheader();w.writerows(rows)

    W,H=2560,1450
    im=Image.new("RGB",(W,H),(247,247,247))
    draw=ImageDraw.Draw(im)
    try:
        heading=ImageFont.truetype(r"C:\Windows\Fonts\segoeuib.ttf",35)
        label=ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf",17)
        small=ImageFont.truetype(r"C:\Windows\Fonts\segoeui.ttf",20)
        tiny=ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf",15)
    except OSError:
        heading=label=small=tiny=ImageFont.load_default()
    draw.text((75,27),"Ender V5 | MetaHuman native landmark index atlas",font=heading,fill=(29,43,50))
    draw.text((75,93),"79 verified API indices • model-space centimetres • no semantic names / NO Ender likeness approval",
              font=small,fill=(82,82,82))
    draw.text((75,124),"Technical coordinate projections, NOT Unreal screenshots or registered 2D art overlays",
              font=small,fill=(82,82,82))

    def panel(left,top,title,haxis):
        right=left+1192
        bottom=top+1175
        draw.rectangle((left,top,right,bottom),outline=(160,169,174),width=2,fill=(255,255,255))
        draw.text((left+30,top+19),title,font=heading,fill=(31,47,54))
        draw.text((left+30,top+66),f"horizontal {haxis.upper()} cm    vertical Z cm",font=small,fill=(70,70,70))
        x0,x1=left+110,right-92
        y0,y1=top+136,bottom-140
        vals=[p["xyz_cm"] for p in points]
        hi={"x":0,"y":1}[haxis]
        lo=min(p[hi] for p in vals);upper=max(p[hi] for p in vals)
        vlo=min(p[2] for p in vals);vhi=max(p[2] for p in vals)
        hpad=max(.9,(upper-lo)*.07);zpad=max(1.,(vhi-vlo)*.08)
        lo-=hpad;upper+=hpad;vlo-=zpad;vhi+=zpad
        def pos(p):
            return (x0+(p[hi]-lo)/(upper-lo)*(x1-x0),
                    y1-(p[2]-vlo)/(vhi-vlo)*(y1-y0))
        draw.rectangle((x0,y0,x1,y1),outline=(96,108,115),width=2)
        for n in range(6):
            yy=y0+n/5*(y1-y0)
            xx=x0+n/5*(x1-x0)
            draw.line((x0,yy,x1,yy),fill=(230,233,235))
            draw.line((xx,y0,xx,y1),fill=(230,233,235))
            draw.text((x0-85,yy-9),f"{vhi-(vhi-vlo)*n/5:5.1f}",font=tiny,fill=(80,80,80))
            draw.text((xx-23,y1+10),f"{lo+(upper-lo)*n/5:.1f}",font=tiny,fill=(80,80,80))
        occupied=[]
        for p in points:
            px,py=pos(p["xyz_cm"])
            draw.ellipse((px-5,py-5,px+5,py+5),fill=(30,88,111),outline=(15,43,51),width=1)
        candidates=[(dx,dy) for r in (18,30,47,65,84,103)
                             for dx,dy in ((r,-r/3),(-r,-r/3),(r,r/2),(-r,r/2),
                                           (0,-r),(0,r),(r,0),(-r,0))]
        for p in points:
            px,py=pos(p["xyz_cm"])
            st=f"{p['index']:02d}"
            bw=draw.textbbox((0,0),st,font=label)
            wd,ht=bw[2]-bw[0]+8,bw[3]-bw[1]+7
            best=None
            for dx,dy in candidates:
                bx=px+dx
                by=py+dy
                region=(bx,by,bx+wd,by+ht)
                if bx<x0+2 or by<y0+2 or bx+wd>x1-2 or by+ht>y1-2:
                    continue
                overlaps=sum(not(reg[2]+2<region[0] or reg[0]-2>region[2] or
                                 reg[3]+2<region[1] or reg[1]-2>region[3]) for reg in occupied)
                score=(overlaps*1000+abs(dx)+abs(dy),region)
                if best is None or score[0]<best[0]:
                    best=score
                if overlaps==0:break
            if best is None:
                raise ValueError("Could not fit point label")
            bx,by,bx2,by2=best[1]
            draw.line((px,py,(bx+bx2)/2,(by+by2)/2),fill=(162,164,161),width=1)
            draw.rectangle((bx,by,bx2,by2),fill=(251,247,229),outline=(220,207,159),width=1)
            draw.text((bx+4,by+1),st,font=label,fill=(34,43,53))
            occupied.append(best[1])
        draw.text((left+40,bottom-96),
                  f"Native indices 00–78  |  {haxis.upper()}: {lo:.2f}–{upper:.2f} cm  |  Z: {vlo:.2f}–{vhi:.2f} cm",
                  font=small,fill=(54,54,54))
        draw.text((left+40,bottom-60),"Labels show index only: anatomical feature names are UNMAPPED.",
                  font=small,fill=(100,51,47))
    panel(55,190,"FRONT coordinate projection","x")
    panel(1313,190,"PROFILE coordinate projection","y")
    draw.text((68,1390),"Unapproved default MetaHuman base • no official content downloads • no artist facial reference registration",
              font=small,fill=(95,56,54))
    png=destination/"v5_native_79_index_atlas.png"
    im.save(png,optimize=False)
    manifest={
        "status":"TECHNICAL_79_INDEX_ATLAS_RENDERED_NOT_REFERENCE_ALIGNED",
        "point_count":79,
        "native_data_sha256":hashlib.sha256(data_file.read_bytes()).hexdigest(),
        "csv_sha256":hashlib.sha256(csv_path.read_bytes()).hexdigest(),
        "png_sha256":hashlib.sha256(png.read_bytes()).hexdigest(),
        "image_size":list(im.size),
        "front_axes":"x,z",
        "profile_axes":"y,z",
        "artist_reference_image_included":False,
        "facial_semantic_index_mapping_approved":False,
        "owner_likeness_approved":False,
        "real_unreal_render":False,
        "engine_native_landmarks":proof["points"],
    }
    (destination/"atlas_manifest.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(manifest,indent=2))
    return manifest

if __name__=="__main__":
    args=argparse.ArgumentParser()
    args.add_argument("native_receipt",type=Path)
    args.add_argument("output_directory",type=Path)
    p=args.parse_args()
    build(p.native_receipt,p.output_directory)
