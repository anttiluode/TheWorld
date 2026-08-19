from __future__ import annotations

"""CC0-A3D: turn >=2-scale certificate blobs into tiny persistent local states.

Front ends remain dense. This tests only whether a connected certificate can be
represented as SUPPORTED / REUSE / HOLD / WAKE local tracks. A plain tile mask
gets the same tracker as an attacker. Held state is explicitly not evidence.
"""

import argparse, csv, json, math, platform, time, tkinter as tk
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tkinter import messagebox
from typing import Dict, List, Optional, Tuple
import cv2, numpy as np
import cc0a3c_scale_certificate_gui as a3c

base = a3c.base
HOLD_FRAMES, MATCH_DISTANCE = 4, 2.0
MOVE_WAKE, AREA_WAKE, SCORE_WAKE = .75, .50, .75

@dataclass
class Blob:
    mask: np.ndarray
    xy: Tuple[float,float]
    area: int
    score: float

@dataclass
class Track:
    tid: int
    mask: np.ndarray
    xy: Tuple[float,float]
    area: int
    score: float
    age: int = 1
    missed: int = 0
    event: str = "NEW"

@dataclass
class TrackFrame:
    belief: np.ndarray
    supported: np.ndarray
    held: np.ndarray
    active: int
    supported_n: int
    held_n: int
    wake: int
    reuse: int
    hold: int
    expire: int


def blobs(mask: np.ndarray, score: Optional[np.ndarray]=None) -> List[Blob]:
    n, lab = cv2.connectedComponents(mask.astype(np.uint8), connectivity=8)
    out=[]
    for k in range(1,n):
        m=lab==k; ys,xs=np.where(m)
        if not xs.size: continue
        sc=float(np.asarray(score)[m].mean()) if score is not None else 1.0
        out.append(Blob(m,(float(xs.mean()),float(ys.mean())),int(m.sum()),sc))
    return out


def dist(a,b): return float(math.hypot(a[0]-b[0],a[1]-b[1]))


class Tracker:
    def __init__(self,name): self.name=name; self.reset()
    def reset(self):
        self.tracks: Dict[int,Track]={}; self.next_id=1; self.created=0; self.expired=0
        self.reacquired=0; self.wake_total=0; self.decision_total=0; self.ages=[]; self.log=[]
    def update(self, mask, score, frame) -> TrackFrame:
        bs=blobs(mask,score); old=list(self.tracks); cand=[]
        for tid in old:
            t=self.tracks[tid]
            for bi,b in enumerate(bs):
                d=dist(t.xy,b.xy)
                if d <= MATCH_DISTANCE+.35*t.missed: cand.append((d,tid,bi))
        cand.sort(); mt=set(); mb=set(); pairs=[]
        for d,tid,bi in cand:
            if tid not in mt and bi not in mb: mt.add(tid); mb.add(bi); pairs.append((tid,bi,d))
        wake=reuse=hold=expire=0
        for tid,bi,d in pairs:
            t,b=self.tracks[tid],bs[bi]; was=t.missed
            sig=was>0 or d>=MOVE_WAKE or abs(b.area-t.area)/max(1,t.area)>=AREA_WAKE or abs(b.score-t.score)>=SCORE_WAKE
            ev="REACQUIRE" if was else ("UPDATE" if sig else "REUSE")
            if ev=="REUSE": reuse+=1
            else: wake+=1; self.reacquired += int(ev=="REACQUIRE")
            t.mask=b.mask.copy(); t.xy=b.xy; t.area=b.area; t.score=b.score; t.age+=1; t.missed=0; t.event=ev
            self.log.append((frame,self.name,tid,ev,*t.xy,t.area,t.score,t.age))
        dead=[]
        for tid in old:
            if tid in mt: continue
            t=self.tracks[tid]; t.age+=1; t.missed+=1
            if t.missed<=HOLD_FRAMES:
                t.event="HOLD"; hold+=1; self.log.append((frame,self.name,tid,"HOLD",*t.xy,t.area,t.score,t.age))
            else:
                expire+=1; wake+=1; self.expired+=1; self.ages.append(t.age); dead.append(tid)
                self.log.append((frame,self.name,tid,"EXPIRE",*t.xy,t.area,t.score,t.age))
        for tid in dead: del self.tracks[tid]
        for bi,b in enumerate(bs):
            if bi in mb: continue
            tid=self.next_id; self.next_id+=1; self.created+=1; wake+=1
            self.tracks[tid]=Track(tid,b.mask.copy(),b.xy,b.area,b.score)
            self.log.append((frame,self.name,tid,"NEW",*b.xy,b.area,b.score,1))
        belief=np.zeros_like(mask,bool); sup=np.zeros_like(mask,bool); held=np.zeros_like(mask,bool); sn=hn=0
        for t in self.tracks.values():
            belief|=t.mask
            if t.missed: held|=t.mask; hn+=1
            else: sup|=t.mask; sn+=1
        decisions=len(self.tracks)+expire; self.wake_total+=wake; self.decision_total+=decisions
        return TrackFrame(belief,sup,held,len(self.tracks),sn,hn,wake,reuse,hold,expire)
    def summary(self):
        ages=self.ages+[t.age for t in self.tracks.values()]
        return {"active_tracks":len(self.tracks),"created":self.created,"expired":self.expired,
                "reacquired":self.reacquired,"receiver_wake_fraction":self.wake_total/self.decision_total if self.decision_total else 0.,
                "receiver_wakes":self.wake_total,"receiver_decisions":self.decision_total,
                "mean_track_age":float(np.mean(ages)) if ages else 0.,"max_track_age":max(ages) if ages else 0}


class TrackerCensus(a3c.CertificateCensus):
    def __post_init__(self):
        super().__post_init__(); self.cert_tracker=Tracker("certificate"); self.tile_tracker=Tracker("tile")
        self.cert_belief_trace=[]; self.cert_held_trace=[]; self.tile_belief_trace=[]
    def reset(self):
        super().reset(); self.cert_tracker.reset(); self.tile_tracker.reset(); self.cert_belief_trace.clear(); self.cert_held_trace.clear(); self.tile_belief_trace.clear()
    def process(self, frame_bgr):
        m,v=super().process(frame_bgr); i=len(self.rows)-1; mult=v["multiplicity"]
        cert=mult>=2; tile=v["tile_wake"].any(axis=0)
        ct=self.cert_tracker.update(cert,mult,i); tt=self.tile_tracker.update(tile,None,i)
        r=self.rows[-1]
        r.update(cert_current_fanout=float(cert.mean()), cert_belief_fanout=float(ct.belief.mean()),
                 cert_held_only_fanout=float((ct.held & ~cert).mean()), cert_tracks=ct.active, cert_held_tracks=ct.held_n,
                 cert_wake_events=ct.wake, cert_reuse_events=ct.reuse, cert_hold_events=ct.hold,
                 tile_belief_fanout=float(tt.belief.mean()), tile_held_only_fanout=float((tt.held & ~tile).mean()),
                 tile_tracks=tt.active, tile_held_tracks=tt.held_n, tile_wake_events=tt.wake)
        self.cert_belief_trace.append(ct.belief.copy()); self.cert_held_trace.append(ct.held.copy()); self.tile_belief_trace.append(tt.belief.copy())
        v.update(tracker_certificate=cert,cert_tracker_frame=ct,tile_tracker_frame=tt); return m,v
    def summary(self):
        s=super().summary(); ss=self.rows[1:] if len(self.rows)>1 else self.rows
        mean=lambda k: float(np.mean([r.get(k,0.) for r in ss])) if ss else 0.
        s.update(a3d_hold_frames=HOLD_FRAMES,a3d_match_distance=MATCH_DISTANCE,
                 certificate_current_fanout=mean("cert_current_fanout"),certificate_belief_fanout=mean("cert_belief_fanout"),
                 certificate_held_only_fanout=mean("cert_held_only_fanout"),certificate_mean_tracks=mean("cert_tracks"),
                 certificate_mean_held_tracks=mean("cert_held_tracks"),tile_tracker_belief_fanout=mean("tile_belief_fanout"),
                 tile_tracker_held_only_fanout=mean("tile_held_only_fanout"),certificate_tracker=self.cert_tracker.summary(),
                 tile_tracker=self.tile_tracker.summary(),warning="Dense Gabor/tile front ends still run every frame. A3D measures persistent-track event sparsity, not runtime speedup.")
        return s

base.LocalFieldCensus=TrackerCensus


def tracker_image(tf:TrackFrame, tracks:Dict[int,Track], size=(400,280)):
    rows,cols=tf.belief.shape; a=np.zeros((rows,cols,3),np.uint8); a[tf.held]=(80,80,80); a[tf.supported]=(235,235,235)
    im=cv2.resize(a,size,interpolation=cv2.INTER_NEAREST); sx,sy=size[0]/cols,size[1]/rows
    for t in tracks.values():
        x=int((t.xy[0]+.5)*sx); y=int((t.xy[1]+.5)*sy); label=f"{t.tid}{'H' if t.missed else ''}"
        cv2.putText(im,label,(max(2,x-8),max(14,y)),cv2.FONT_HERSHEY_SIMPLEX,.43,(0,0,255),1,cv2.LINE_AA)
    return im


class A3DGUI(a3c.A3CGUI):
    def __init__(self,root,args):
        super().__init__(root,args); self.root.title("CC0-A3D Certificate Tracker — SUPPORTED / REUSE / HOLD / WAKE")
        self.panels["scale"].master.configure(text="Persistent certificate tracks: bright=supported, dim=HOLD")
        self.panels["info"].master.configure(text="Receiver event stream / tile tracker attacker")
    def _update_metrics(self,m):
        super()._update_metrics(m); s=self.census.summary(); cs=s["certificate_tracker"]; ts=s["tile_tracker"]
        self.metric_vars["fanout"].set(f"cert {s['certificate_current_fanout']:.3f} belief {s['certificate_belief_fanout']:.3f} tile {s.get('tile_spatial_routing_fanout',0):.3f}")
        self.metric_vars["scale"].set(f"receiver WAKE cert {cs['receiver_wake_fraction']:.3f} tile {ts['receiver_wake_fraction']:.3f}")
        self.metric_vars["bundle"].set(f"tracks cert {cs['active_tracks']} tile {ts['active_tracks']} held avg {s['certificate_mean_held_tracks']:.2f}")
    def _update_panels(self,frame,m,v):
        super()._update_panels(frame,m,v); ct=v["cert_tracker_frame"]; tt=v["tile_tracker_frame"]
        im=tracker_image(ct,self.census.cert_tracker.tracks); cv2.putText(im,"bright=SUPPORTED  dim=HOLD  red=id",(8,20),cv2.FONT_HERSHEY_SIMPLEX,.42,(255,255,255),1,cv2.LINE_AA); self._set_panel("scale",im)
        s=self.census.summary(); cs=s["certificate_tracker"]; ts=s["tile_tracker"]; info=np.zeros((280,400,3),np.uint8)
        lines=["A3D LOCAL STATE: SUPPORTED / REUSE / HOLD / WAKE",f"hold window {HOLD_FRAMES}f",f"cert tracks {ct.active} supported {ct.supported_n} held {ct.held_n}",
               f"now WAKE {ct.wake} REUSE {ct.reuse} HOLD {ct.hold}",f"session cert WAKE fraction {cs['receiver_wake_fraction']:.3f}",
               f"cert current/belief fanout {float(v['tracker_certificate'].mean()):.3f}/{float(ct.belief.mean()):.3f}",f"held-only fanout {float((ct.held & ~v['tracker_certificate']).mean()):.3f}","",
               "TILE TRACKER ATTACKER",f"tracks {tt.active} held {tt.held_n}",f"session tile WAKE fraction {ts['receiver_wake_fraction']:.3f}",f"tile belief fanout {float(tt.belief.mean()):.3f}","","Dense oracle front end. Tracker != speed."]
        y=18
        for line in lines: cv2.putText(info,line,(7,y),cv2.FONT_HERSHEY_SIMPLEX,.37,(235,235,235),1,cv2.LINE_AA); y+=17
        self._set_panel("info",info)
    def save_receipt(self):
        if not self.census or not self.census.rows: messagebox.showinfo("Nothing to save","Run first."); return
        out=Path(self.args.out_dir); out.mkdir(parents=True,exist_ok=True); sid=datetime.now().strftime("%Y%m%d_%H%M%S"); p=out/f"cc0a3d_certificate_tracker_{sid}"; s=self.census.summary()
        s.update(session_id=sid,source_kind=self.source_kind,source_name=self.source_name,elapsed_s=float(time.perf_counter()-self.started_at) if self.started_at else None,platform=platform.platform(),opencv_version=cv2.__version__)
        p.with_suffix(".json").write_text(json.dumps(s,indent=2)+"\n",encoding="utf-8")
        keys=[]
        for r in self.census.rows:
            for k in r:
                if k not in keys: keys.append(k)
        with p.with_suffix(".csv").open("w",newline="",encoding="utf-8") as f: w=csv.DictWriter(f,fieldnames=keys); w.writeheader(); w.writerows(self.census.rows)
        ep=p.with_name(p.name+"_track_events.csv"); ek=["frame","tracker","track_id","event","x","y","area","score","age"]
        with ep.open("w",newline="",encoding="utf-8") as f: w=csv.writer(f); w.writerow(ek); w.writerows(self.census.cert_tracker.log+self.census.tile_tracker.log)
        cs,ts=s["certificate_tracker"],s["tile_tracker"]
        txt=["CC0-A3D CERTIFICATE TRACKER","="*72,f"frames: {s['frames_used']}",f"raw change: {s['raw_change_rate']:.6f}",f"certificate current fanout: {s['certificate_current_fanout']:.6f}",f"certificate belief fanout: {s['certificate_belief_fanout']:.6f}",f"held-only fanout: {s['certificate_held_only_fanout']:.6f}",f"tile current fanout: {s.get('tile_spatial_routing_fanout',0):.6f}",f"tile belief fanout: {s['tile_tracker_belief_fanout']:.6f}","",f"certificate receiver WAKE frac: {cs['receiver_wake_fraction']:.6f}",f"tile receiver WAKE frac: {ts['receiver_wake_fraction']:.6f}",f"certificate mean track age: {cs['mean_track_age']:.3f}f",f"tile mean track age: {ts['mean_track_age']:.3f}f","","WARNING:",s['warning']]
        p.with_suffix(".txt").write_text("\n".join(txt)+"\n",encoding="utf-8")
        np.savez_compressed(p.with_name(p.name+"_trace.npz"),multiplicity=np.stack(self.census.multiplicity_trace),certificate_belief=np.stack(self.census.cert_belief_trace),certificate_held=np.stack(self.census.cert_held_trace),tile_belief=np.stack(self.census.tile_belief_trace),hold_frames=np.array([HOLD_FRAMES]))
        messagebox.showinfo("Receipt saved",f"Saved A3D receipt in:\n{out}")


def self_test():
    c=TrackerCensus(base.SpectralConfig(analysis_width=128)); rng=np.random.default_rng(8)
    for t in range(28):
        im=np.zeros((96,128,3),np.uint8); cv2.rectangle(im,(10,15),(115,82),(55,55,55),-1); x=8+(3*t)%100
        if not 13<=t<=15: cv2.rectangle(im,(x,32),(min(127,x+16),67),(220,220,220),-1)
        im=np.clip(im.astype(np.int16)+rng.normal(0,1.2,im.shape).astype(np.int16),0,255).astype(np.uint8); _,v=c.process(im); assert v["cert_tracker_frame"].belief.shape==(6,8)
    s=c.summary(); assert 0<=s["certificate_tracker"]["receiver_wake_fraction"]<=1; print("CC0-A3D self-test PASS"); print(json.dumps({"cert":s["certificate_tracker"],"tile":s["tile_tracker"]},indent=2))


def main():
    global HOLD_FRAMES,MATCH_DISTANCE
    ap=argparse.ArgumentParser(); ap.add_argument("--camera",type=int,default=0); ap.add_argument("--analysis-width",type=int,default=128); ap.add_argument("--tolerance",type=float,default=.35); ap.add_argument("--tile-tolerance",type=float,default=.08); ap.add_argument("--hold-frames",type=int,default=4); ap.add_argument("--match-distance",type=float,default=2.0); ap.add_argument("--out-dir",default="results/cc0a3d_certificate_tracker_runs"); ap.add_argument("--self-test",action="store_true"); args=ap.parse_args()
    HOLD_FRAMES=max(0,args.hold_frames); MATCH_DISTANCE=max(.25,args.match_distance)
    if args.self_test: self_test(); return
    root=tk.Tk(); A3DGUI(root,args); root.mainloop()
if __name__=="__main__": main()
