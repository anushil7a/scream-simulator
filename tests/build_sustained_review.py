"""Build disposable native Studio review places using normal ModuleScript loading.

This only assembles/compiles artifacts. It does not run Studio or verify audio.
Both outputs refuse to run Bootstrap outside unpublished local Studio places.
"""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def absolute_paths(node):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "$path":
                node[key] = str(ROOT / value)
            else:
                absolute_paths(value)
    elif isinstance(node, list):
        for value in node:
            absolute_paths(value)


def main():
    rojo = shutil.which("rojo") or "/opt/homebrew/bin/rojo"
    compiler = shutil.which("luau-compile") or "/opt/homebrew/bin/luau-compile"
    project = json.loads((ROOT / "default.project.json").read_text())
    absolute_paths(project)
    source = ROOT / "src/ServerScriptService"
    server = project["tree"]["ServerScriptService"]
    del server["$path"]
    for path in source.iterdir():
        if path.is_file() and path.suffix == ".luau":
            name = path.name.removesuffix(".server.luau").removesuffix(".luau")
            server[name] = {"$path": str(path)}
        else:
            raise RuntimeError(f"Explicitly map new server content before building: {path}")
    guard = '''-- DISPOSABLE LOCAL REVIEW ONLY: NEVER PUBLISH THIS BUILD.
assert(game:GetService("RunService"):IsStudio() and game.PlaceId == 0,
 "Open this disposable review as a local file in Studio; never publish it")
workspace:SetAttribute("LocalSustainedPrototype", true)
'''
    bootstrap = (source / "Bootstrap.server.luau").read_text()
    fixture = "\n".join((ROOT / "tests" / name).read_text() for name in
                         ["StudioSustainedDamage.server.luau", "StudioSustainedDestruction.server.luau"])
    output = ROOT / "build"
    output.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="scream-review-") as temp:
        temp = Path(temp)
        for name, appendix in [("SustainedLocalPlay", ""), ("SustainedNativeFixture", fixture)]:
            script = temp / "Bootstrap.server.luau"
            script.write_text(guard + bootstrap + "\n" + appendix)
            subprocess.run([compiler, str(script)], check=True, stdout=subprocess.DEVNULL)
            server["Bootstrap"] = {"$path": str(script)}
            project["name"] = name + "_DO_NOT_PUBLISH"
            project_path = temp / "review.project.json"
            project_path.write_text(json.dumps(project, indent=2))
            subprocess.run([rojo, "build", str(project_path), "-o", str(output / (name + ".rbxl"))], check=True)
    print("Built local play and synthetic native fixture places; neither was executed in Studio.")

if __name__ == "__main__":
    main()
