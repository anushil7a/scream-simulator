"""Build disposable native Studio review places using normal ModuleScript loading.

This only assembles/compiles artifacts. It does not run Studio or verify audio.
All outputs refuse to run Bootstrap outside unpublished local Studio places.
"""
import json
import hashlib
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
                         ["StudioSustainedDamage.server.luau", "StudioSustainedDestruction.server.luau", "StudioSustainedPvp.server.luau", "StudioProgression.server.luau", "StudioFirstBeam.server.luau"])
    performance = "local summarizeHeartbeat=(function()\n" + (ROOT / "tests/support/HeartbeatSummary.luau").read_text() + "\nend)()\n" + (ROOT / "tests/StudioPerformance.server.luau").read_text()
    fingerprint_paths = sorted(set((ROOT / "src").rglob("*.luau")) | {
        ROOT / "default.project.json", Path(__file__).resolve(),
        *(ROOT / "tests" / name for name in ["StudioSustainedDamage.server.luau",
          "StudioSustainedDestruction.server.luau", "StudioSustainedPvp.server.luau", "StudioProgression.server.luau", "StudioFirstBeam.server.luau",
          "StudioPerformance.server.luau", "StudioVoiceTransport.server.luau", "StudioVoiceTransport.client.luau", "support/HeartbeatSummary.luau"]),
    })
    def source_fingerprint():
        digest = hashlib.sha256()
        for path in fingerprint_paths:
            digest.update(path.relative_to(ROOT).as_posix().encode() + b"\0")
            digest.update(path.read_bytes() + b"\0")
        return digest.hexdigest()
    source_hash = source_fingerprint()
    output = ROOT / "build"
    output.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="scream-review-") as temp:
        temp = Path(temp)
        for name, appendix in [("SustainedLocalPlay", ""), ("SustainedNativeFixture", fixture), ("PerformanceReview", performance), ("VoiceTransportReview", (ROOT / "tests/StudioVoiceTransport.server.luau").read_text())]:
            script = temp / "Bootstrap.server.luau"
            provenance = output / (name + ".provenance.json")
            provenance.unlink(missing_ok=True)
            stamp = f'workspace:SetAttribute("ReviewBuildName", "{name}")\nworkspace:SetAttribute("ReviewSourceSha256", "{source_hash}")\n'
            script.write_text(guard + stamp + bootstrap + "\n" + appendix)
            subprocess.run([compiler, str(script)], check=True, stdout=subprocess.DEVNULL)
            server["Bootstrap"] = {"$path": str(script)}
            if name == "VoiceTransportReview":
                clients = project["tree"]["StarterPlayer"]["StarterPlayerScripts"]
                del clients["$path"]
                for client_path in (ROOT / "src/StarterPlayer/StarterPlayerScripts").glob("*.luau"):
                    client_name = client_path.name.removesuffix(".client.luau").removesuffix(".luau")
                    clients[client_name] = {"$path": str(client_path)}
                client_script = temp / "Client.client.luau"
                client_script.write_text('assert(game:GetService("RunService"):IsStudio() and game.PlaceId == 0)\n' +
                    (ROOT / "src/StarterPlayer/StarterPlayerScripts/Client.client.luau").read_text() + "\n" +
                    (ROOT / "tests/StudioVoiceTransport.client.luau").read_text())
                subprocess.run([compiler, str(client_script)], check=True, stdout=subprocess.DEVNULL)
                clients["Client"] = {"$path": str(client_script)}
            project["name"] = name + "_DO_NOT_PUBLISH"
            project_path = temp / "review.project.json"
            project_path.write_text(json.dumps(project, indent=2))
            subprocess.run([rojo, "build", str(project_path), "-o", str(output / (name + ".rbxl"))], check=True)
            if source_fingerprint() != source_hash:
                raise RuntimeError("Review sources changed during build; rebuild before testing")
            provenance.write_text(json.dumps({
                "build": name, "sourceSha256": source_hash,
                "artifactSha256": hashlib.sha256((output / (name + ".rbxl")).read_bytes()).hexdigest(),
                "scope": "Compiled disposable local fixture; not executed or published",
            }, indent=2) + "\n")
    print("Built local play, native and transport fixtures, and performance review; none was executed in Studio.")

if __name__ == "__main__":
    main()
