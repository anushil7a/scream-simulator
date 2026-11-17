"""Build a guarded blank Studio place without any game bootstrap or account integrations."""
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

BASE = Path(__file__).resolve().parent
OUT = BASE.parents[1] / "build" / "map21"
OUT.mkdir(parents=True, exist_ok=True)

def command(*args):
    return subprocess.run(args, check=True, text=True, capture_output=True).stdout

def serialize():
    parts, routes = [], []
    vector = lambda s: list(map(float, s.split(",")))
    for line in command("luau", str(BASE / "export_geometry.luau")).splitlines():
        kind, *data = line.split("|")
        if kind == "P":
            name, point, size, rot, color, shape, material, collision, tags = data
            parts.append(dict(id=name, position=vector(point), size=vector(size), rotation=vector(rot),
                              color=vector(color), shape=shape, material=material,
                              collidable=collision=="true",tags=tags.split(",") if tags else []))
        else:
            assert kind=="R"
            name,start,end,width=data
            routes.append(dict(id=name,a=vector(start),b=vector(end),width=float(width)))
    assert len(parts)>100 and len(routes)>=3
    return dict(parts=parts,routes=routes)

def main():
    srcs = ["FoundryPreview.server.luau", "Zone05Geometry.luau", "FoundryAmbience.client.luau"]
    source_hash = hashlib.sha256()
    for name in [*srcs,"foundry.project.json"]:
        source_hash.update(name.encode() + b"\0" + (BASE/name).read_bytes() + b"\0")
    stamp=source_hash.hexdigest()
    for name in srcs:
        command("luau-compile", str(BASE/name))
    geom=serialize()
    (OUT/"geometry.json").write_text(json.dumps(geom,indent=2))
    with tempfile.TemporaryDirectory() as tmp:
        tmp=Path(tmp)
        for name in [*srcs,"foundry.project.json"]:
            original=(BASE/name).read_text()
            if name == srcs[0]:
                needle='workspace:SetAttribute("ReviewBuildName", "Map10V21FoundryReview")'
                assert original.count(needle)==1
                original=original.replace(needle, f'workspace:SetAttribute("ReviewSourceSha256", "{stamp}")\n'+needle)
            (tmp/name).write_text(original)
        artifact=OUT/"Map10V21FoundryReview.rbxl"
        print(command("rojo","build",str(tmp/"foundry.project.json"),"-o",str(artifact)),end="")
    manifest=dict(sourceSha256=stamp, artifactSha256=hashlib.sha256(artifact.read_bytes()).hexdigest(),
                  parts=len(geom["parts"]), routes=len(geom["routes"]), isolation="unpublished Studio only, no production server")
    (OUT/"provenance.json").write_text(json.dumps(manifest,indent=2)+"\n")
    print(json.dumps(manifest,indent=2))

if __name__=="__main__":
    main()
