#!/usr/bin/env python3
"""Generate deterministic 1024px UV-space dragonfly vein mask. Requires Pillow."""
from pathlib import Path
from PIL import Image, ImageDraw
import math

def generate(size=1024, output=Path("AureateWake_VenationMask_RGBA.png")):
    if size < 128: raise ValueError("size must be at least 128")
    im = Image.new("RGBA", (size,size), (0,0,0,0))
    draw = ImageDraw.Draw(im)
    def xy(u,v): return (round(u*(size-1)),round((1-v)*(size-1)))
    def half(t): return max(.025,math.sin(math.pi*t)**.8)*(.78+.22*t)*.48
    paths=[[(t/160,.5) for t in range(161)]]
    for side in (-1,1):
        paths.append([(t/160,.5+side*half(t/160)) for t in range(161)])
        for i in range(2,30):
            u=i/32
            end=min(.97,u+.11)
            paths.append([(u+(end-u)*q/8,.5+side*half(u+(end-u)*q/8)*q/8) for q in range(9)])
            if i<25:
                paths.append([(u+(end-u)*q/8,.5+side*half(u+(end-u)*q/8)*(1-q/8)) for q in range(9)])
    for index,path in enumerate(paths):
        draw.line([xy(u,v) for u,v in path],fill=(235,245,255,230 if index<3 else 160),
                  width=4 if index<3 else 2,joint="curve")
    output.parent.mkdir(parents=True,exist_ok=True)
    im.save(output)
    return len(paths)

if __name__=="__main__":
    output=Path("AureateWake_VenationMask_RGBA.png")
    print(f"Generated {generate(output=output)} paths into {output}")
