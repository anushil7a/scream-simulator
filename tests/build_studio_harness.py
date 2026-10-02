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

def inline(path):
    text=path.read_text()
    text=text.replace('require(RS:WaitForChild("Shared"):WaitForChild("Config"))','modules.Config')
    text=re.sub(r'require\((?:script.Parent|game:GetService\("ReplicatedStorage"\)(?::WaitForChild\("Shared"\))?):WaitForChild\("([A-Za-z0-9_]+)"\)\)',r'modules.\1',text)
    text=re.sub(r'require\((?:game:GetService\("ReplicatedStorage"\)|[^()])+\)',lambda m:'modules.'+re.search(r'\.([A-Za-z0-9_]+)\)$',m[0])[1],text)
    assert 'require(' not in text, path
    return text

def bundle(paths,entry):
    chunks=['assert(game:GetService("RunService"):IsStudio() and game.PlaceId==0,"Disposable local Studio place required")','local modules={}']
    for path in paths:
        chunks.append('modules.'+path.stem+'=(function()\n'+inline(path)+'\nend)()')
    chunks.append(inline(entry))
    return '\n'.join(chunks)

out=ROOT/'build';out.mkdir(exist_ok=True)
common=[shared/'VoiceCombat.luau',shared/'Progression.luau',shared/'Config.luau']
server_order=common+[shared/'ProfileLease.luau',shared/'DestructionRules.luau']+[server/(n+'.luau') for n in ['City','World','CombatRules','Profiles','DeveloperAccess','Entitlements','Equipment','SoccerChallenge','Destruction']]
(out/'StudioServerHarness.luau').write_text(bundle(server_order,server/'Bootstrap.server.luau'))
(out/'StudioClientHarness.luau').write_text(bundle(common+[shared/'MicPower.luau',client/'Microphone.luau',client/'ScreamEffects.luau'],client/'Client.client.luau'))
(out/'StudioAnimationsHarness.luau').write_text(bundle(common,client/'RunAnimation.client.luau')+'\n'+inline(client/'Residents.client.luau'))
print('Assembled server, client and animation harnesses from current source')

world_source=bundle(common+[server/'City.luau'],server/'World.luau')
head,tail=world_source.rsplit('return World',1)
(out/'StudioWorldHarness.luau').write_text(head+'return World.Build()'+tail)
