"""Actual developer authorization, command and sanitizer with mocked engine services.
No native execution, network, or real persistence. --baseline reproduces pre-fix failures.
"""
from config_fixture import inline_compact_layout
from pathlib import Path
import argparse, re, subprocess, tempfile
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--baseline',action='store_true');parser.add_argument('--negative-controls',action='store_true');args=parser.parse_args()
def read(name):
 if args.baseline:
  return subprocess.check_output(['git','show','4e37a44:'+name],cwd=root,text=True,encoding='utf-8')
 return (root/name).read_text(encoding='utf-8')
config=read('src/ReplicatedStorage/Shared/Config.luau')
config=inline_compact_layout(config,root)
profiles=read('src/ServerScriptService/Profiles.luau')
access=read('src/ServerScriptService/DeveloperAccess.luau')
server=read('src/ServerScriptService/Bootstrap.server.luau')
dev=server[server.index('local function dev(p,command)'):server.index('World.OnVehicleSweep=')]
visibility=re.search(r'devAccess=(Access\.IsAuthorized\(.*?\)),savingAvailable=',server).group(1)
preamble=r"""
local Healing=require('../src/ReplicatedStorage/Shared/Healing')
local Combat=require('../src/ReplicatedStorage/Shared/VoiceCombat')
local Progression=require('../src/ReplicatedStorage/Shared/Progression')
local Lease=require('../src/ReplicatedStorage/Shared/ProfileLease')
local Vector3={new=function(x,y,z)return {X=x,Y=y,Z=z}end}
local Color3={fromRGB=function(r,g,b)return {r,g,b}end}
local CFrame={new=function(...)return {...}end}
local Enum={CreatorType={User='User',Group='Group'}}
local script={Parent={WaitForChild=function(_,name)return name end}}
local config
local require=function(name)
 if name=='Healing' then return Healing elseif name=='VoiceCombat' then return Combat elseif name=='Progression' then return Progression
 elseif name=='Config' then return config elseif name=='Lease' then return Lease end
 error('Unexpected dependency '..tostring(name))
end
local function loadConfig()
"""
between=r"""
end
config=loadConfig();local Config=config
local studio=false
local RunService={IsStudio=function()return studio end}
local services={DataStoreService={GetDataStore=function()error('Live stores forbidden in developer tools test')end},
 ReplicatedStorage={Shared={Config='Config',ProfileLease='Lease'}},RunService=RunService,HttpService={GenerateGUID=function()return 'dev-fixture' end}}
local game={JobId='dev-fixture',GetService=function(_,name)return services[name]end,CreatorType=Enum.CreatorType.User,CreatorId=11499795799}
local warn=function()end
local function loadProfiles()
"""
helpers=r"""
end
local Profiles=loadProfiles()
local Access=(function()
"""
setup=r"""
end)()
local owner={UserId=11499795799,SetAttribute=function()end};local ordinary={UserId=1234,SetAttribute=function()end}
local VoiceCombat=Combat;local function cancelSustained()end
local sessions={};local busy=false;local notices=0;local healthSync=0;local entitlementWrites=0;local movement=false
local Commerce={Busy=function()return busy end}
local function state()notices+=1 end
local function parts()return nil,nil,{Health=100,MaxHealth=100}end
local World={SafeSpawn={},Bots={}}
local function syncHealth()healthSync+=1 end
local function protect()error('Unexpected teleport')end
local function stopQuest()error('Unexpected quest reset')end
local function restoreBot()error('Unexpected bot reset')end
local function xp(p,n)sessions[p].data.xp+=n end
local Entitlements={SetStudioMovement=function(_,enabled)movement=enabled;entitlementWrites+=1 end,HasStudioMovement=function()return movement end}
local function fresh(p,level,xpValue)
 sessions[p]={voice=Combat.New(),data=Profiles.Sanitize({schemaVersion=4,level=level,xp=xpValue or 17,sound='TinyAah',aura='Gold',coins=123,
 amplifierOwned=true,amplifierEquipped=true,customColor='FA4FFF',useCustomColor=true,settings={volume=.4,reducedShake=true},
 achievements={FirstBeam=true},availableQuests={garden=true},quests={garden={progress=1,claimed=false}}})}
 return sessions[p]
end
local n=0;local function check(ok,msg)assert(ok,msg);n+=1 end
"""
checks=r"""
-- Actual access module, including nil players and boolean-only Studio admission.
check(not Access.IsAuthorized(nil,Enum.CreatorType.User,Access.OwnerUserId,false),'Nil live player authorized')
check(not Access.IsAuthorized(nil,Enum.CreatorType.User,Access.OwnerUserId,true),'Nil Studio player authorized')
check(Access.IsAuthorized(owner,Enum.CreatorType.User,Access.OwnerUserId,false),'Owner denied own user experience')
check(not Access.IsAuthorized(ordinary,Enum.CreatorType.User,Access.OwnerUserId,false),'Ordinary live player authorized')
check(not Access.IsAuthorized(owner,Enum.CreatorType.User,99,false),'Mismatched owner experience authorized')
check(not Access.IsAuthorized(owner,Enum.CreatorType.Group,Access.OwnerUserId,false),'Group experience authorized by user ID')
check(Access.IsAuthorized(ordinary,Enum.CreatorType.Group,99,true),'Studio ordinary player denied')
check(not Access.IsAuthorized(ordinary,Enum.CreatorType.User,Access.OwnerUserId,'true'),'Truthy nonboolean Studio flag authorized')
check(not Access.IsAuthorized(ordinary,Enum.CreatorType.User,Access.OwnerUserId),'Missing Studio flag opened access')
-- Actual state payload expression agrees with actual command enforcement.
for _,context in ipairs({{ordinary,false,Enum.CreatorType.User,11499795799,false},{owner,false,Enum.CreatorType.User,11499795799,true},
 {owner,false,Enum.CreatorType.Group,11499795799,false},{owner,false,Enum.CreatorType.User,99,false},{ordinary,true,Enum.CreatorType.Group,99,true}}) do
 local p=context[1];studio=context[2];game.CreatorType=context[3];game.CreatorId=context[4]
 check(visible(p)==context[5],'Replicated tool visibility disagrees with access')
 local s=fresh(p,1);dev(p,'AddLevels')
 check(s.data.level==(context[5] and 11 or 1),'Command entrypoint access or +10 failed')
 check((s.testBaseline~=nil)==context[5],'Denied command froze legitimate profile')
end
studio=false;game.CreatorType=Enum.CreatorType.User;game.CreatorId=Access.OwnerUserId
local s=fresh(owner,1);busy=true;dev(owner,'AddLevels');busy=false
check(s.data.level==1 and s.testBaseline==nil,'Busy purchase allowed test mutation')
for _,command in ipairs({false,1,{},'', 'AddLevels 100','addlevels','Unknown'}) do
 s=fresh(owner,1);dev(owner,command);check(s.data.level==1 and s.testBaseline==nil,'Malformed command changed profile')
end
s=fresh(owner,1);dev(owner,nil);check(s.data.level==1 and s.testBaseline==nil,'Nil command changed profile')
sessions[owner]=nil;dev(owner,'AddLevels');check(sessions[owner]==nil,'Missing session recreated')
-- Fixed +10 boundaries; no arbitrary level argument, no XP grants/style switching.
for _,level in ipairs({1,79,80,89,90,91,99,100}) do
 s=fresh(owner,level);local before=s.data
 dev(owner,'AddLevels',999)
 local expected=math.min(100,level+10)
 check(s.data.level==expected,'AddLevels did not add exactly ten with cap')
 check(s.data.xp==(expected==100 and 0 or 17),'AddLevels changed existing XP below cap')
 check(s.testBaseline.level==level,'Baseline captured after mutation')
 check(s.data.sound=='TinyAah' and s.data.aura=='Gold' and s.data.customColor=='FA4FFF' and s.data.useCustomColor,'Style changed with test level')
 check(s.data.amplifierOwned and s.data.amplifierEquipped and s.data.coins==123 and entitlementWrites==0,'Entitlement or coins changed')
 check(s.data~=before and s.testBaseline~=before and s.testBaseline~=s.data,'Baseline or test data aliases original')
 check(s.data.quests~=s.testBaseline.quests and s.data.quests.garden~=s.testBaseline.quests.garden and s.data.settings~=s.testBaseline.settings,'Nested baseline aliases test data')
end
s=fresh(owner,1);dev(owner,'AddLevels');local baseline=s.testBaseline
s.data.quests.garden.progress=7;s.data.settings.volume=.9;s.data.achievements.FirstBeam=false
for i=1,12 do dev(owner,'AddLevels') end
check(s.data.level==100 and s.data.xp==0,'Repeated tool exceeded cap')
check(s.testBaseline==baseline and baseline.level==1 and baseline.xp==17,'Repeat test recaptured modified baseline')
check(baseline.quests.garden.progress==1 and baseline.settings.volume==.4 and baseline.achievements.FirstBeam,'Nested legitimate baseline changed')
check(entitlementWrites==0 and healthSync>0,'Level tool modified movement entitlement or skipped health sync')
print('PASS '..n..' actual developer access/command/sanitizer assertions; mocked engine, no native or real save validation')
"""
def assemble(access_source=access,dev_source=dev):
 return preamble+config+between+profiles+helpers+access_source+setup+'\nAccess.PrelaunchAllTesters=false -- retained owner-only policy matrix; enabled policy covered separately\n'+dev_source+'\nlocal function visible(p)return '+visibility+' end\n'
def run(code,expected=None):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',encoding='utf-8',delete=False) as f:
  path=Path(f.name);f.write(code)
 try:
  r=subprocess.run(['luau',str(path)],cwd=root,capture_output=True,text=True,encoding='utf-8');out=r.stdout+r.stderr
  if expected:
   assert r.returncode and expected in out,out
   print('PASS expected failure:',expected)
  else:
   print(out,end='');assert r.returncode==0,out
 finally:path.unlink()
if args.baseline:
 run(assemble()+"local s=fresh(owner,1);dev(owner,'AddLevels');check(s.data.level==11,'Missing +10 command')",'Missing +10 command')
 run(assemble()+"check(not Access.IsAuthorized(ordinary,Enum.CreatorType.User,Access.OwnerUserId,false),'Public live tools exposed')",'Public live tools exposed')
else:
 run(assemble()+checks)
 # Verify all actual persistence call sites still select the frozen baseline, not test state.
 saves=[line for line in server.splitlines() if 'pcall(Profiles.Save,p.UserId,' in line]
 assert len(saves)==4 and sum('s.testBaseline or s.data' in line for line in saves)==3,saves
 late=server[server.index(' if closing or not p.Parent then',server.index('local function joined(p)')):server.index(' local s={data=data',server.index('local function joined(p)'))]
 assert 'pcall(Profiles.Save,p.UserId,data,true)' in late and 'return' in late,'Unexpected raw-data save outside pre-session late-load release'
 assert 'devAccess=Access.IsAuthorized(p,game.CreatorType,game.CreatorId,RunService:IsStudio(),game.GameId)' in server,'Visibility omitted server Studio/universe context'
 assert server.count('Access.IsAuthorized(p,game.CreatorType,game.CreatorId,RunService:IsStudio(),game.GameId)')==2,'Visibility/command must both use server universe'
 print('PASS three persistence call-site baseline selections and server-side visibility wiring (source checks only)')
 if args.negative_controls:
  bad_access=re.sub(r'function Access.IsAuthorized\(.*?\nend', 'function Access.IsAuthorized(player,creatorType,creatorId,isStudio)\n return player~=nil\nend',access,flags=re.S)
  assert bad_access!=access
  run(assemble(bad_access)+checks,'Ordinary live player authorized')
  uncapped=dev.replace('math.min(Config.MaxLevel,s.data.level+10)','s.data.level+10')
  assert uncapped!=dev,'Cap mutation did not match source'
  run(assemble(dev_source=uncapped)+checks,'AddLevels did not add exactly ten with cap')
  recaptured=dev.replace('if not s.testBaseline then','if true then')
  assert recaptured!=dev
  run(assemble(dev_source=recaptured)+checks,'Repeat test recaptured modified baseline')
  aliased=dev.replace('s.testBaseline=Profiles.Sanitize(s.data)','s.testBaseline=s.data')
  assert aliased!=dev
  run(assemble(dev_source=aliased)+checks,'Baseline or test data aliases original')
