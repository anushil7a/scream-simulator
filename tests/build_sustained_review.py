"""Build disposable native Studio review places using normal ModuleScript loading.

This only assembles/compiles artifacts. It does not run Studio or verify audio.
All outputs refuse to run Bootstrap outside unpublished local Studio places.
"""
import argparse
import copy
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
    parser = argparse.ArgumentParser()
    parser.add_argument('--transport-mutation', choices=('drop-stop', 'corrupt-replay'),
                        help='Build only an intentionally broken, guarded transport negative control')
    parser.add_argument('--test-tools-local', action='store_true',
                        help='Build one guarded Test Tools place, using procedural fallback for two incompatible VFX binaries')
    parser.add_argument("--boss-arena-local-qa", action="store_true",
                        help="Build the single-player, unpublished boss diagnostic place only")
    parser.add_argument("--combat-readouts-local-qa", action="store_true",
                        help="Build the unpublished combat readout diagnostic place only")
    parser.add_argument("--central-pvp-local-qa", action="store_true",
                        help="Build the unpublished two-client middle-green PvP diagnostic place")
    parser.add_argument("--test-beam-damage-local-qa", action="store_true",
                        help="Build the unpublished manual two-player Test Beam damage review")
    parser.add_argument("--resonance-local-qa", action="store_true",
                        help="Build the unpublished Resonance Hall combat playtest")
    args = parser.parse_args()
    if args.resonance_local_qa and any((args.test_beam_damage_local_qa, args.central_pvp_local_qa,
                                      args.combat_readouts_local_qa, args.boss_arena_local_qa,
                                      args.transport_mutation, args.test_tools_local)):
        parser.error("Resonance Hall combat playtest is a separate fixture")
    if args.test_beam_damage_local_qa and (args.central_pvp_local_qa or args.combat_readouts_local_qa or args.boss_arena_local_qa or args.transport_mutation or args.test_tools_local):
        parser.error("Test Beam damage review is a separate local-only fixture")
    if args.central_pvp_local_qa and (args.combat_readouts_local_qa or args.boss_arena_local_qa or args.transport_mutation or args.test_tools_local):
        parser.error("Central PvP diagnostic is a separate local-only fixture")
    if args.combat_readouts_local_qa and (args.boss_arena_local_qa or args.transport_mutation or args.test_tools_local):
        parser.error("Combat readouts diagnostic is a separate local-only fixture")
    if args.boss_arena_local_qa and (args.test_tools_local or args.transport_mutation):
        parser.error("Boss arena diagnostic is a separate local-only fixture")
    if args.test_tools_local and args.transport_mutation:
        parser.error('--test-tools-local and --transport-mutation are separate fixtures')
    rojo = shutil.which("rojo") or "/opt/homebrew/bin/rojo"
    compiler = shutil.which("luau-compile") or "/opt/homebrew/bin/luau-compile"
    project = json.loads((ROOT / "default.project.json").read_text())
    if args.test_tools_local:
        # Rojo in the review environment cannot decode two legacy .rbxm
        # templates. The production project and both asset files are untouched.
        templates = project["tree"]["ReplicatedStorage"]["VfxTemplates"]
        del templates["FireBeam"], templates["StarterBeam"]
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
assert(game:GetService("RunService"):IsStudio() and game.PlaceId == 0 and game.GameId == 0,
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
          "StudioTrainingRoam.server.luau", "StudioPerformance.server.luau", "StudioVoiceTransport.server.luau", "StudioVoiceTransport.client.luau", "support/HeartbeatSummary.luau"]),
    })
    if args.test_tools_local:
        fingerprint_paths = sorted(set(fingerprint_paths) | {
            ROOT / "assets/vfx/HollowPurpleBeam.rbxmx",
            ROOT / "assets/review/MosaicFountain.rbxmx",
        })
    if args.test_beam_damage_local_qa:
        fingerprint_paths = sorted(set(fingerprint_paths) | {ROOT / "tests/StudioTestBeamDamageReview.server.luau"})
    if args.central_pvp_local_qa:
        fingerprint_paths = sorted(set(fingerprint_paths) | {
            ROOT / "tests/StudioCentralPvpReview.server.luau",
            ROOT / "tests/StudioCombatReadoutsReview.server.luau",
        })
    if args.combat_readouts_local_qa:
        fingerprint_paths = sorted(set(fingerprint_paths) | {ROOT / "tests/StudioCombatReadoutsReview.server.luau"})
    if args.boss_arena_local_qa:
        fingerprint_paths = sorted(set(fingerprint_paths) | {ROOT / "tests/StudioBossArenaReview.server.luau"})
    if args.resonance_local_qa:
        arena = ROOT / "prototypes/resonance-arena"
        arena_cases = ROOT / "tests/StudioResonanceCombat.server.luau"
        fingerprint_paths = sorted(set(fingerprint_paths) | set(arena.glob("*.luau")) | {arena_cases})
        # Use the real combat code with only this generated place's city setup replaced.
        assert bootstrap.count("BeachVolley.Start(workspace.ScreamSimulatorWorld)") == 1
        bootstrap = bootstrap.replace("BeachVolley.Start(workspace.ScreamSimulatorWorld)",
            'assert(Config.MovementPassId == 0, "Local arena has no movement pass")\n'
            'for _, item in ipairs(ShopCatalog.Items) do assert(item.id == 0, "Local arena has no paid products") end')
    def source_fingerprint():
        digest = hashlib.sha256()
        digest.update(("resonance-local-qa" if args.resonance_local_qa else "test-beam-damage-local-qa" if args.test_beam_damage_local_qa else "central-pvp-local-qa" if args.central_pvp_local_qa else "combat-readouts-local-qa" if args.combat_readouts_local_qa else "boss-arena-local-qa" if args.boss_arena_local_qa else "test-tools-local" if args.test_tools_local else args.transport_mutation or "none").encode() + b"\0")
        for path in fingerprint_paths:
            digest.update(path.relative_to(ROOT).as_posix().encode() + b"\0")
            digest.update(path.read_bytes() + b"\0")
        return digest.hexdigest()
    source_hash = source_fingerprint()
    output = ROOT / "build"
    output.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="scream-review-") as temp:
        temp = Path(temp)
        transport_fixture = (ROOT / "tests/StudioVoiceTransport.server.luau").read_text()
        builds = [("SustainedLocalPlay", ""), ("SustainedNativeFixture", fixture), ("PerformanceReview", performance), ("VoiceTransportReview", transport_fixture), ("TrainingRoamReview", (ROOT / "tests/StudioTrainingRoam.server.luau").read_text())]
        if args.resonance_local_qa:
            portal_prep = '''
require(script.Parent.PortalTravel).SetPreparation(function(p, character)
 local s=sessions[p]
 if closing or not s or s.character~=character or s.flight then return false end
 local now=os.clock()
 cancelSustained(p,s,now)
 VoiceCombat.Cancel(s.voice);p:SetAttribute("CaptureStarted",0)
 if testBeamEnd(p,s,now) then task.defer(state,p) end
 return true
end)
'''
            builds = [("ResonanceCombatLocalReview", portal_prep + arena_cases.read_text())]
        elif args.test_beam_damage_local_qa:
            builds = [("TestBeamDamageLocalReview", (ROOT / "tests/StudioTestBeamDamageReview.server.luau").read_text())]
        elif args.central_pvp_local_qa:
            appendix = "\n".join((ROOT / "tests" / file).read_text() for file in
                                  ("StudioCombatReadoutsReview.server.luau", "StudioCentralPvpReview.server.luau"))
            builds = [("CentralPvpLocalReview", appendix)]
        elif args.combat_readouts_local_qa:
            builds = [("CombatReadoutsLocalReview", (ROOT / "tests/StudioCombatReadoutsReview.server.luau").read_text())]
        elif args.boss_arena_local_qa:
            builds = [("BossArenaLocalReview", (ROOT / "tests/StudioBossArenaReview.server.luau").read_text())]
        elif args.test_tools_local:
            builds = [("TestToolsLocalPlay", "")]
        elif args.transport_mutation:
            builds = [("VoiceTransportDropStop" if args.transport_mutation == "drop-stop" else "VoiceTransportCorruptReplay", transport_fixture)]
        template = copy.deepcopy(project)
        for name, appendix in builds:
            project = copy.deepcopy(template)
            server = project["tree"]["ServerScriptService"]
            script = temp / "Bootstrap.server.luau"
            provenance = output / (name + ".provenance.json")
            provenance.unlink(missing_ok=True)
            stamp = f'workspace:SetAttribute("ReviewBuildName", "{name}")\nworkspace:SetAttribute("ReviewSourceSha256", "{source_hash}")\n'
            script.write_text(guard + stamp + bootstrap + "\n" + appendix)
            subprocess.run([compiler, str(script)], check=True, stdout=subprocess.DEVNULL)
            server["Bootstrap"] = {"$path": str(script)}
            if args.resonance_local_qa:
                server["Arena"] = {"$path": str(arena / "Arena.server.luau")}
                server["PortalTravel"] = {"$path": str(arena / "PortalTravel.luau")}
                server["World"] = {"$path": str(arena / "CombatWorld.luau")}
                profiles = (source / "Profiles.luau").read_text()
                store_call = 'return DataStoreService:GetDataStore(RunService:IsStudio() and "ScreamSimulator_Studio_v2" or "ScreamSimulator_v1")'
                assert profiles.count(store_call) == 1
                profile_copy = temp / "Profiles.luau"
                profile_copy.write_text(profiles.replace(store_call, 'return nil -- This arena has no persistence'))
                server["Profiles"] = {"$path": str(profile_copy)}
                shared = project["tree"]["ReplicatedStorage"]["Shared"]
                shared_directory = Path(shared.pop("$path"))
                shared["$className"] = "Folder"
                for shared_path in shared_directory.glob("*.luau"):
                    shared[shared_path.stem] = {"$path": str(shared_path)}
                config = (shared_directory / "Config.luau").read_text()
                assert config.count("\nreturn Config") == 1
                config_copy = temp / "Config.luau"
                config_copy.write_text(config.replace("\nreturn Config", '''
Config.CompactCity=false
Config.ResonanceLayout=require(script.Parent:WaitForChild("ResonanceLayout"))
Config.ProfileQuestCatalog=Config.Quests
Config.Quests={}
Config.MapMin=Vector3.new(-88,-20,-76)
Config.MapMax=Vector3.new(88,120,272)
local combat=Config.ResonanceLayout.Combat
Config.ZoneMin=Vector3.new(combat.minX,combat.minY,combat.minZ)
Config.ZoneMax=Vector3.new(combat.maxX,combat.maxY,combat.maxZ)
local inHall=Config.InArena
function Config.InArena(p)
 return inHall(p) and not Config.ResonanceLayout.IsSafeApron(p)
end
return Config'''))
                shared["Config"] = {"$path": str(config_copy)}
                shared["ResonanceLayout"] = {"$path": str(arena / "Layout.luau")}
                clients = project["tree"]["StarterPlayer"]["StarterPlayerScripts"]
                client_directory = Path(clients.pop("$path"))
                for path in client_directory.glob("*.luau"):
                    name_in_place = path.name.removesuffix(".client.luau").removesuffix(".luau")
                    clients[name_in_place] = {"$path": str(path)}
                clients["CityMapBase"] = clients["CityMap"]
                clients["CityMap"] = {"$path": str(arena / "Map.luau")}
                for arena_source in (*arena.glob("*.luau"), config_copy, profile_copy):
                    subprocess.run([compiler, str(arena_source)], check=True, stdout=subprocess.DEVNULL)
            if name.startswith("VoiceTransport"):
                clients = project["tree"]["StarterPlayer"]["StarterPlayerScripts"]
                del clients["$path"]
                for client_path in (ROOT / "src/StarterPlayer/StarterPlayerScripts").glob("*.luau"):
                    client_name = client_path.name.removesuffix(".client.luau").removesuffix(".luau")
                    clients[client_name] = {"$path": str(client_path)}
                client_script = temp / "Client.client.luau"
                client_fixture = (ROOT / "tests/StudioVoiceTransport.client.luau").read_text()
                if args.transport_mutation == "drop-stop":
                    needle = "   nativeSend(verb,arg)"
                    assert client_fixture.count(needle) == 1
                    client_fixture = client_fixture.replace(needle,
                        '   if not (verb=="SustainedStop" and arg==5) then nativeSend(verb,arg) end')
                if args.transport_mutation == "corrupt-replay":
                    adapter = (source / "SustainedAttackAdapter.luau").read_text()
                    needle = '  if not sampleIndex(request.sample) or request.sample<=intent.sample then return false,"sample" end'
                    assert adapter.count(needle) == 1
                    adapter = adapter.replace(needle,
                        '  if sampleIndex(request.sample) and request.sample<=intent.sample then active.power=request.power;intent.aim=request.aim;return false,"sample" end\n' + needle)
                    mutant = temp / "SustainedAttackAdapter.luau"
                    mutant.write_text(adapter)
                    subprocess.run([compiler, str(mutant)], check=True, stdout=subprocess.DEVNULL)
                    server["SustainedAttackAdapter"] = {"$path": str(mutant)}
                client_script.write_text('assert(game:GetService("RunService"):IsStudio() and game.PlaceId == 0)\n' +
                    (ROOT / "src/StarterPlayer/StarterPlayerScripts/Client.client.luau").read_text() + "\n" + client_fixture)
                subprocess.run([compiler, str(client_script)], check=True, stdout=subprocess.DEVNULL)
                clients["Client"] = {"$path": str(client_script)}
            if name == "TrainingRoamReview":
                # Server/physics-only test: exclude the live microphone controller,
                # which legitimately clears synthetic readiness during onboarding.
                clients = project["tree"]["StarterPlayer"]["StarterPlayerScripts"]
                clients.pop("$path", None)
                for client_path in (ROOT / "src/StarterPlayer/StarterPlayerScripts").glob("*.luau"):
                    if client_path.name == "Client.client.luau":
                        continue
                    client_name = client_path.name.removesuffix(".client.luau").removesuffix(".luau")
                    clients[client_name] = {"$path": str(client_path)}
                clients.pop("Client", None)
            project["name"] = name + "_DO_NOT_PUBLISH"
            project_path = temp / "review.project.json"
            project_path.write_text(json.dumps(project, indent=2))
            subprocess.run([rojo, "build", str(project_path), "-o", str(output / (name + ".rbxl"))], check=True)
            if source_fingerprint() != source_hash:
                raise RuntimeError("Review sources changed during build; rebuild before testing")
            provenance.write_text(json.dumps({
                "build": name, "sourceSha256": source_hash, "mutation": args.transport_mutation,
                "artifactSha256": hashlib.sha256((output / (name + ".rbxl")).read_bytes()).hexdigest(),
                "scope": "Compiled disposable local fixture; not executed or published",
                **({"proceduralFallback": ["FireBeam", "StarterBeam"]} if args.test_tools_local else {}),
            }, indent=2) + "\n")
    if args.resonance_local_qa:
        print("Built unpublished Resonance Hall combat review; no Studio test was run.")
    elif args.test_beam_damage_local_qa:
        print("Built unpublished Test Beam damage review; no Studio test was run.")
    elif args.central_pvp_local_qa:
        print("Built unpublished central PvP diagnostic; no Studio test was run.")
    elif args.combat_readouts_local_qa:
        print("Built unpublished combat readouts diagnostic; no Studio test was run.")
    elif args.boss_arena_local_qa:
        print("Built unpublished boss diagnostic; no Studio test was run.")
    elif args.test_tools_local:
        print("Built Test Tools local play with procedural fallback for two legacy VFX assets; not executed in Studio.")
    else:
        print("Built local play, native and transport fixtures, and performance review; none was executed in Studio.")

if __name__ == "__main__":
    main()
