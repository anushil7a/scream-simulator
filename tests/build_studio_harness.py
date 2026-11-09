"""Assemble actual source for disposable-place MCP checks when script insertion is unavailable.
Only dependency resolution changes. This does not verify normal Script loading or live voice.
Run the server/client outputs once per fresh Studio play session; Stop cleans connections.
"""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[1]
shared=ROOT/'src/ReplicatedStorage/Shared'
server=ROOT/'src/ServerScriptService'
client=ROOT/'src/StarterPlayer/StarterPlayerScripts'

# Resolve only repository-owned, literal module paths. Unknown forms fail closed.
MODULES={}
for directory in (shared,server,client):
    for path in directory.glob('*.luau'):
        if path.name.endswith(('.server.luau','.client.luau')):
            continue
        if path.stem in MODULES:
            raise RuntimeError(f"Ambiguous harness module: {path.stem}")
        MODULES[path.stem]=path
REQUIRE=re.compile(r'require\((?:script\.Parent|RS|ReplicatedStorage|game\.ReplicatedStorage|game:GetService\("ReplicatedStorage"\))(?:(?:\.[A-Za-z0-9_]+)|(?::WaitForChild\("[A-Za-z0-9_]+"\)))+\)')

def inline(path):
    def replace(match):
        names=re.findall(r'\.([A-Za-z0-9_]+)|:WaitForChild\("([A-Za-z0-9_]+)"\)',match[0])
        name=next(value for value in names[-1] if value)
        if name not in MODULES:
            raise RuntimeError(f"Unknown dependency {name} in {path}")
        return 'modules.'+name
    text=REQUIRE.sub(replace,path.read_text())
    if re.search(r'\brequire\s*\(',text):
        raise RuntimeError(f"Unsupported require expression in {path}")
    return text

def bundle(paths,entry):
    chunks=['assert(game:GetService("RunService"):IsStudio() and game.PlaceId==0,"Disposable local Studio place required")','local modules={}']
    visited=set();visiting=set()
    def dependencies(text):
        for name in dict.fromkeys(re.findall(r'\bmodules\.([A-Za-z0-9_]+)',text)):
            visit(MODULES[name])
    def visit(path):
        if path in visited: return
        if path in visiting: raise RuntimeError(f"Circular harness dependency: {path}")
        visiting.add(path)
        text=inline(path);dependencies(text)
        chunks.append('modules.'+path.stem+'=(function()\n'+text+'\nend)()')
        visiting.remove(path);visited.add(path)
    for path in paths: visit(path)
    text=inline(entry);dependencies(text);chunks.append(text)
    return '\n'.join(chunks)

out=ROOT/'build';out.mkdir(exist_ok=True)
common=[shared/'VoiceCombat.luau',shared/'Progression.luau',shared/'Config.luau']
server_order=common+[shared/'ProfileLease.luau',shared/'DestructionRules.luau',shared/'QuestLifecycle.luau']+[server/(n+'.luau') for n in ['City','World','CombatRules','Profiles','DeveloperAccess','Entitlements','Equipment','SoccerChallenge','Destruction']]
(out/'StudioServerHarness.luau').write_text(bundle(server_order,server/'Bootstrap.server.luau'))
(out/'StudioClientHarness.luau').write_text(bundle(common+[shared/'MicPower.luau',client/'Microphone.luau',client/'ScreamEffects.luau'],client/'Client.client.luau'))
(out/'StudioAnimationsHarness.luau').write_text(bundle(common,client/'RunAnimation.client.luau')+'\n'+inline(client/'Residents.client.luau'))
print('Assembled server, client and animation harnesses from current source')

world_source=bundle(common+[server/'City.luau'],server/'World.luau')
head,tail=world_source.rsplit('return World',1)
(out/'StudioWorldHarness.luau').write_text(head+'return World.Build()'+tail)

# Isolated actual-service collection/cleanup audit with fake player records.
soccer_source=bundle(common+[server/'CombatRules.luau'],server/'SoccerChallenge.luau')
audit_source=(ROOT/'tests/StudioSoccerAudit.luau').read_text()
(out/'StudioSoccerHarness.luau').write_text('assert(game.PlaceId==0);local world=workspace:FindFirstChild("ScreamSimulatorWorld");local owned=not world;if not world then world=Instance.new("Model");world.Name="ScreamSimulatorWorld";world.Parent=workspace end\nlocal Soccer=(function()\n'+soccer_source+'\nend)()\nlocal audit=(function()\n'+audit_source+'\nend)()\nlocal result=audit(Soccer);if owned then world:Destroy() end;return result')
