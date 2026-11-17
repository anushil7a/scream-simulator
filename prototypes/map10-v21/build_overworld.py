"""Build the local-only MAP-10 v2.1 full map and export the exact runtime geometry."""
import argparse
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

BASE=Path(__file__).resolve().parent
OUT=BASE.parents[1]/"build"/"map21"
PROJECT="overworld.project.json"
SERVER="OverworldPreview.server.luau"
ARTIFACT="Map10V21OverworldReview.rbxl"
BOSS_ARTIFACT="Map10V21BossPlacementReview.rbxl"
ACADEMY_ARTIFACT="Map10V21AcademyRouteReview.rbxl"
BOSS_SHARED=("BossCatalog","BossRules","BossPatterns","BossMotion","BossVisualData")
BOSS_CLIENT=("BossVisuals.client","BossAppearance","BossVisualController","BossPose")

def include_bosses(project, paths, academy=False):
    tree=project["tree"]
    source=BASE.parents[1]/"src"
    project["name"]=Path(ACADEMY_ARTIFACT if academy else BOSS_ARTIFACT).stem
    sss=tree["ServerScriptService"]
    def add(parent,key,filename,original):
        assert filename not in paths and original.is_file(), original
        parent[key]={"$path":filename}
        paths[filename]=original
    if academy:
        for name in ("AcademyRoutePreview","AcademyRouteRules"):
            filename=name+".luau"
            add(sss,name,filename,BASE/filename)
        add(sss,"Equipment","Equipment.luau",source/"ServerScriptService"/"Equipment.luau")
        add(sss,"TestFlight","TestFlight.luau",source/"ServerScriptService"/"TestFlight.luau")
    else:
        add(sss,"BossPlacementPreview","BossPlacementPreview.luau",BASE/"BossPlacementPreview.luau")
    add(sss,"BossService","BossService.luau",source/"ServerScriptService"/"BossService.luau")
    rep=tree["ReplicatedStorage"]={"$className":"ReplicatedStorage"}
    shared=rep["Shared"]={"$className":"Folder"}
    add(shared,"CompactLayout","CompactLayout.luau",BASE/"BossHomes.luau")
    for name in BOSS_SHARED+(("GearCatalog","VoiceCombat") if academy else ()):
        filename=name+".luau"
        add(shared,name,filename,source/"ReplicatedStorage"/"Shared"/filename)
    starter=tree["StarterPlayer"]["StarterPlayerScripts"]
    for name in BOSS_CLIENT:
        filename=name+".luau"
        add(starter,name.removesuffix(".client"),filename,source/"StarterPlayer"/"StarterPlayerScripts"/filename)
    if academy:
        filename="AcademyRoutePreview.client.luau"
        add(starter,"AcademyRoutePreview",filename,BASE/filename)
        name="NavigationGuide"
        filename=name+".luau"
        add(starter,name,filename,source/"StarterPlayer"/"StarterPlayerScripts"/filename)


def run(*args, capture=False):
    return subprocess.run(args,cwd=BASE,check=True,text=True,stdout=subprocess.PIPE if capture else None)

def export():
    data=json.loads((BASE/"layout.json").read_text())
    parts=[];routes=[]
    def vector(s):return list(map(float,s.split(",")))
    def tags(s):return s.split(",") if s else []
    for line in run("luau","export_overworld.luau",capture=True).stdout.splitlines():
        kind,*row=line.split("|")
        if kind=="P":
            ident,position,size,rotation,color,shape,material,collide,query,role,zone,labels=row
            parts.append(dict(id=f"{zone}/{ident}",position=vector(position),size=vector(size),
               rotation=vector(rotation),color=vector(color),shape=shape,material=material,
               collidable=collide=="true",queryable=query=="true",collisionRole=role,zone=zone,tags=tags(labels)))
        else:
            assert kind=="R"
            ident,start,end,width,style,link=row
            routes.append(dict(id=ident,a=vector(start),b=vector(end),width=float(width),
                               **{"class":style},**({"link":tags(link)} if link else {})))
    data.update(parts=parts,routes=routes)
    (OUT/"overworld-geometry.json").write_text(json.dumps(data,indent=2))
    return len(parts),len(routes)

def main():
    parser=argparse.ArgumentParser()
    mode=parser.add_mutually_exclusive_group()
    mode.add_argument("--bosses",action="store_true",help="Include the actual current boss visuals and patrol at new map homes (no progression or combat).")
    mode.add_argument("--academy",action="store_true",help="Include the disposable playable Academy route with temporary progression.")
    options=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    run("python3","build_layout_data.py","--check")
    count,routes=export()
    project=json.loads((BASE/PROJECT).read_text())
    paths={v["$path"]:BASE/v["$path"] for v in project["tree"]["ServerScriptService"].values() if isinstance(v,dict)}
    if options.bosses or options.academy:
        include_bosses(project,paths,options.academy)
    project_bytes=json.dumps(project,indent=2).encode()+b"\n" if options.bosses or options.academy else (BASE/PROJECT).read_bytes()
    contents={name:path.read_bytes() for name,path in paths.items()}
    contents[PROJECT]=project_bytes
    h=hashlib.sha256()
    for name,data in sorted(contents.items()):
        h.update(name.encode()+b"\0"+data+b"\0")
        if name.endswith(".luau"):
            subprocess.run(["luau-compile",str(paths[name])],stdout=subprocess.DEVNULL,check=True)
    stamp=h.hexdigest()
    artifact=ACADEMY_ARTIFACT if options.academy else BOSS_ARTIFACT if options.bosses else ARTIFACT
    with tempfile.TemporaryDirectory() as d:
        temp=Path(d)
        for name,data in contents.items():
            (temp/name).write_bytes(data)
        script=(temp/SERVER).read_text()
        needle='workspace:SetAttribute("ReviewBuildName","Map10V21OverworldReview")'
        assert script.count(needle)==1
        replacement=f'workspace:SetAttribute("ReviewSourceSha256","{stamp}")\n'+needle
        if options.academy:
            replacement=replacement.replace(Path(ARTIFACT).stem,Path(ACADEMY_ARTIFACT).stem)
        elif options.bosses:
            replacement='require(script.Parent.BossPlacementPreview)(world)\n'+replacement.replace(Path(ARTIFACT).stem,Path(BOSS_ARTIFACT).stem)
        script=script.replace(needle,replacement)
        if options.academy:
            start="local function setup(player) player.RespawnLocation=spawn end"
            assert script.count(start)==1
            script=script.replace(start,'require(script.Parent.AcademyRoutePreview)(world)\n'+start)
        (temp/SERVER).write_text(script)
        run("rojo","build",str(temp/PROJECT),"-o",str(OUT/artifact))
    manifest=dict(sourceSha256=stamp,artifactSha256=hashlib.sha256((OUT/artifact).read_bytes()).hexdigest(),
                  parts=count,routes=routes,streaming={"min":256,"target":896},isolation="Studio local only")
    if options.bosses:
        manifest["bossPreview"]="Current roster visuals and patrol only, no combat/progression"
    if options.academy:
        manifest["academyRoute"]="Unpublished Studio only; adjustable silent held-input Beam and Test Flight, temporary coins and gear; no microphone or live saves"
    provenance=("academy-route-provenance.json" if options.academy else
                "boss-placement-provenance.json" if options.bosses else "overworld-provenance.json")
    (OUT/provenance).write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))

if __name__=="__main__":main()
