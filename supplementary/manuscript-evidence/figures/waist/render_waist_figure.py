"""Render saved model surfaces and stored contours; no new scientific measurements."""
from pathlib import Path
import argparse, hashlib, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from mesh_io import read_glb

HERE=Path(__file__).resolve().parent
S=3.7
BLUE="#0072B2"; ORANGE="#C45A00"; BAND="#DDE7EE"; TEXT="#172B3A"; GRAY="#627583"
XMIN,XMAX,YMIN,YMAX=-.30,.30,-.25,.37
def font(size,bold=False):
    return ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",round(size*S))
def xy(p): return tuple(round(x*S) for x in p)
def line(d,points,fill=TEXT,width=1): d.line([xy(p) for p in points],fill=fill,width=max(1,round(width*S)))
def text(d,p,s,size=21,fill=TEXT,anchor="la",bold=False):
    d.text(xy(p),s,font=font(size,bold),fill=fill,anchor=anchor)
def dashed(d,x0,x1,y,color=GRAY,width=.8):
    for x in np.arange(x0,x1,8):line(d,[(x,y),(min(x+4,x1),y)],color,width)
def dot(d,x,y,color,radius=3.3):
    d.ellipse((*xy((x-radius,y-radius)),*xy((x+radius,y+radius))),fill=color,outline="white",width=round(.7*S))

def render_mesh(vertices,faces,anchor,side):
    size=1200; yaw=np.pi/2 if side else 0
    rotation=np.array([[np.cos(yaw),0,np.sin(yaw)],[0,1,0],[-np.sin(yaw),0,np.cos(yaw)]])
    v=vertices.astype(float)@rotation.T;v[:,1]-=anchor
    tri=v[faces]
    mask=((tri[:,:,1].max(1)>=YMIN)&(tri[:,:,1].min(1)<=YMAX)&(tri[:,:,0].max(1)>=XMIN)&(tri[:,:,0].min(1)<=XMAX))
    indices=np.flatnonzero(mask)
    normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
    normal/=np.maximum(np.linalg.norm(normal,axis=1,keepdims=True),1e-30)
    light=np.array([-.30,.45,1.]);light/=np.linalg.norm(light)
    b=np.clip(.36+.57*np.abs(normal@light),0,1)
    colors=np.stack([b*.83,b*.88,b*.91],axis=1)*255
    proj=np.column_stack([(v[:,0]-XMIN)*(size-1)/(XMAX-XMIN),(YMAX-v[:,1])*(size-1)/(YMAX-YMIN)])
    im=Image.new("RGB",(size,size),"white");d=ImageDraw.Draw(im)
    for i in indices[np.argsort(tri[indices,:,2].mean(1))]:
        d.polygon([tuple(p) for p in proj[faces[i]]],fill=tuple(colors[i].astype(int)))
    return im

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--repo",type=Path);args=ap.parse_args()
    root=args.repo or next(p for p in HERE.parents if (p/"publication/somatoanthropy-huggingface-companion").is_dir())
    doc=json.loads((HERE/"waist_illustration_data.json").read_text(encoding="utf-8"))
    im=Image.new("RGB",xy((1000,860)),"white");d=ImageDraw.Draw(im)
    for row,rec in enumerate(doc["records"]):
        path=root/rec["mesh_relative_path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest()==rec["mesh_sha256"]
        verts,faces,_=read_glb(path)
        anchor=rec["anchor_world_y_m"]; top=rec["search_interval_world_y_m"][1]-anchor
        sel=rec["selected_plane_world_y_m"]-anchor
        color=ORANGE if rec["fallback_applied"] else BLUE
        offset=370*row
        text(d,(25,18+offset),["(a) Adaptive selection","(b) Offset fallback"][row],26,bold=True)
        for col in range(2):
            left=20+col*230; ypos=91+offset;w=225;h=w*(YMAX-YMIN)/(XMAX-XMIN)
            render=render_mesh(verts,faces,anchor,col==1)
            im.paste(render.resize(xy((w,h)),Image.Resampling.LANCZOS),xy((left,ypos)))
            def py(y):return ypos+(YMAX-y)/(YMAX-YMIN)*h
            overlay=Image.new("RGBA",im.size,(0,0,0,0));od=ImageDraw.Draw(overlay)
            od.rectangle((*xy((left,py(top))),*xy((left+w,py(0)))),fill=(182,205,220,65))
            im=Image.alpha_composite(im.convert("RGBA"),overlay).convert("RGB");d=ImageDraw.Draw(im)
            dashed(d,left,left+w,py(0))
            points=np.array(rec["contour_points_m"])
            xx=points[:,2] if col else points[:,0]
            plotpts=[(left+(x-XMIN)/(XMAX-XMIN)*w,py(y-anchor)) for x,y in zip(xx,points[:,1])]
            line(d,plotpts+[plotpts[0]],color,2.7)
            text(d,(left+w/2,63+offset),["Front","Profile"][col],22,anchor="ma")
            if col==0:
                sx=left+19;sb=py(-.22);st=py(-.12)
                line(d,[(sx,st),(sx,sb)],TEXT,1.5)
                line(d,[(sx-4,st),(sx+4,st)],TEXT,1)
                line(d,[(sx-4,sb),(sx+4,sb)],TEXT,1)
                text(d,(sx+12,(st+sb)/2),"10 cm",21,anchor="lm")
        x0,x1,y0,y1=655,970,92+offset,332+offset
        fx=lambda x:x0+(x-91)/19*(x1-x0)
        fy=lambda y:y1-(y+.4)/14.4*(y1-y0)
        d.rectangle((*xy((x0,fy(top*100))),*xy((x1,fy(0)))),fill=BAND)
        for yy in [0,4,8,12]:
            line(d,[(x0,fy(yy)),(x1,fy(yy))],"white",1)
            line(d,[(x0-5,fy(yy)),(x0,fy(yy))],GRAY,.9)
            text(d,(x0-12,fy(yy)),str(yy),21,anchor="rm")
        for xx in [95,100,105,110]:
            line(d,[(fx(xx),y1),(fx(xx),y1+5)],GRAY,.9)
            text(d,(fx(xx),y1+10),str(xx),21,anchor="ma")
        line(d,[(x0,y0),(x0,y1),(x1,y1)],GRAY,1)
        profile=[p for p in rec["profile"] if p["world_y_m"]<=rec["search_interval_world_y_m"][1]+1e-10]
        cx=np.array([p["raw_contour_cm"] for p in profile]);hy=(np.array([p["world_y_m"] for p in profile])-anchor)*100
        curve=[(fx(x),fy(y)) for x,y in zip(cx,hy)]
        line(d,curve,"#4F606B",1.9)
        for x,y in curve:dot(d,x,y,"#4F606B",2.3)
        sx,sy=fx(rec["selected_raw_contour_cm"]),fy(sel*100)
        dot(d,sx,sy,color,5.2)
        if rec["fallback_applied"]:
            rx,ry=curve[-1]
            line(d,[(rx-5,ry-5),(rx+5,ry+5)],ORANGE,1.7);line(d,[(rx-5,ry+5),(rx+5,ry-5)],ORANGE,1.7)
            text(d,(806,fy(13.0)),"Rejected boundary",21,anchor="mm")
            line(d,[(713,fy(12.75)),(rx+7,ry-2)],GRAY,.9)
            text(d,(861,fy(5.1)),"Offset: +0.5 cm",21,anchor="mm")
            line(d,[(843,fy(4.2)),(sx,sy-8)],GRAY,.9)
        else:
            text(d,(793,fy(9.5)),"Selected extremum",21,anchor="mm")
            line(d,[(847,fy(8.7)),(sx-3,sy-8)],GRAY,.9)
        text(d,((x0+x1)/2,63+offset),"Saved search profile",22,anchor="ma")
        text(d,((x0+x1)/2,y1+39),"Contour length (cm)",21,anchor="ma")
        lab=Image.new("RGBA",xy((290,55)),(0,0,0,0));ld=ImageDraw.Draw(lab)
        text(ld,(145,0),"Height above anchor",21,anchor="ma")
        text(ld,(145,23),"(cm)",21,anchor="ma")
        lab=lab.rotate(90,expand=True,resample=Image.Resampling.BICUBIC)
        im.paste(lab,xy((548,(y0+y1)/2-145)),lab);d=ImageDraw.Draw(im)
    # Two rows keep all labels legible at a 13.86 cm manuscript width.
    y=799
    d.rectangle((*xy((92,y-7)),*xy((122,y+7))),fill=BAND)
    text(d,(138,y),"Search interval",21,anchor="lm")
    dashed(d,548,581,y);text(d,(598,y),"Umbilicus anchor",21,anchor="lm")
    y=836
    line(d,[(92,y),(125,y)],BLUE,2.7);text(d,(138,y),"Adaptive contour",21,anchor="lm")
    line(d,[(548,y),(581,y)],ORANGE,2.7);text(d,(598,y),"Fallback contour",21,anchor="lm")
    path=HERE/"Waist_selection_and_fallback.png";im.save(path,dpi=(500,500))
    prov={"asset":path.name,"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"pixels":list(im.size),"dpi":500,
          "rendering":"Orthographic front and profile torso crops. Common engineering-coordinate scale and anchor-relative vertical window; no per-body scale or shape normalization.",
          "inputs":[{k:r[k] for k in ("sample_id","mesh_relative_path","mesh_sha256","measurement_details_sha256","selector_version","fallback_applied","quality_state","reason","frame_check_max_saved_point_to_selected_mesh_edge_m","frame_check_max_plane_residual_m")} for r in doc["records"]],
          "saved_data_sha256":hashlib.sha256((HERE/"waist_illustration_data.json").read_bytes()).hexdigest(),
          "meaning":"Illustrations from measurement-conditioned generated model surfaces outside evaluation cohorts. Saved contours and search profiles; no participant scans, new fitting, native forwards or measurement reruns.",
          "privacy":"No source conditioning values, respondent identifiers, private locations or participant linkage included.",
          "interpretation":"PROXY_VALID is a saved selector quality state, not anatomical or clinical validation. The fallback retains the saved SITE_AMBIGUOUS label.",
          "caption":"Waist selection on two saved measurement-conditioned MHR model surfaces outside the evaluation cohorts. Front and profile torso views share an engineering-coordinate display scale. The shaded band is the retained lower-half umbilicus-to-chest search interval; the dashed line marks the umbilicus anchor. Colored lines project the stored selected three-dimensional sections. Saved circumference profiles show (a) an interior extremum retained by the adaptive selector and (b) a boundary extremum marked ambiguous, with the explicit 0.5 cm offset section used instead. These are method illustrations, not participant scans or evidence of anatomical accuracy."}
    (HERE/"waist_figure_provenance.json").write_text(json.dumps(prov,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"figure":path.name,"pixels":list(im.size),"dpi":500,"sha256":prov["sha256"]}))
if __name__=="__main__":main()
