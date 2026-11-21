"""Execute cosmetic renderer with instance/frame doubles; no native rendering claim."""
from pathlib import Path
import subprocess,tempfile
R=Path(__file__).resolve().parents[1]
module=(R/'src/StarterPlayer/StarterPlayerScripts/BossAttackEffects.luau').read_text()
pre='''
local count=0
local function check(v)assert(v);count+=1 end
local mt={};mt.__index=mt
local function v(x,y,z)return setmetatable({X=x or 0,Y=y or 0,Z=z or 0},mt)end
mt.__mul=function(a,b)return v(a.X*b,a.Y*b,a.Z*b)end
mt.__add=function(a,b)return v(a.X+b.X,a.Y+b.Y,a.Z+b.Z)end
local Vector3={new=v,zero=v()}
local fm={};fm.__index=fm
local function frame(a,b,c)return setmetatable({Position=type(a)=='table' and a or v(a,b,c)},fm)end
fm.__mul=function(a,b)return frame(a.Position+b.Position)end
fm.__add=function(a,b)return frame(a.Position+b)end
local CFrame={new=frame,Angles=function()return frame()end}
local Color3={fromRGB=function(r,g,b)return {r,g,b}end}
local Enum={Material={Neon='Neon',Slate='Slate'}}
local Instance={new=function(kind)
 local t={kind=kind};function t:Destroy()self.destroyed=true end;return t
end}
local Effects=(function()
'''
post='''
end)()
for _,id in ipairs({'metronome','golem','ignis','leviathan','conductor'})do
 for _,impact in ipairs({false,true})do
  local markers={};for i=1,16 do table.insert(markers,{position=v(i,32,0)})end
  local e=Effects.Build({},id,markers,impact)
  check(#e.pieces==24)
  for _,p in ipairs(e.pieces)do
   check(p.part.Anchored and not p.part.CanCollide and not p.part.CanTouch and not p.part.CanQuery and not p.part.CastShadow)
   check(p.part.Size.X>0 and p.part.Size.Y>0 and p.part.Size.Z>0)
  end
  e:Step(.2);for _,p in ipairs(e.pieces)do check(p.part.Transparency>=.25 and p.part.Transparency<=1)end
  e:Step(Effects.Lifetime);if impact then check(e.pieces[1].part.Transparency==1)end
  local folder=e.folder;e:Destroy();check(folder.destroyed and #e.pieces==0)
 end
end
local broad=Effects.Build({},'leviathan',{{position=v(),size=v(24,.12,5)}},false)
local siren=Effects.Build({},'leviathan',{{position=v(),size=v(4,.12,24)},{position=v(),size=v(4,.12,24)}},false)
check(#broad.pieces==4 and #siren.pieces==24)
check(broad.pieces[1].part.Size.X==1.5 and siren.pieces[1].part.Size.Y==1.1)
check(siren.pieces[1].part.Color[1]==100 and siren.pieces[1].part.Color[2]==225)
broad:Destroy();siren:Destroy()
print('PASS '..count..' actual VFX budget/physics/fade/cleanup assertions (doubles)')
'''
with tempfile.NamedTemporaryFile('w',dir=R/'tests',suffix='.luau',delete=False) as f:
 f.write(pre+module+post);p=Path(f.name)
try:subprocess.run(['luau',str(p)],check=True,cwd=R)
finally:p.unlink()
client=(R/'src/StarterPlayer/StarterPlayerScripts/BossAttackAccents.client.luau').read_text()
for contract in ['count<5','Effects.Distance','not reduced()','impact==serial','now-at<=Effects.Lifetime','elseif s.mode=="warning" and not warning','s.serial~=serial','not seen[model]','connection:Disconnect()']:
 assert contract in client,contract
service=(R/'src/ServerScriptService/BossService.luau').read_text()
impact=service.index('SetAttribute("BossAttackImpactSerial"')
assert service.rfind('if now>=b.strike.at then',0,impact)>service.rfind('if #targets==0',0,impact)
assert service.count('SetAttribute("BossAttackImpactSerial"')==1
assert service.index('warning:SetAttribute("BossMarkerCount",#strike.shapes)')<service.index('marker.CFrame=')<service.index('warning.Parent=b.model')
print('PASS visibility/reduced/cancel/stale/teardown and server-only impact source contracts')
pre2='''
local n=0;local function check(v)assert(v);n+=1 end
local now=0;local callback;local destroy;local built=0;local cleared=0;local lastMarkerCount
local delta={Magnitude=10,X=10,Y=-10,Z=0}
local pos=setmetatable({},{__sub=function()return delta end})
local FX={Distance=140,Lifetime=.45,Build=function(_,id,markers,impact)
 built+=1;lastMarkerCount=#markers;return {Destroy=function()cleared+=1 end,Step=function()end}
end}
local attrs={BossReducedEffects=false}
local player={Character={FindFirstChild=function()return {Position=pos}end},GetAttribute=function(_,k)return attrs[k]end,
 SetAttribute=function(_,k,v)attrs[k]=v end}
local Enum={PartType={Cylinder='Cylinder'}}
local marker={Name='Hazard',Position=pos,IsA=function(_,class)return class=='Part' end}
local a={BossAttackSerial=1,BossState='Windup',BossAttackAt=2}
local children={marker, marker}
local expected,warningSerial,hint=2,1,nil
local function newWarning()
 return {GetChildren=function()return children end,GetAttribute=function(_,key)
  if key=='BossMarkerCount' then return expected end
  if key=='BossAttackSerial' then return warningSerial end
  if key=='BossAttackHint' then return hint end
 end}
end
local warning=newWarning()
local model={Name='metronome',GetAttribute=function(_,k)return a[k]end,FindFirstChild=function(_,k)if k=='Core'then return {Position=pos} elseif k=='DodgeWarning'then return warning end end}
local bosses={GetChildren=function()return {model}end,FindFirstChild=function(_,name)if model.Name==name then return model end end}
local world={FindFirstChild=function()return bosses end}
local workspace={GetServerTimeNow=function()return now end,FindFirstChild=function()return world end}
local disconnected=false
local Run={Heartbeat={Connect=function(_,fn)callback=fn;return {Disconnect=function()disconnected=true end}end}}
local Gui={ReducedMotionEnabled=false}
local game={GetService=function(_,name)if name=='Players'then return {LocalPlayer=player} elseif name=='RunService'then return Run else return Gui end end}
local script={Parent={WaitForChild=function()return {}end},Destroying={Connect=function(_,fn)destroy=fn end}}
local require=function()return FX end
'''
post2='''
a.BossState='Recovery';callback(.05);check(built==0)
a.BossState='Windup';a.BossAttackAt=-1;callback(.05);check(built==0)
a.BossAttackAt=2;a.BossAttackImpactSerial=1;callback(.05);check(built==0)
a.BossAttackImpactSerial=nil;children={marker};callback(.05);check(built==0 and cleared==0)
children={marker,marker};warningSerial=0;callback(.05);check(built==0)
warningSerial=1;children={marker,{Name='Other',IsA=function()return false end}}
callback(.05);check(built==0)
children={marker,marker};callback(.05);check(built==1 and cleared==0 and lastMarkerCount==2)
callback(.05);check(built==1)
warning=nil;callback(.05);check(cleared==1 and built==1)
warning=newWarning();warningSerial=2;a.BossAttackSerial=2;callback(.05);check(built==2)
a.BossAttackImpactSerial=2;a.BossAttackImpactAt=0;warning=nil;callback(.05);check(built==3 and cleared==2 and lastMarkerCount==2)
now=1;callback(.05);check(cleared==3)
warning=newWarning();warningSerial=3;a.BossAttackSerial=3;callback(.05);check(built==4)
attrs.BossReducedEffects=true;callback(.05);check(cleared==4)
attrs.BossReducedEffects=false;callback(.05);check(built==5)
player.Character=nil;callback(.05);check(cleared==5)
player.Character={FindFirstChild=function()return {Position=pos}end};callback(.05);check(built==6)
a.BossAttackAt=now;warning=nil;callback(.05);check(cleared==6 and built==6)
a.BossAttackImpactSerial=3;a.BossAttackImpactAt=now;callback(.05);check(built==7 and cleared==6)
now+=1;callback(.05);check(cleared==7)
warning=newWarning();warningSerial=4;a.BossAttackSerial=4;a.BossAttackAt=now+2;callback(.05);check(built==8)
local savedCharacter=player.Character
model.Name='conductor';attrs.BossReducedEffects=true;hint='Step off the circles'
expected=6;callback(.05);check(not attrs.BossCombatHint and cleared==8)
children={marker,marker,marker,marker,marker,marker};warningSerial=3
callback(.05);check(not attrs.BossCombatHint)
warningSerial=4;callback(.05)
check(attrs.BossCombatHint==hint and built==8)
delta.Y=15;callback(.05);check(not attrs.BossCombatHint);delta.Y=-10
delta.X=31;callback(.05);check(not attrs.BossCombatHint);delta.X=10
callback(.05);check(attrs.BossCombatHint==hint)
player.Character=nil;callback(.05);check(not attrs.BossCombatHint);player.Character=savedCharacter
callback(.05);check(attrs.BossCombatHint==hint)
now=a.BossAttackAt;callback(.05);check(not attrs.BossCombatHint)
a.BossAttackAt=now+2;callback(.05);check(attrs.BossCombatHint==hint)
a.BossAttackImpactSerial=4;callback(.05);check(not attrs.BossCombatHint)
local active=warning
a.BossAttackImpactSerial=nil;warning=nil;callback(.05);check(not attrs.BossCombatHint)
warning=active;callback(.05);check(attrs.BossCombatHint==hint)
destroy();check(cleared==8 and disconnected and not attrs.BossCombatHint)
callback(.05);check(built==8)
print('PASS '..n..' actual client warning/impact/cancel/reduced/respawn/teardown checks')
'''
with tempfile.NamedTemporaryFile('w',dir=R/'tests',suffix='.luau',delete=False) as f:
 f.write(pre2+client+post2);p=Path(f.name)
try:subprocess.run(['luau',str(p)],check=True,cwd=R)
finally:p.unlink()
for name,source in [
 ('partial warning admission',pre2+client.replace('if #children==expected then','if #children>0 then').replace('if #markers==expected then','if #markers>0 then')+post2),
 ('stale warning folder',pre2+client.replace('warning:GetAttribute("BossAttackSerial")==serial and ','')+post2),
 ('stale-warning admission',pre2+client.replace('and model:GetAttribute("BossState")=="Windup"','')+post2),
 ('reduced effects hiding the hint',pre2+client.replace(' updateHint(player,root,bosses,now)',' if not reduced() then updateHint(player,root,bosses,now) end')+post2),
 ('captain siren motif',pre+module.replace('and width<length then','and false then')+post),
]:
 with tempfile.NamedTemporaryFile('w',dir=R/'tests',suffix='.luau',delete=False) as f:
  f.write(source);p=Path(f.name)
 try:
  result=subprocess.run(['luau',str(p)],cwd=R,capture_output=True,text=True)
  assert result.returncode!=0,'Negative control survived: '+name
 finally:p.unlink()
 print('PASS negative control:',name)
