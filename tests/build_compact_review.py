"""Build guarded native compact review. No Studio execution or publication."""
from pathlib import Path
from collections import Counter
import copy,hashlib,json,re,shutil,subprocess,tempfile,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 rojo=shutil.which('rojo');compiler=shutil.which('luau-compile')
 if not rojo or not compiler:raise RuntimeError('Official Rojo and Luau compiler required')
 fixture=ROOT/'tests/StudioCompactCity.server.luau'
 sources=sorted((ROOT/'src').rglob('*.luau'))
 paths=sources+[ROOT/'default.project.json',ROOT/'assets/review/MosaicFountain.rbxmx',fixture,Path(__file__).resolve()]
 before={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in paths}
 fingerprint=sha(json.dumps(before,sort_keys=True).encode())
 project=copy.deepcopy(json.loads((ROOT/'default.project.json').read_text()))
 def absolute(node):
  if isinstance(node,dict):
   for key,value in node.items():
    if key=='$path':
     path=(ROOT/value).resolve()
     if not path.is_relative_to(ROOT):raise ValueError('Project reference escapes workspace')
     node[key]=str(path)
    else:absolute(value)
  elif isinstance(node,list):
   for value in node:absolute(value)
 absolute(project)
 project['name']='CompactCityNativeReview_LOCAL_ONLY'
 out=ROOT/'build';out.mkdir(exist_ok=True)
 # Never leave an old success sidecar beside a failed or partial replacement.
 (out/'CompactCityReview.provenance.json').unlink(missing_ok=True)
 base=Path.home()/'.compact-review-temp'
 if base.is_symlink() or (hasattr(base,'is_junction') and base.is_junction()):raise ValueError('Unsafe temporary root')
 base.mkdir(exist_ok=True)
 with tempfile.TemporaryDirectory(prefix='build-',dir=base) as name:
  temp=Path(name).resolve()
  if not temp.is_relative_to(base.resolve()):raise ValueError('Temporary workspace escaped')
  profile_path=ROOT/'src/ServerScriptService/Profiles.luau';profiles=profile_path.read_text()
  expression='return DataStoreService:GetDataStore(RunService:IsStudio() and "ScreamSimulator_Studio_v2" or "ScreamSimulator_v1")'
  if profiles.count(expression)!=1:raise ValueError('Review new profile store initialization before building fixture')
  profiles=profiles.replace(expression,'error("COMPACT REVIEW: DataStore acquisition disabled")')
  copied_profile=temp/'Profiles.luau';copied_profile.write_text(profiles)
  guard='''-- UNSAVED LOCAL REVIEW ONLY; NEVER PUBLISH.
assert(game:GetService("RunService"):IsStudio() and game.PlaceId==0,"Open local Studio review only")
workspace:SetAttribute("LocalSustainedPrototype",true)
workspace:SetAttribute("CompactProfileCalls",0)
local compactProfiles=require(script.Parent.Profiles)
local function denyCompactPersistence()
 workspace:SetAttribute("CompactProfileCalls",workspace:GetAttribute("CompactProfileCalls")+1)
 error("COMPACT REVIEW: profile Load/Save disabled")
end
compactProfiles.Load=denyCompactPersistence;compactProfiles.Save=denyCompactPersistence
'''
  bootstrap_path=ROOT/'src/ServerScriptService/Bootstrap.server.luau'
  bootstrap=guard+'workspace:SetAttribute("CompactReviewFingerprint","'+fingerprint+'")\n'+bootstrap_path.read_text()+'\n'+fixture.read_text()
  copied_bootstrap=temp/'Bootstrap.server.luau';copied_bootstrap.write_text(bootstrap)
  server=project['tree']['ServerScriptService'];del server['$path']
  for path in sorted((ROOT/'src/ServerScriptService').iterdir()):
   if path.suffix!='.luau':raise ValueError('Review unexpected server content')
   key=path.name.removesuffix('.server.luau').removesuffix('.luau')
   selected=copied_bootstrap if path==bootstrap_path else copied_profile if path==profile_path else path
   server[key]={'$path':str(selected)}
  clients=project['tree']['StarterPlayer']['StarterPlayerScripts'];del clients['$path']
  client_path=ROOT/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau'
  for path in sorted(client_path.parent.iterdir()):
   if path==client_path:continue
   if path.suffix!='.luau':raise ValueError('Review unexpected client content')
   key=path.name.removesuffix('.client.luau').removesuffix('.luau');clients[key]={'$path':str(path)}
  for path in (copied_profile,copied_bootstrap):subprocess.run([compiler,str(path)],check=True,stdout=subprocess.DEVNULL)
  config=temp/'review.project.json';config.write_text(json.dumps(project))
  xml=out/'CompactCityReview.rbxlx';binary=out/'CompactCityReview.rbxl'
  subprocess.run([rojo,'build',str(config),'-o',str(xml)],check=True)
  expected=[]
  for path in sources:
   if path==client_path:continue
   text=bootstrap if path==bootstrap_path else profiles if path==profile_path else path.read_text()
   expected.append(sha(text.encode()))
  actual=[]
  for item in ET.fromstring(xml.read_bytes()).iter('Item'):
   if item.get('class') in ('Script','LocalScript','ModuleScript'):
    source=next(p.text or '' for p in item.find('Properties') if p.get('name')=='Source');actual.append(sha(source.encode()))
  if Counter(actual)!=Counter(expected):raise ValueError('Guarded review source audit mismatch')
  subprocess.run([rojo,'build',str(config),'-o',str(binary)],check=True)
  after={p.relative_to(ROOT).as_posix():sha(p.read_bytes()) for p in paths}
  if before!=after:raise RuntimeError('Production changed during build; rerun')
  (out/'CompactCityReview.provenance.json').write_text(json.dumps({'status':'built/compiled only; native checks NOT executed','fingerprint':fingerprint,'sources':before,'sourceCount':len(actual),'omittedClient':client_path.relative_to(ROOT).as_posix(),'overrides':['Bootstrap local-only guard and fixture','Profiles DataStore acquisition disabled, Load/Save fail closed'],'artifacts':{p.name:sha(p.read_bytes()) for p in (xml,binary)}},indent=2)+'\n')
 print('PASS guarded compact native review built and source audited; no native execution')
if __name__=='__main__':main()
