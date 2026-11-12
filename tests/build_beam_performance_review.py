"""Build only: isolated native beam measurement, never launches Studio."""
from pathlib import Path
import hashlib,json,subprocess
def validate_cadence(client,fixture):
 import re
 for name,source in [('Client',client),('Fixture',fixture)]:
  assert re.search(r'beamFrame\+=dt\s+if beamFrame>=1/30 then\s+beamFrame=0',source),name+' cadence changed'

def stamp(fixture,identity):
 token='__BEAM_PERFORMANCE_BUILD_ID__'
 assert fixture.count(token)==1,'Build identity token must occur exactly once'
 assert len(identity)==64 and all(c in '0123456789abcdef' for c in identity),'Invalid identity'
 return fixture.replace(token,identity)

R=Path(__file__).resolve().parents[1];out=R/'build';out.mkdir(exist_ok=True)
sources={'Fixture':R/'tests/StudioBeamPerformance.client.luau','BeamVisuals':R/'src/StarterPlayer/StarterPlayerScripts/BeamVisuals.luau','SustainedBeams':R/'src/StarterPlayer/StarterPlayerScripts/SustainedBeams.luau','ClientCadence':R/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau','BeamStyle':R/'src/ReplicatedStorage/Shared/BeamStyle.luau'}
snapshot={k:p.read_bytes() for k,p in sources.items()};copies={}
sha=lambda b:hashlib.sha256(b).hexdigest()
builderBytes=Path(__file__).read_bytes()
identity=sha(json.dumps({'sources':{k:sha(v) for k,v in snapshot.items()},'builder':sha(builderBytes)},sort_keys=True).encode())
validate_cadence(snapshot['ClientCadence'].decode(),snapshot['Fixture'].decode())
generated=stamp(snapshot['Fixture'].decode(),identity).encode()

for k,data in snapshot.items():
 if k=='ClientCadence':continue
 if k=='Fixture':data=generated
 p=out/('BeamPerformanceReview.'+k+('.client.luau' if k=='Fixture' else '.luau'));p.write_bytes(data);copies[k]=p.name
 subprocess.run(['luau-compile',str(p)],check=True,stdout=subprocess.DEVNULL,timeout=30)
client=snapshot['ClientCadence'].decode().replace('\r\n','\n')
assert 'beamFrame+=dt\n  if beamFrame>=1/30 then\n   beamFrame=0' in client,'Client cadence changed; update fixture before comparison'
fixture=snapshot['Fixture'].decode();assert 'game.PlaceId==0' in fixture and 'Run:IsStudio()' in fixture
for forbidden in ['DataStoreService','FireServer','MarketplaceService','SoundService'] : assert forbidden not in fixture
assert 'task.delay(35' in fixture and 'connection:Disconnect()' in fixture and 'Visuals.Clear()' in fixture
project={'name':'BeamPerformanceReview','tree':{'$className':'DataModel','Workspace':{'$className':'Workspace','SafeSpawn':{'$className':'SpawnLocation','$properties':{'Anchored':True,'Neutral':True,'Enabled':True,'Duration':0,'Size':[40,2,40],'Position':[300,0,300]}}},'ReplicatedStorage':{'$className':'ReplicatedStorage','BeamVisuals':{'$path':copies['BeamVisuals']},'SustainedBeams':{'$path':copies['SustainedBeams']},'Shared':{'$className':'Folder','BeamStyle':{'$path':copies['BeamStyle']}}},'StarterPlayer':{'$className':'StarterPlayer','StarterPlayerScripts':{'$className':'StarterPlayerScripts','Review':{'$path':copies['Fixture']}}}}}
pp=out/'BeamPerformanceReview.project.json';pp.write_text(json.dumps(project,indent=2))
artifact=out/'BeamPerformanceReview.rbxl';subprocess.run(['rojo','build',str(pp),'-o',str(artifact)],check=True,timeout=60)
for k,p in sources.items():assert p.read_bytes()==snapshot[k],'Source changed during build'
sha=lambda b:hashlib.sha256(b).hexdigest()
assert Path(__file__).read_bytes()==builderBytes,'Builder changed during build'
manifest={'nativeExecuted':False,'buildIdentity':identity,'builderSha256':sha(builderBytes),'generatedFixtureSha256':sha(generated),'sourceHashes':{k:sha(v) for k,v in snapshot.items()},'artifactSha256':sha(artifact.read_bytes()),'scope':'Studio-only client visuals; frame intervals/script durations, not GPU, phone or network measurements'}
(out/'BeamPerformanceReview.provenance.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(manifest,indent=2))
print('PASS compiled/built/structural checks only; native measurement pending')
