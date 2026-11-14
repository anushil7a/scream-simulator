"""Actual controller with synthetic Instances, projections and raycasts; no native/input claim."""
from pathlib import Path
import subprocess,tempfile,argparse
R=Path(__file__).resolve().parents[1]
source=(R/'src/StarterPlayer/StarterPlayerScripts/LockOn.luau').read_text()
SETUP=r"""
local V={};V.__index=function(t,k)if k=='Magnitude'then return math.sqrt(t.X*t.X+t.Y*t.Y+t.Z*t.Z)end;return V[k]end
V.__sub=function(a,b)return setmetatable({X=a.X-b.X,Y=a.Y-b.Y,Z=a.Z-b.Z,_type='Vector3'},V)end
local function v(x,y,z)return setmetatable({X=x,Y=y,Z=z,_type='Vector3'},V)end
local function typeof(t)return type(t)=='table' and t._type or type(t)end
local Enum={RaycastFilterType={Exclude='Exclude'}}
local RaycastParams={new=function()return {}end}
local n=0;local function check(x,m)assert(x,m);n+=1 end
local function obj(class)
 local t={_type='Instance',class=class,Parent=true,attrs={}}
 function t:IsA(c)return c==self.class or c=='BasePart' and self.class=='Part'end
 function t:IsDescendantOf(w)return self.Parent~=nil and not self.detached end
 function t:GetAttribute(k)return self.attrs[k]end
 function t:FindFirstChild(k)return self[k]end
 function t:FindFirstChildOfClass(k)return self[k]end
 return t
end
local function model(x)
 local m=obj('Model');m.HumanoidRootPart=obj('Part');m.HumanoidRootPart.Position=v(x,0,10)
 m.Humanoid=obj('Humanoid');m.Humanoid.Health=100;return m
end
"""
CHECKS=r"""
local function fixture()
 local me=obj('Player');me.Character=model(0)
 local enemy=obj('Player');enemy.Character=model(2)
 local npc=model(1);npc.attrs.TrainingTier='rookie';npc.attrs.ResidentActive=true
 local harmless=model(0)
 local players={list={me,enemy}}
 function players:GetPlayers()return self.list end
 function players:GetPlayerFromCharacter(m)for _,p in ipairs(self.list)do if p.Character==m then return p end end end
 local collection={list={npc,harmless}}
 function collection:GetTagged()return self.list end
 function collection:HasTag(m)return table.find(self.list,m)~=nil end
 local rays=0;local world={}
 function world:Raycast(origin,delta,params)
  rays+=1;check(params.RespectCanCollide and #params.FilterDescendantsInstances==2,'LOS query contract')
  if self.cover or (self.cameraCover and origin.X==99)then return {}end
 end
 local camera=obj('Camera');camera.ViewportSize={X=640,Y=360};camera.CFrame={Position=v(99,3,0)}
 function camera:WorldToViewportPoint(pos)return v(320+pos.X*10,180,10),not self.hidden end
 local c={allowed=true,character=me.Character,origin=v(0,2,0),position=v(0,0,0),range=30,now=10,camera=camera}
 local o={world=world,localPlayer=me,players=players,collection=collection,trainingHomes={rookie=v(0,0,0)},trainingRadius=32,inArena=function(pos)return pos.X>=0 end}
 return LockOn.new(o),c,o,npc,enemy,harmless
end
local lock,c,o,npc,enemy,harmless=fixture()
check(lock:Toggle(c)==npc,'Nearest valid trainer not selected')
local point,target=lock:Resolve(c);check(target==npc and point==npc.HumanoidRootPart.Position,'Resolved aim not exact target')
check(lock:Toggle(c)==nil and lock.target==nil,'Explicit unlock failed')
o.collection.list={harmless};check(lock:Toggle(c)==enemy.Character,'Eligible player not selected')
lock:Clear();o.players.list={o.localPlayer};check(lock:Toggle(c)==nil,'Harmless resident acquired')
for _,case in ipairs({'cover','cameraCover','dead','removed','detachedRoot','detachedHumanoid','replacedRoot','replacedHumanoid','respawn','range','home','inactive','tier','untagged','focus','menu','off','destroy','offscreen'})do
 local l,x,a,m,e=fixture();check(l:Toggle(x)==m,'Setup lock failed')
 if case=='cover'then a.world.cover=true elseif case=='cameraCover'then a.world.cameraCover=true
 elseif case=='dead'then m.Humanoid.Health=0 elseif case=='removed'then m.Parent=nil
 elseif case=='detachedRoot'then m.HumanoidRootPart.Parent=nil
 elseif case=='detachedHumanoid'then m.Humanoid.Parent=nil
 elseif case=='replacedRoot'then m.HumanoidRootPart=obj('Part');m.HumanoidRootPart.Position=v(1,0,10)
 elseif case=='replacedHumanoid'then m.Humanoid=obj('Humanoid');m.Humanoid.Health=100
 elseif case=='respawn'then x.character=model(0);a.localPlayer.Character=x.character
 elseif case=='range'then x.range=1 elseif case=='home'then a.trainingHomes.rookie=v(100,0,0)
 elseif case=='inactive'then m.attrs.ResidentActive=false elseif case=='tier'then m.attrs.TrainingTier='not-a-tier'
 elseif case=='untagged'then a.collection.list={}
 elseif case=='destroy'then l:Destroy() elseif case=='offscreen'then x.camera.hidden=true else x.allowed=false end
 check(l:Resolve(x)==nil and l.target==nil,'Invalid target retained: '..case)
 x.allowed=true;a.world.cover=false;a.world.cameraCover=false
 check(l:Resolve(x)==nil,'Automatic retarget: '..case)
end
for _,case in ipairs({'safeSelf','safeTarget','protected','dodging','playerGone','playerRespawn','advisory','malformedProtection'})do
 local l,x,a,m,e=fixture();a.collection.list={};check(l:Toggle(x)==e.Character,'Player setup')
 if case=='safeSelf'then x.position=v(-1,0,0) elseif case=='safeTarget'then e.Character.HumanoidRootPart.Position=v(-1,0,10)
 elseif case=='protected'then e.attrs.ProtectionEnds=11 elseif case=='dodging'then e.attrs.DodgeEnds=11
 elseif case=='playerGone'then e.Parent=nil elseif case=='playerRespawn'then e.Character=model(2)
 elseif case=='advisory'then a.canSelect=function()return false end else e.attrs.ProtectionEnds='bad'end
 check(l:Resolve(x)==nil,'Invalid PvP target retained: '..case)
end
for _,bad in ipairs({0,-1,0/0,math.huge,'30'})do local l,x=fixture();x.range=bad;check(l:Toggle(x)==nil,'Malformed range admitted')end
local l,x,a,m,e=fixture();a.players.list={a.localPlayer};m.Humanoid.Health=0/0;check(l:Toggle(x)==nil,'NaN health admitted')
l,x,a,m,e=fixture();a.collection.list={nil};a.players.list={a.localPlayer,{Character=false}};check(l:Toggle(x)==nil,'Malformed candidate admitted')
l,x,a,m,e=fixture();a.collection.list={};e.attrs.ProtectionEnds=10;e.attrs.DodgeEnds=10;check(l:Toggle(x)==e.Character,'Expired protection rejected')
l:Destroy();l:Destroy();check(l:Toggle(x)==nil and l:Resolve(x)==nil,'Destroyed controller resurrected')
l,x,a,m,e=fixture();check(l:Toggle(x)==m,'Setup repeated resolution');for i=1,120 do x.now+=100;check(l:Resolve(x)~=nil,'Valid current aim lost')end
check(l.target.model==m,'Repeated resolution retargeted')
print('PASS '..n..' lock-on assertions; mocked Instances/LOS/projection, no native or server hit claim')
"""
def run(s):
 code=SETUP+'\nlocal LockOn=(function()\n'+s+'\nend)()\n'+CHECKS
 with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=R/'tests',delete=False,encoding='utf8')as f:f.write(code);p=Path(f.name)
 try:return subprocess.run(['luau',str(p)],capture_output=True,text=True,timeout=15)
 finally:p.unlink()
def main():
 args=argparse.ArgumentParser();args.add_argument('--negative-controls',action='store_true');a=args.parse_args()
 r=run(source);print(r.stdout,end='');assert r.returncode==0,r.stderr
 if a.negative_controls:
  mutations=[('or o.world:Raycast(origin,root.Position-origin,params)','or false','Invalid target retained: cover'),('prior.root~=root','false','Invalid target retained: replacedRoot'),('or not o.inArena(c.position)','or false','Invalid PvP target retained: safeSelf'),('(c.position-home).Magnitude>o.trainingRadius','false','Invalid target retained: home'),('untilTime>c.now','false','Invalid PvP target retained: protected'),('if self.target then self:Clear();return nil end','if false then self:Clear();return nil end','Explicit unlock failed')]
  for old,new,expected in mutations:
   assert old in source
   r=run(source.replace(old,new,1));assert r.returncode and expected in r.stderr,(old,r.stdout,r.stderr)
  print('PASS '+str(len(mutations))+' negative controls')
if __name__=='__main__':main()
